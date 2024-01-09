from utils import create_checksum
import socket
import struct


# Dirección y puerto del servidor
SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 7000

# Creando socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
server_socket.bind(('localhost', SERVER_PORT))

while True:
    # Esperamos datos, y establecemos un buffer de 2^16 bits
    data, addr = server_socket.recvfrom(2**16)

    # Extraemos el cabezal UDP
    udp_header = data[20:28]
    udp_data = struct.unpack('!HHHH', udp_header)

    # Extraemos información del cabezal
    source_port = udp_data[0]
    dest_port = udp_data[1]
    length = udp_data[2]
    checksum = udp_data[3]

    if dest_port != SERVER_PORT:
        continue

    # Calculamos y comprobamos el checksum
    received_checksum = udp_data[3]
    
    try:
        real_source_ip, real_source_port, message = data[30:].decode().split('%')
    except:
        # Paquete no contiene el formato del proyecto, ignorando
        continue

    sender_address, sender_port = addr
    
    # Al header se le quita el checksum y se pone un 0 en su lugar, pues es como se calculó el checksum original
    zero_checksum_header = udp_header[:6] + b'\x00\x00' + udp_header[8:]
    
    calculated_checksum = create_checksum(sender_address, SERVER_ADDRESS, zero_checksum_header + data[28:])

    if received_checksum != calculated_checksum:
        print("Checksum invalido, paquete corrupto, ignorando.")
        continue
    
    # En un servidor real aquí se procesarían los datos recibidos de los clientes
    print("Received valid packet:", message)
