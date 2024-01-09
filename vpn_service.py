import os
import queue
import socket
import struct
import json
import threading
import time

from utils import create_checksum, assign_ip_address

class VPN:
    def __init__(self):
        self.running = False
        self.VPN_ADDRESS = "127.0.0.1"
        self.VPN_PORT = 8050
        self.vpn_socket = None
        self.log_queue = queue.Queue()

        # Cargamos datos de usuarios, asi como los usuarios y VLANS restringidos de un archivo para asegurar persistencia
        
        try:
            with open('users.json', 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}

        try:
            with open('restricted_users.json', 'r') as f:
                self.restricted_users = set(json.load(f))
        except FileNotFoundError:
            self.restricted_users = set()

        try:
            with open('restricted_vlans.json', 'r') as f:
                self.restricted_vlans = set(json.load(f))
        except FileNotFoundError:
            self.restricted_vlans = set()
                

    def start(self):
        if self.running:
            print("VPN is already running.")
            return
        
        self.vpn_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        self.vpn_socket.bind(('localhost', self.VPN_PORT))

        # Se corre la función de procesamiento de paquetes en un hilo distinto
        # para que se pueda seguir usando la consola
        thread = threading.Thread(target=self.run)
        thread.start()
        
        self.running = True

        print(f"VPN started on {self.VPN_ADDRESS}:{self.VPN_PORT}")
        

    def stop(self):
        if self.running:
            self.vpn_socket.close()
            self.vpn_socket = None
            self.running = False
            

    def create_user(self, username, password, vlan_id):
        # Se asigna una IP y puerto virtual al usuario
        ip_address, port = assign_ip_address()
        self.users[username] = {'password': password, 'vlan_id': vlan_id, 'ip_address': ip_address, 'port': port}
        with open('users.json', 'w') as f:
            json.dump(self.users, f)

        self.log_message(f"Creado usuario {username} con dirección virtual {ip_address}:{port} en la VLAN {vlan_id}")
        

    def restrict_user(self, port):
        self.restricted_users.add(port)
        with open('restricted_users.json', 'w') as f:
            json.dump(list(self.restricted_users), f)
            

    def restrict_vlan(self, vlan_id):
        self.restricted_vlans.add(vlan_id)
        with open('restricted_vlans.json', 'w') as f:
            json.dump(list(self.restricted_vlans), f)
            

    def validate_user(self, sender_addr, sender_port, username, password):
        user_data = self.users.get(username)
        if user_data is None:
            self.log_message(f"Ignorando paquete de usuario no registrado en: {sender_addr}:{sender_port}")
            return None

        if user_data['password'] != password:
            self.log_message(f"Error de autenticación de usuario en: {sender_addr}:{sender_port}")
            return None

        if str(sender_port) in self.restricted_users:
            self.log_message(f"Ignorando paquete de usuario restringido en puerto: {sender_port}")
            return None

        vlan = str(user_data['vlan_id']) 
        if vlan in self.restricted_vlans:
            self.log_message(f"Ignorando paquete de VLAN restringida: {vlan}")
            return None

        return user_data
    

    def log_message(self, message):
        self.log_queue.put(message)

        with open('logs.txt', 'a') as f:
            f.write(message + '\n')
            

    def run(self):
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        while True:
            try:
                # Esperando datos en un buffer de tamaño 2^16
                data, addr = self.vpn_socket.recvfrom(2**16)

                # Desempaquetando cabezal UDP
                udp_header = data[20:28]
                udp_data = struct.unpack('!HHHH', udp_header)

                source_port = udp_data[0]
                dest_port = udp_data[1]
                length = udp_data[2]
                sender_addr, sender_port = addr

                if dest_port != self.VPN_PORT:
                    # Paquete enviado a otro puerto, ignorando
                    continue
                
                try:
                    username, password, message = data[30:].decode().split('%')
                except:
                    # No se pudieron extraer los datos, no era un paquete valido
                    continue
                
                # Comprobamos si el usuario está registrado y no esta restringido
                user = self.validate_user(sender_addr, source_port, username, password)
                if user is None:
                    continue

                # Calculamos y comprobamos el checksum
                received_checksum = udp_data[3]

                zero_checksum_header = udp_header[:6] + b'\x00\x00' + udp_header[8:]
                calculated_checksum = create_checksum(sender_addr, self.VPN_ADDRESS, zero_checksum_header + data[28:])

                if received_checksum != calculated_checksum:
                    self.log_message("Checksum inválido, ignorando paquete corrupto.")
                    continue

                # Extraemos puerto de destinación
                forward_port = struct.unpack('!H', data[28:30])[0]

                message = user['ip_address'] + "%" + str(user['port']) + "%" + message
                new_data = struct.pack(">H", forward_port) + message.encode()

                # Generamos un nuevo cabezal enmascarando el cliente original
                new_source_port = self.VPN_PORT
                new_udp_header = struct.pack("!HHHH", new_source_port, forward_port, 8 + len(new_data), 0)

                new_udp_checksum = create_checksum(self.VPN_ADDRESS, self.VPN_ADDRESS, new_udp_header + new_data)
                new_udp_header = struct.pack("!HHHH", new_source_port, forward_port, 8 + len(new_data), new_udp_checksum)
                
                # Creamos el nuevo paquete y lo enviamos al servidor
                forwarded_packet = new_udp_header + new_data

                send_socket.sendto(forwarded_packet, (self.VPN_ADDRESS, forward_port))

                self.log_message(
                    f"Enviado paquete de {sender_addr}:{source_port} a {self.VPN_ADDRESS}:{forward_port} con dirección enmascarada {user['ip_address']}:{user['port']}")
            except Exception:
                if self.vpn_socket is None:
                    break
                else:
                    raise
