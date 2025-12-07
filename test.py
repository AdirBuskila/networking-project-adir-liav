"""
TCP/IP Encapsulation Test Script
Students: Adir Buksila & Liav Wizman

This script tests the core functionality of the TCP/IP encapsulation project.
Run this to verify everything works before using the Jupyter notebook.
"""

import socket
import struct
import random
import time
import platform
import pandas as pd
from typing import Optional

print("="*60)
print("TCP/IP ENCAPSULATION PROJECT - TEST SCRIPT")
print("Students: Adir Buksila & Liav Wizman")
print("="*60)
print()

# Detect platform
IS_WINDOWS = (platform.system() == 'Windows')
print(f"[1] Platform Detection:")
print(f"    Operating System: {platform.system()}")
print(f"    Windows Mode: {IS_WINDOWS}")
print()

# Try to import Scapy
print(f"[2] Scapy Import:")
try:
    from scapy.all import IP as SCAPY_IP, TCP as SCAPY_TCP, Raw as SCAPY_Raw, send as scapy_send, get_if_list
    HAVE_SCAPY = True
    print("    ✓ Scapy imported successfully!")
except Exception as e:
    HAVE_SCAPY = False
    SCAPY_IMPORT_ERR = e
    print(f"    ✗ Scapy import failed: {e}")
    print("      Install with: pip install scapy")
print()

# Test CSV loading
print(f"[3] CSV Loading:")
try:
    CSV_PATH = "./input_messages.csv"
    messages_df = pd.read_csv(CSV_PATH)
    print(f"    ✓ Loaded {len(messages_df)} messages from {CSV_PATH}")
    print(f"    Columns: {list(messages_df.columns)}")
except Exception as e:
    print(f"    ✗ Failed to load CSV: {e}")
print()

