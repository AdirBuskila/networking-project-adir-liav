# ⚡ CYBER CHAT - TCP/IP Network Project ⚡

**Students:** Adir Buskila & Liav Weizman  
**Course:** Computer Networks  
**Date:** December 2025

---

## 📋 Project Overview

This project demonstrates practical understanding of **TCP/IP networking** through two parts:

1. **Part 1:** Packet Encapsulation - Creating TCP/IP packets and capturing with Wireshark
2. **Part 2:** Chat Application - Multi-client TCP chat system with GUI

---

## 📁 Project Structure

| File | Description |
|------|-------------|
| **Part 1 - Encapsulation** ||
| `group01_http_input.csv` | 📄 CSV with 20 application layer messages (HTTP/DNS) |
| `tcp_ip_encapsulation.ipynb` | 📓 Jupyter notebook for packet encapsulation |
| **Part 2 - Chat Application** ||
| `main.py` | 🚀 Entry point - Launcher GUI |
| `server.py` | 🖥️ TCP Server - handles 50+ concurrent clients |
| `client.py` | 💬 TCP Client - GUI chat interface |
| `config.py` | ⚙️ Configuration and constants |
| `utils.py` | 🛠️ Utilities, logging, validation |
| `ui_components.py` | 🎨 Reusable UI widgets |

---

## 🚀 Quick Start

### Part 1: Packet Encapsulation
```bash
# Install dependencies
pip install pandas scapy

# Run Jupyter notebook
jupyter notebook networking-project-adir-liav\tcp_ip_encapsulation.ipynb
```

### Part 2: Chat Application
```bash
# Option 1: GUI Launcher
python main.py

# Option 2: Direct modes
python main.py server    # Start server
python main.py client    # Start client
```

---

## 📊 Part 1 - Packet Encapsulation

### CSV Input File (`group01_http_input.csv`)
Contains 20 application layer messages with required fields:
- `msg_id` - Message identifier
- `app_protocol` - Protocol (HTTP, DNS)
- `src_app` - Source application
- `dst_app` - Destination application
- `message` - Message content
- `timestamp` - Time offset

### Jupyter Notebook Process
1. **Load CSV** - Read application messages
2. **Validate Schema** - Check required columns
3. **Build IP Header** - Version, TTL, checksum, addresses
4. **Build TCP Header** - Ports, sequence numbers, flags
5. **Encapsulate** - Combine layers into packets
6. **Send** - Transmit via raw sockets (Linux/macOS) or Scapy (Windows)
7. **Capture** - Record in Wireshark

### Wireshark Capture
1. Open Wireshark → Select **Npcap Loopback Adapter**
2. Start capture
3. Run notebook cells to send packets
4. Apply filter: `tcp.port == 12345`
5. Stop and save as `.pcap`

---

## 💬 Part 2 - Chat Application

### Technical Requirements Met

| Requirement | Implementation |
|-------------|----------------|
| TCP Protocol | `socket.SOCK_STREAM` |
| Bidirectional Communication | Server ↔ Multiple Clients |
| Handle ≥5 Concurrent Clients | `MAX_CLIENTS = 50` with threading |
| Server Mediates Between Clients | Broadcast + Private DM routing |
| Real-time Messaging | Threaded receive loops |
| Sockets Only | Pure `socket` library |
| Multi-threading | `threading.Thread` per client |
| Error Handling | Try/except + graceful cleanup |
| Clean Code | 6 modular, documented files |
| **BONUS: GUI** | Full Tkinter interface |

### Server Features
- 📊 Live statistics (users, messages, uptime, data TX/RX)
- 📜 Color-coded server logs
- 👑 Admin controls (kick users, broadcast announcements)
- 📤 Export logs to file
- 👥 User status tracking (Online/Away/Busy)

### Client Features
- 🎨 Cyberpunk-themed GUI
- 👤 User status (Online/Away/Busy)
- 🔒 Private messages (click user to DM)
- 😊 Emoji picker (40+ emojis)
- 📥 Export chat history
- ⌨️ Chat commands (`/help`, `/status`, `/dm`, `/clear`, `/save`)

---

## ⌨️ Client Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/status <online\|away\|busy>` | Change your status |
| `/dm <user> <message>` | Send private message |
| `/clear` | Clear chat window |
| `/save` | Export chat history |

### Protocol Commands
| Command | Description |
|---------|-------------|
| `LIST` | Get online users |
| `TO:user:message` | Send private message |
| `STATUS:away` | Change status |
| `QUIT` | Disconnect |

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 12345
MAX_CLIENTS = 50
BUFFER_SIZE = 4096
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                    (Launcher GUI)                            │
└─────────────────────┬───────────────────────┬───────────────┘
                      │                       │
          ┌───────────▼───────────┐ ┌────────▼────────┐
          │      server.py        │ │    client.py     │
          │  (TCP Server + GUI)   │ │ (TCP Client+GUI) │
          └───────────┬───────────┘ └────────┬────────┘
                      │                       │
          ┌───────────▼───────────────────────▼───────────┐
          │              ui_components.py                  │
          │         (Reusable styled widgets)              │
          └───────────────────────┬───────────────────────┘
                                  │
          ┌───────────────────────▼───────────────────────┐
          │         config.py      │      utils.py         │
          │        (Settings)      │     (Helpers)         │
          └───────────────────────────────────────────────┘
```

---

## 📂 Output Files

| File | Location | Description |
|------|----------|-------------|
| `cyber_chat.log` | Project folder | Application log |
| `chat_history/*.txt` | chat_history/ | Exported conversations |
| `server_logs_*.txt` | Project folder | Server log exports |

---

## ✅ Deliverables Checklist

### Part 1 - Packet Encapsulation
- [x] `group01_http_input.csv` - Application messages (20 rows)
- [x] `tcp_ip_encapsulation.ipynb` - Executed notebook with outputs
- [ ] Wireshark `.pcap` capture file

### Part 2 - Chat Application
- [x] `server.py` - Multi-threaded TCP server
- [x] `client.py` - GUI chat client
- [x] Supporting modules (`main.py`, `config.py`, `utils.py`, `ui_components.py`)
- [ ] Chat traffic `.pcap` capture file

---

## 🤖 AI Usage

This project was developed with assistance from **Claude (Anthropic)** for:
- Code structure and organization
- Debugging and error handling
- Documentation and comments
- UI/UX improvements

All code was reviewed, understood, and tested by the students.

---

## 👥 Authors

**Adir Buskila & Liav Weizman**  
Computer Networks Course, December 2025

---

<p align="center">
  <b>⚡ CYBER CHAT ⚡</b><br>
  <i>TCP/IP Network Project</i>
</p>
