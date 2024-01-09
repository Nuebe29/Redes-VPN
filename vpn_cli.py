from utils import assign_ip_address
from vpn_service import VPN

vpn = VPN()

# Esta función hace el rol de interfaz en consola para los metodos del VPN

def main():
    while True:
        command = input("CDL-VPN >").split()

        if command[0] == 'start':
            print("Iniciando VPN...")
            vpn.start()
        elif command[0] == 'stop':
            print("Deteniendo VPN...")
            vpn.stop()
        elif command[0] == 'create_user':
            vpn.create_user(command[1], command[2], command[3])
        elif command[0] == 'restricte_vlan':
            vpn.restrict_vlan(command[1])
        elif command[0] == 'restrict_user':
            vpn.restrict_user(command[1])
        elif command[0] == 'logs':
            while not vpn.log_queue.empty():
                print(vpn.log_queue.get())
        else:
            print("Comando desconocido")


if __name__ == "__main__":
    main()