# Helper functions
def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b'\0'
    res = sum(struct.unpack('!%dH' % (len(data)//2), data))
    while res >> 16:
        res = (res & 0xFFFF) + (res >> 16)
    return ~res & 0xFFFF

def hexdump(data: bytes, width: int = 16):
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
        ascii_bytes = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"    {i:04x}  {hex_bytes:<{width*3}}  {ascii_bytes}")

def build_ip_header(src_ip: str, dst_ip: str, payload_len: int, proto: int = socket.IPPROTO_TCP) -> bytes:
    version_ihl = (4 << 4) + 5
    tos = 0
    total_length = 20 + payload_len
    identification = random.randint(0, 65535)
    flags_fragment = 0
    ttl = 64
    header_checksum = 0
    src = socket.inet_aton(src_ip)
    dst = socket.inet_aton(dst_ip)
    ip_header = struct.pack('!BBHHHBBH4s4s',
                            version_ihl, tos, total_length, identification,
                            flags_fragment, ttl, proto, header_checksum,
                            src, dst)
    chksum = checksum(ip_header)
    ip_header = struct.pack('!BBHHHBBH4s4s',
                            version_ihl, tos, total_length, identification,
                            flags_fragment, ttl, proto, chksum,
                            src, dst)
    return ip_header

def build_tcp_header(src_ip: str, dst_ip: str, src_port: int, dst_port: int, 
                     payload: bytes = b'', seq: Optional[int] = None, 
                     ack_seq: int = 0, flags: int = 0x02, window: int = 65535) -> bytes:
    if seq is None:
        seq = random.randint(0, 0xFFFFFFFF)
    doff_reserved = (5 << 4)
    checksum_tcp = 0
    urg_ptr = 0
    tcp_header = struct.pack('!HHLLBBHHH',
                             src_port, dst_port, seq, ack_seq,
                             doff_reserved, flags, window,
                             checksum_tcp, urg_ptr)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(payload)
    pseudo_header = struct.pack('!4s4sBBH',
                                socket.inet_aton(src_ip), socket.inet_aton(dst_ip),
                                placeholder, protocol, tcp_length)
    chksum = checksum(pseudo_header + tcp_header + payload)
    tcp_header = struct.pack('!HHLLBBHHH',
                             src_port, dst_port, seq, ack_seq,
                             doff_reserved, flags, window,
                             chksum, urg_ptr)
    return tcp_header

# Test packet building
print(f"[4] Packet Building Test:")
try:
    src_ip = '127.0.0.1'
    dst_ip = '127.0.0.1'
    src_port = 52001
    dst_port = 12345
    payload = b'Hello from Adir & Liav!'
    
    ip_hdr = build_ip_header(src_ip, dst_ip, 20 + len(payload))
    tcp_hdr = build_tcp_header(src_ip, dst_ip, src_port, dst_port, payload)
    full_packet = ip_hdr + tcp_hdr + payload
    
    print(f"    ✓ Built packet successfully!")
    print(f"    IP Header: {len(ip_hdr)} bytes")
    print(f"    TCP Header: {len(tcp_hdr)} bytes")
    print(f"    Payload: {len(payload)} bytes")
    print(f"    Total Packet: {len(full_packet)} bytes")
    print()
    print(f"    Full packet hexdump:")
    hexdump(full_packet)
except Exception as e:
    print(f"    ✗ Packet building failed: {e}")
print()

# Test RawTcpTransport class
print(f"[5] Transport Class Test:")

class RawTcpTransport:
    def __init__(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, iface: Optional[str] = None):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.iface = iface
        self.windows_fallback = IS_WINDOWS
        
        if not self.windows_fallback:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        else:
            if not HAVE_SCAPY:
                raise RuntimeError(
                    f"Windows detected but Scapy is not available.\n"
                    "Install with: pip install scapy. Ensure Npcap is installed."
                )

    def encapsulate(self, data: bytes, flags: int = 0x02) -> bytes:
        tcp = build_tcp_header(self.src_ip, self.dst_ip, self.src_port, self.dst_port, data, flags=flags)
        ip = build_ip_header(self.src_ip, self.dst_ip, len(tcp) + len(data))
        return ip + tcp + data

    def send(self, data: bytes, flags: int = 0x02):
        if not self.windows_fallback:
            pkt = self.encapsulate(data, flags=flags)
            self.sock.sendto(pkt, (self.dst_ip, 0))
        else:
            scapy_pkt = SCAPY_IP(src=self.src_ip, dst=self.dst_ip) / \
                        SCAPY_TCP(sport=self.src_port, dport=self.dst_port, flags=flags) / \
                        SCAPY_Raw(data)
            chosen_iface = self.iface
            if chosen_iface is None and self.dst_ip in ("127.0.0.1", "::1"):
                chosen_iface = "Npcap Loopback Adapter"
            scapy_send(scapy_pkt, verbose=False, iface=chosen_iface)

try:
    transport = RawTcpTransport('127.0.0.1', '127.0.0.1', 52001, 12345, iface="\\Device\\NPF_Loopback")
    print(f"    ✓ Transport class created successfully!")
    print(f"    Using Windows fallback: {transport.windows_fallback}")
except Exception as e:
    print(f"    ✗ Transport creation failed: {e}")
print()

# List interfaces (Windows only)
if IS_WINDOWS and HAVE_SCAPY:
    print(f"[6] Available Network Interfaces:")
    try:
        interfaces = get_if_list()
        for i, iface in enumerate(interfaces):
            print(f"    {i+1}. {iface}")
    except Exception as e:
        print(f"    Could not list interfaces: {e}")
    print()

# Test sending packets
print(f"[7] Packet Sending Test:")
print("    ⚠️  Make sure Wireshark is capturing on Npcap Loopback Adapter!")
print("       Filter: ip.addr == 127.0.0.1 && tcp.port == 12345")
print()

try:
    print("    Sending 3 test packets...")
    for i in range(3):
        payload = f'Test Packet {i+1} from Adir & Liav'.encode()
        transport.send(payload, flags=0x18)  # PSH+ACK
        print(f"    ✓ Sent packet {i+1}: {payload.decode()}")
        time.sleep(0.5)
    print("    ✓ All test packets sent!")
except Exception as e:
    print(f"    ✗ Packet sending failed: {e}")
    print(f"      Error type: {type(e).__name__}")
print()

# Summary
print("="*60)
print("TEST SUMMARY")
print("="*60)
print(f"Platform: {platform.system()} (Windows mode: {IS_WINDOWS})")
print(f"Scapy: {'Available' if HAVE_SCAPY else 'Not available'}")
print(f"CSV: Loaded {len(messages_df)} messages")
print()
print("To capture packets in Wireshark:")
print("1. Open Wireshark")
print("2. Start capture on 'Npcap Loopback Adapter'")
print("3. Apply filter: ip.addr == 127.0.0.1 && tcp.port == 12345")
print("4. Run this script or the Jupyter notebook")
print()
print("✓ All tests completed!")
print("="*60)


