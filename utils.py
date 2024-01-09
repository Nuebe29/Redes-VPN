import random
import socket
import struct


def create_checksum(source_ipv4, dest_ipv4, packet_contents):
    pseudo_header = struct.pack('!4s4sBBH',
                                socket.inet_aton(source_ipv4),
                                socket.inet_aton(dest_ipv4),
                                0,
                                socket.IPPROTO_UDP,
                                len(packet_contents))
    return calc_checksum(pseudo_header + packet_contents)


def calc_checksum(packet_contents):
    if len(packet_contents) % 2 != 0:
        packet_contents += b'\0'
    res = sum((int.from_bytes(packet_contents[i:i + 2], 'big') for i in range(0, len(packet_contents), 2)))
    res = (res >> 16) + (res & 0xffff)
    res += res >> 16
    return ~res & 0xffff


def assign_ip_address():
    ip_address = f"127.0.0.1"
    port = random.randint(1024, 65535)
    return ip_address, port
