import socket
import threading
import hashlib
import time
import os
from datetime import datetime

def recibirArchivo(socket, numeroConexiones, nombreArchivo, paquetes):
    print("Presione cualquier caracter para inicar la recepción")
    input()
    socket.send(b"")
    print("Iniciando recepción")
    numeroCliente = socket.recv(1024).decode()
    numeroConexiones = socket.recv(1024).decode()
    hash = socket.recv(1024)
    conexion = socket.recv(1024)
    conexiones.append([numeroCliente, conexion])
    nombreArchivo = f"Cliente{numeroCliente}-Prueba-{numeroConexiones}.test"
    archivo = open(nombreArchivo)
    recepcionInicio = time.time()
    recepcionPaquete = socket.recv(65536)
    while True:
        archivo.write(recepcionPaquete)
        recepcionPaquete = socket.recv(65536)
        paquetes += 1
        if "Archivo Enviado" in str(recepcionPaquete):
            break
    recepcionFin = time.time()
    archivo.write(recepcionPaquete[:-3])
    tiempoRecepcion = recepcionFin - recepcionInicio
    print(f"Recepcion Finalizada. Tiempo de transmision: {tiempoRecepcion} ms")
    tiempos.append([numeroCliente, tiempoRecepcion])
    archivo.close()
    hashUsed = hashlib.sha256()
    archivoValidate = open(f"Cliente{numeroCliente}-Prueba-{numeroConexiones}.test")
    hashUsed.update(archivoValidate.read())
    if hashUsed.digest() == hash:
        print("Validación de integirdad terminada. No hubo corrupción de información")
    else:
        fallas.append("Falla")
        print("Validación de integirdad terminada. Se encontró corrupción de información en el archivo recibido")
    archivoValidate.close()
    # Se crea y se escribe el log
    socket.close()

print("Ingresar un numero de clientes")
numeroClientes = int(input())
conexiones = []
tiempos = []
fallas = []
numeroConexiones = 0
paquetes = 0
nombreArchivo = ""
print("Ingresar la dirección IP del servidor")
ipAdressServer = input()
port = 1234

for i in range(numeroClientes):
    newSocket = socket.socket()
    newSocket.connect(ipAdressServer, port)
    newCliente = threading.Thread(recibirArchivo(newSocket, numeroConexiones, nombreArchivo, paquetes))
    newCliente.start()
    newCliente.join()
date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
archivoLog = open(f"{date}.txt")
archivoLog.write(f"Nombre del archivo: {nombreArchivo}\n")
tamanoArchivo = os.path.getsize(nombreArchivo)
archivoLog.write(f"Tamaño del archivo: {tamanoArchivo} bytes\n")
for i in conexiones:
    archivoLog.write(f"Conexion {i[1]} - Cliente {i[2]}\n")
if len(fallas) == 0:
    archivoLog.write("Entrega exitosa\n")
else:
    archivoLog.write("Entrega no exitosa\n")
for i in tiempos:
    archivoLog.write(f"Tiempos: Cliente {i[0]}: {i[1]}ms\n")
archivoLog.write(f"Paquetes: {paquetes}")
archivoLog.close()