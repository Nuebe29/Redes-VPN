import random

from utils import create_checksum
import socket
import struct


# Dirección y puerto del servidor
TARGET_ADDRESS = "127.0.0.1"
VPN_PORT = 8050

# Socket con el que se comunicará el cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)


# Dirección y puertos del cliente
SOURCE_ADDRESS = "127.0.0.1"
SOURCE_PORT = 3000

# Puerto del servidor real al que queremos acceder
TARGET_SERVER_PORT = 7000

# Mensajes de prueba a enviar al servidor
messages = ["Hola", "Mundo", "!", "Al", "Habla", SOURCE_ADDRESS, ":", str(SOURCE_PORT)]

# Usuario y contraseña de este cliente en el VPN
USERNAME = "test"
PASSWORD = "test"

for i in range(len(messages)):
    # Formateando el mensaje
    messages[i] = USERNAME + "%" + PASSWORD + "%" + messages[i]

    message = messages[i].encode()
    
    # Empezamos a crear los datos que contendrá el paquete
    contents = struct.pack(">H", TARGET_SERVER_PORT) + message

    # Creando cabezal udp
    header = struct.pack("!HHHH", SOURCE_PORT, VPN_PORT, 8 + len(contents), 0)

    # Calculamos el checksum del paquete
    checksum = create_checksum(SOURCE_ADDRESS, TARGET_ADDRESS, header + contents)
 
    # Simlando corrupción de paquetes
    if random.randint(1, 5) == 1:
        checksum_to_send = 1
    else:
        checksum_to_send = checksum

    # Empaquetado del header con el checksum, y concatenado con los datos para crear el paquete final
    header = struct.pack("!HHHH", SOURCE_PORT, VPN_PORT, 8 + len(contents), checksum_to_send)
    packet = header + contents
    
    client_socket.sendto(packet, (TARGET_ADDRESS, VPN_PORT))
    print(f"Enviado mensaje #{i} al VPN en {TARGET_ADDRESS}:{VPN_PORT} con servidor final {TARGET_SERVER_PORT}")
    
client_socket.close()