# common/protocol.py

import struct
import asyncio

# Usaremos un 'unsigned int' (4 bytes) para la longitud.
# '!' significa orden de red (big-endian).
HEADER_FORMAT = '!I'
HEADER_LENGTH = struct.calcsize(HEADER_FORMAT)

# --- Versión Asíncrona (para Servidor A con asyncio) ---

async def send_msg_async(writer: asyncio.StreamWriter, msg_bytes: bytes):
    """
    (Asíncrono) Empaqueta y envía un mensaje.
    1. Calcula longitud.
    2. Empaqueta longitud en 4 bytes.
    3. Envía header + mensaje.
    """
    # 1. Calcular y empaquetar longitud
    msg_len = len(msg_bytes)
    header = struct.pack(HEADER_FORMAT, msg_len)
    
    # 2. Enviar header y luego el mensaje
    writer.write(header)
    writer.write(msg_bytes)
    
    # 3. Esperar a que el buffer se vacíe
    await writer.drain()

async def read_msg_async(reader: asyncio.StreamReader) -> bytes:
    """
    (Asíncrono) Lee y desempaqueta un mensaje.
    1. Lee 4 bytes de header.
    2. Desempaqueta la longitud.
    3. Lee exactamente 'longitud' bytes.
    """
    try:
        # 1. Leer header
        header = await reader.readexactly(HEADER_LENGTH)
        
        # 2. Desempaquetar longitud
        msg_len = struct.unpack(HEADER_FORMAT, header)[0]
        
        # 3. Leer cuerpo del mensaje
        msg_bytes = await reader.readexactly(msg_len)
        
        return msg_bytes
        
    except asyncio.IncompleteReadError:
        # Conexión cerrada prematuramente
        return None

# --- Versión Síncrona (para Servidor B con socketserver) ---

def send_msg_sync(sock, msg_bytes: bytes):
    """(Síncrono) Empaqueta y envía un mensaje."""
    msg_len = len(msg_bytes)
    header = struct.pack(HEADER_FORMAT, msg_len)
    
    # sendall se asegura de enviar todo
    sock.sendall(header + msg_bytes)

def read_msg_sync(sock) -> bytes:
    """(Síncrono) Lee y desempaqueta un mensaje."""
    
    def recv_all(s, n):
        """Función helper para asegurar que leemos N bytes."""
        data = bytearray()
        while len(data) < n:
            packet = s.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    # 1. Leer header
    header = recv_all(sock, HEADER_LENGTH)
    if not header:
        return None
        
    # 2. Desempaquetar longitud
    msg_len = struct.unpack(HEADER_FORMAT, header)[0]
    
    # 3. Leer cuerpo del mensaje
    return recv_all(sock, msg_len)