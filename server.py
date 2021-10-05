import socket
import tqdm
import os
import threading
import hashlib
import datetime
from time import time, sleep

BUFFER_SIZE = 4096  # send 4096 bytes each time step
numeroThreadsProcesando = 0
logTransmisiones = {}
logHashes = {}


def hash_file(filename):
    h = hashlib.sha1()
    with open(filename, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    return h.hexdigest()


def enviarArchivo(s, conexion, nConexiones, nArchivo):
    nombreThread = threading.currentThread().getName()
    global numeroThreadsProcesando
    s.recv(1024).decode()
    numeroThreadsProcesando += 1

    while numeroThreadsProcesando < nConexiones:
        ...

    s.send(nombreThread.encode())
    sleep(0.3)

    s.send(str(nConexiones).encode())
    sleep(0.3)

    s.send(hash_file(nArchivo))
    sleep(0.3)

    s.send(conexion.encode())
    sleep(0.3)

    filesize = os.path.getsize(nArchivo)
    progress = tqdm.tqdm(range(
        filesize), f"Sending {nArchivo} to {nombreThread}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(nArchivo, 'rb') as f:
        inicioTransmision = time()
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
            progress.update(len(bytes_read))
    s.send('Archivo Enviado'.encode())
    sleep(0.3)
    logTransmisiones[nombreThread] = time() - inicioTransmision
    logHashes[nombreThread] = s.recv(1024).decode()
    s.close()
    print(f"Archivo enviado al cliente {nombreThread} {conexion}")


nArchivo = input(
    "Ingrese el nombre del archivo a enviar (Ej. 100MB.test): ")
threadsClientes = []
conexionesClientes = {}
numeroClientes = int(input("Ingrese el numero de clientes: "))
host = input("\nIngrese la direccion IP del servidor: ")
s = socket.socket()
port = 5001
print(f"[+] Connecting to {host}:{port}")
s.bind((host, port))
print("[+] Connected.")
for i in range(numeroClientes):
    socketClienteActual, conexion = s.accept()
    print("Conexion de:", conexion)
    t = threading.Thread(name=f"Cliente{i}", target=enviarArchivo, args=(
        socketClienteActual, conexion, numeroClientes, nArchivo))
    threadsClientes.append(t)
    conexionesClientes[f'Cliente{i}'] = conexion
for thread in threadsClientes:
    thread.start()

for thread in threadsClientes:
    thread.join()

fechaStr = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
log = open(f"Logs/{fechaStr}.txt", "w")

log.write(f"Nombre archivo: {nArchivo}\n")
tamanioArchivo = os.path.getsize(nArchivo)
log.write(f"Tamanio archivo: {tamanioArchivo} bytes\n")

log.write("Clientes de transferencia:\n")
for i in range(numeroClientes):
    log.write(f"Cliente {i}: {conexionesClientes[f'Cliente{i}']}\n")

log.write("Resultados comprobacion hash:\n")
for i in range(numeroClientes):
    log.write(f"Cliente {i}: {logHashes[f'Cliente{i}']}\n")
log.write("\n")

log.write("Tiempos transferencias:\n")
for i in range(numeroClientes):
    log.write(f"Cliente {i}: {logTransmisiones[f'Cliente{i}']}ms\n")
log.write("\n")

log.close()
