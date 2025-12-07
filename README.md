# TCP/IP Encapsulation Project

**Students:** Adir Buksila & Liav Wizman  
**Course:** Computer Networks  
**Date:** December 2025

---

## 📋 Project Overview

This project demonstrates **TCP/IP packet encapsulation** by manually constructing IPv4 and TCP headers, sending crafted packets over the network, and capturing them with Wireshark for analysis.

### Learning Objectives
- Understand the TCP/IP protocol stack layers
- Learn how application data is encapsulated into network packets
- Build IP and TCP headers from scratch
- Analyze network traffic using Wireshark

---

## 📁 Project Files

| File | Description |
|------|-------------|
| `tcp_ip_encapsulation.ipynb` | Main Jupyter notebook with encapsulation code |
| `input_messages.csv` | Input CSV file with HTTP messages |
| `test.py` | Python test script to verify functionality |
| `README.md` | This file |

---

## 🔧 Prerequisites

### Software Requirements

1. **Python 3.8+** - Programming language
2. **Wireshark** - Network protocol analyzer
3. **Npcap** - Packet capture library for Windows

### Python Packages

```bash
pip install scapy pandas jupyter
```

### Windows Setup (Important!)

1. **Install Wireshark with Npcap:**
   - Download from [wireshark.org](https://www.wireshark.org/)
   - During installation, ensure these options are checked:
     - ✅ Install Npcap
     - ✅ WinPcap API-compatible mode
     - ✅ Support loopback traffic

2. **Run as Administrator:**
   - Jupyter notebook must run with administrator privileges
   - Right-click → "Run as administrator"

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install scapy pandas jupyter
```

### Step 2: Test the Setup

```bash
python test.py
```

Expected output:
```
============================================================
TCP/IP ENCAPSULATION PROJECT - TEST SCRIPT
Students: Adir Buksila & Liav Wizman
============================================================

[1] Platform Detection:
    Operating System: Windows
    Windows Mode: True

[2] Scapy Import:
    ✓ Scapy imported successfully!

[3] CSV Loading:
    ✓ Loaded 20 messages from ./input_messages.csv
...
✓ All tests completed!
```

### Step 3: Start Wireshark Capture

1. Open Wireshark
2. Select **Npcap Loopback Adapter** interface
3. Apply filter: `ip.addr == 127.0.0.1 && tcp.port == 12345`
4. Click Start Capture (blue shark fin)

### Step 4: Run the Notebook

```bash
jupyter notebook tcp_ip_encapsulation.ipynb
```

Run cells in order to:
1. Load CSV messages
2. Validate the schema
3. Build IP/TCP headers
4. Send packets
5. Observe in Wireshark

---

## 📊 CSV Input Format

The input CSV file must contain these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `msg_id` | Unique message identifier | 1, 2, 3... |
| `app_protocol` | Application protocol | HTTP, DNS |
| `src_port` | Source port number | 52001 |
| `dst_port` | Destination port number | 80, 443 |
| `message` | Message content | GET / HTTP/1.1 |
| `timestamp` | Time offset in seconds | 0.001 |

### Example CSV:
```csv
msg_id,app_protocol,src_port,dst_port,message,timestamp
1,HTTP,52001,80,GET / HTTP/1.1,0.001
2,HTTP,52001,80,Host: www.example.com,0.002
3,HTTP,80,52001,HTTP/1.1 200 OK,0.050
```

---

## 🔬 Technical Details

### TCP/IP Layer Model

```
┌─────────────────────────────────────┐
│  Application Layer (HTTP messages)  │  ← CSV Messages
├─────────────────────────────────────┤
│  Transport Layer (TCP Header)       │  ← 20 bytes
├─────────────────────────────────────┤
│  Network Layer (IP Header)          │  ← 20 bytes
├─────────────────────────────────────┤
│  Link Layer (Ethernet Frame)        │  ← Handled by OS/Npcap
└─────────────────────────────────────┘
```

### IPv4 Header Structure (20 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |    TOS        |         Total Length          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|     Fragment Offset     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  TTL  |    Protocol           |       Header Checksum         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source IP Address                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination IP Address                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### TCP Header Structure (20 bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Offset|  Res  |C|E|U|A|P|R|S|F|           Window              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |         Urgent Pointer        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### TCP Flags

| Flag | Hex Value | Description |
|------|-----------|-------------|
| SYN | 0x02 | Synchronize - initiate connection |
| ACK | 0x10 | Acknowledge - confirm receipt |
| SYN+ACK | 0x12 | Connection acknowledgment |
| PSH+ACK | 0x18 | Push data immediately |
| FIN | 0x01 | Finish - close connection |
| RST | 0x04 | Reset - abort connection |

---

## 🖥️ Wireshark Analysis

### Useful Filters

```
# All packets on port 12345
tcp.port == 12345

# Loopback traffic
ip.addr == 127.0.0.1

# Combined filter
ip.addr == 127.0.0.1 && tcp.port == 12345

# SYN packets only
tcp.flags.syn == 1 && tcp.flags.ack == 0

# Data packets (PSH+ACK)
tcp.flags.push == 1 && tcp.flags.ack == 1

# Follow TCP stream
tcp.stream eq 0
```

### What to Look For

1. **IP Header:** Version (4), TTL (64), Protocol (6=TCP), Addresses
2. **TCP Header:** Ports, Flags, Sequence numbers, Checksum
3. **Payload:** Your message data in ASCII

---

## 📝 Deliverables Checklist

- [x] CSV input file (`input_messages.csv`)
- [x] Executed Jupyter notebook with outputs
- [ ] Wireshark .pcap capture file
- [ ] Report with analysis and screenshots

---

## ⚠️ Troubleshooting

### "Scapy not available"
```bash
pip install scapy
```

### "Npcap not found" or "No interfaces"
- Reinstall Wireshark with Npcap
- Enable loopback support during installation

### "Permission denied" / "Access is denied"
- Run CMD/Jupyter as Administrator
- Right-click → Run as administrator

### "No packets visible in Wireshark"
- Ensure you're capturing on **Npcap Loopback Adapter**
- Check filter: `ip.addr == 127.0.0.1`
- Verify packets are being sent (check notebook output)

### Available Network Interfaces
Run this to see available interfaces:
```python
from scapy.all import get_if_list
print(get_if_list())
```

Look for: `\Device\NPF_Loopback`

---

## 📚 References

- [RFC 791 - Internet Protocol](https://tools.ietf.org/html/rfc791)
- [RFC 793 - Transmission Control Protocol](https://tools.ietf.org/html/rfc793)
- [Scapy Documentation](https://scapy.readthedocs.io/)
- [Wireshark User Guide](https://www.wireshark.org/docs/wsug_html/)

---

## 👥 Authors

- **Adir Buksila**
- **Liav Wizman**

Computer Networks Course Project, 2025

