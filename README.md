# Informe del Proyecto de Redes: VPN

## Introducción:

Este proyecto es una implementación sencilla de una VPN (Red Privada Virtual) utilizando Python. Consiste en un cliente, un servidor y una VPN que actúa como intermediario. El cliente envía paquetes en forma de datagramas UDP a la VPN, la cual luego los reenvía al servidor. La VPN también puede restringir ciertos usuarios y VLANs para que no accedan al servidor.

## Archivos:

- test_client.py: Este archivo contiene el código para el cliente que envía paquetes a la VPN.
- test_server.py: Este archivo contiene el código para el servidor que recibe paquetes de la VPN.
- vpn_service.py: Este archivo contiene el código para la VPN que reenvía paquetes del cliente al servidor.
- vpn_cli.py: Este archivo proporciona una interfaz de línea de comandos (CLI) para controlar la VPN.
- utils.py: Este archivo contiene funciones de utilidad para asignar direcciones IP y puertos a los usuarios y calcular sumas de verificación UDP.

## Modulos:

### `test_client.py`

El cliente crea un socket en bruto y envía un paquete UDP a la VPN. El paquete contiene un mensaje y el puerto real de destino. El cliente calcula la suma de comprobación UDP y la incluye en el encabezado UDP.

### `test_server.py`

El servidor crea un socket en bruto y espera paquetes entrantes. Cuando recibe un paquete, desempaqueta el encabezado UDP y verifica la suma de verificación. Si la suma de verificación es válida, procesa el paquete. De lo contrario, descarta el paquete.

### `vpn_service.py`

La VPN crea un socket en bruto y espera paquetes entrantes. Cuando recibe un paquete, valida al usuario y verifica la suma de comprobación. Si el usuario es válido y la suma de comprobación es correcta, reforma el cabezal UDP enmascarando la información del cliente y recalcula la suma de comprobación, entonces reenvía el paquete al servidor. Si el paquete no se verifica que fue enviado por un cliente registrado del VPN o la suma de comprobación no es correcta, se descarta el paquete.

La VPN también puede restringir a ciertos usuarios y VLANs. Los usuarios restringidos se identifican por su puerto, y las VLAN restringidas se identifican por su ID de VLAN.

### `utils.py`

Este módulo contiene tres funciones:

- `assign_ip_address`: Asigna una dirección IP y un puerto aleatorios a un usuario.
- `create_checksum(source_ipv4, dest_ipv4, packet_contents)`: Calcula la suma de verificación UDP para un paquete.
- `calc_checksum(packet)`: Calcula la suma de comprobación para un paquete.

## Modo de Uso:

Para usar este proyecto siga los siguientes pasos:

1. Inicia la VPN ejecutando `vpn_cli.py` e introduciendo el comando start.
2. Crea un usuario ingresando el comando `create_user <username> <password> <vlan_id>`.
3. Ejecuta `test_server.py` para recibir un paquete desde la VPN.
4. Ejecuta `test_client.py` para enviar el paquete a la VPN.

> Dependiendo de los permisos que tenga tu sistema, es posible que necesites ejecutar estos comandos con la palabra clave sudo.

Puedes restringir usuarios y VLANs ingresando los comandos `restrict_user <port>` y `restrict_vlan <vlan_id>` en la CLI de la VPN.

Puedes ver logs generados por la VPN ingresando el comando `logs`.

Para detener la VPN, ingresa el comando `stop` en la CLI de la VPN.

## Dependencias:

Este proyecto requiere Python 3 y las siguientes bibliotecas de Python:

- `socket`
- `struct`
- `random`

## Acerca de UDP:

El Protocolo de Datagramas de Usuario (UDP) es uno de los protocolos fundamentales del conjunto de protocolos de Internet. Es un protocolo simple y sin conexión que no garantiza la entrega, el orden o la comprobación de errores de los datos. Esto significa que UDP no establece una conexión antes de enviar datos, no asegura que los datos sean recibidos y no garantiza que los datos sean recibidos en el mismo orden en que fueron enviados.

A pesar de estas limitaciones, UDP se utiliza en este proyecto por su simplicidad y velocidad. Debido a que UDP no tiene la sobrecarga de establecer una conexión, garantizar la entrega y asegurar el orden, es más rápido y sencillo que los protocolos orientados a la conexión como TCP (Protocolo de Control de Transmisión). Esto hace que UDP sea adecuado para aplicaciones donde la velocidad es más importante que la fiabilidad, como en la transmisión de audio y vídeo en tiempo real.

## Datagramas en UDP:

Un datagrama UDP está compuesto por un encabezado y datos. El encabezado UDP tiene una longitud de 8 bytes y consta de los siguientes campos:

- Puerto de origen (Source Port) 2 bytes: Este es el número de puerto de la aplicación en el host que envía el datagrama.
- Puerto de destino (Destination Port) 2 bytes: Este es el número de puerto de la aplicación en el host que recibe el datagrama.
- Longitud (Length) 2 bytes: Esta es la longitud en bytes de todo el datagrama (encabezado y datos).
- Checksum (Checksum)2 bytes: Se utiliza para la verificación de errores del encabezado y los datos, siendo un método sencillo de verificación de errores, lo que significa que los paquetes que se detectan como defectuosos simplemente se descartan, es decir, "disparar y olvidar", dejamos que la capa 5 se preocupe de eso.

Los datos siguen al encabezado y contienen la carga útil del datagrama.

## Aclaraciones Importantes:

- Porque UDP es un protocolo sin conexión, no establece una conexión antes de enviar datos. Esto significa que UDP no tiene un apretón de manos de tres vías como TCP. 
- UDP no garantiza que los datos sean recibidos. Esto significa que UDP no tiene confirmaciones (ACK) o confirmaciones negativas (NACK) como TCP. 
- UDP no garantiza que los datos sean recibidos en el mismo orden en que se enviaron. Esto significa que UDP no tiene números de secuencia como TCP. 
- La simplicidad y velocidad de UDP tienen un costo de confiabilidad. Las aplicaciones que usan UDP deben poder manejar paquetes perdidos, duplicados y desordenados. 
- A pesar de sus limitaciones, UDP se utiliza en muchos protocolos importantes de Internet, incluidos DNS (Sistema de Nombres de Dominio), DHCP (Protocolo de Configuración Dinámica de Hosts) y RTP (Protocolo de Transporte en Tiempo Real).

## Detalles del Sistema:

- Cuando se ejecuta el comando `start` en `vpn_cli.py` se crea un nuevo hilo que ejecutará el método `run`, por lo que aún podran escribirse comandos en la consola.

- Cada acción creará un mensaje de registro que se almacenará en el archivo `logs.txt` para ser mostrado cuando se solicite.

- El usuario creado con el comando `create_user` de `vpn_cli.py` se guardará en `users.json`.

- Los usuarios y VLAN restringidos se almacenarán en `restricted_users.json` y `restricted_vlans.json`, respectivamente.

## Referencias:

- [Practical Networking Youtube](https://www.youtube.com/@PracticalNetworking): the main source for information about the transport layer protocols.