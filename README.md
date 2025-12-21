# ⚡ CYBER CHAT - TCP/IP Network Project ⚡

**Students:** Adir Buskila & Liav Wizman  
**Course:** Computer Networks  
**Date:** December 2025

---

## 📁 Project Structure

| File | Description |
|------|-------------|
| `main.py` | 🚀 **Main Entry Point** - Launcher GUI |
| `server.py` | 🖥️ **Enhanced Server** with admin features |
| `client.py` | 💬 **Enhanced Client** with modern features |
| `config.py` | ⚙️ Configuration, colors, and constants |
| `protocol.py` | 🔐 Message encryption & protocol handling |
| `utils.py` | 🛠️ Logging, chat history, helper functions |
| `ui_components.py` | 🎨 Reusable styled UI widgets |
| `cyber_chat.py` | 📦 **Backup** - Original single-file version |
| `tcp_ip_encapsulation.ipynb` | 📓 Part 1: Packet encapsulation notebook |

---

## 🚀 Quick Start

### Run the Application
```bash
python main.py              # Opens launcher GUI (recommended)
python main.py server       # Start server directly
python main.py client       # Start client directly  
python main.py --help       # Show help
```

### Backup Version (Single File)
```bash
python cyber_chat.py        # Original version
```

### Part 1: Packet Encapsulation
```bash
jupyter notebook tcp_ip_encapsulation.ipynb
```

---

## ⭐ Features Overview

### 🖥️ Server Features
| Feature | Description |
|---------|-------------|
| 📊 Live Statistics | Connected users, messages, uptime, peak users, data TX/RX |
| 📜 Color-coded Logs | Info, success, warning, error, message logs |
| 👑 Admin Controls | Kick users, broadcast announcements |
| 📤 Export Logs | Save server logs to file |
| 👥 User Management | See all connected users with status |

### 💬 Client Features
| Feature | Description |
|---------|-------------|
| 🎨 Cyberpunk UI | Dark theme with neon accents |
| 👤 User Status | Online / Away / Busy - click to change |
| 🔒 Private Messages | Click any user to send DM |
| 😊 Emoji Picker | 40+ emojis with shortcuts |
| 📥 Save Chat | Export conversation to `.txt` file |
| ⌨️ Commands | Built-in chat commands |

### 🔐 Security Features
| Feature | Description |
|---------|-------------|
| 🔐 Encryption | XOR-based encryption with SHA-256 key expansion |
| ✅ Validation | Username and message validation |
| 🛡️ Sanitization | Input sanitization to prevent issues |

---

## 📋 How to Use

### Step 1: Start the Server
1. Run `python main.py`
2. Click **🖥️ START SERVER**
3. Click the green **▶ START SERVER** button
4. Server is now listening on `127.0.0.1:12345`

### Step 2: Connect Clients
1. Open new terminal(s)
2. Run `python main.py`
3. Click **💬 JOIN AS CLIENT**
4. Enter username and click **⚡ CONNECT ⚡**

### Step 3: Chat!
- **Send message:** Type and press Enter
- **Private DM:** Click a username in the sidebar
- **Change status:** Click your status badge (🟢 Online)
- **Use emojis:** Click 😊 or use shortcuts like `:)`
- **Save chat:** Click "📥 Save Chat" button

---

## ⌨️ Client Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/status <online\|away\|busy>` | Change your status |
| `/dm <user> <message>` | Send private message |
| `/clear` | Clear chat window |
| `/save` | Export chat history to file |
| `/ping` | Check connection latency |

### Raw Protocol Commands
| Command | Description |
|---------|-------------|
| `LIST` | Get list of online users |
| `TO:user:message` | Send private message |
| `STATUS:away` | Change status |
| `QUIT` | Disconnect from server |

---

## 😊 Emoji Shortcuts

| Shortcut | Emoji | Shortcut | Emoji |
|----------|-------|----------|-------|
| `:)` | 😊 | `:(` | 😢 |
| `:D` | 😄 | `;)` | 😉 |
| `:P` | 😛 | `<3` | ❤️ |
| `:fire:` | 🔥 | `:+1:` | 👍 |
| `:star:` | ⭐ | `:rocket:` | 🚀 |
| `:check:` | ✅ | `:x:` | ❌ |
| `:lock:` | 🔒 | `:eyes:` | 👀 |

---

## 👑 Admin Features (Server)

### Kick Users
1. Select a user in the "CONNECTED USERS" list
2. Click **🚫 Kick** button
3. Confirm the kick

### Broadcast Announcements
1. Type message in the admin input at the bottom
2. Click **📢 Broadcast**
3. All users receive: `📢 ADMIN: your message`

### Export Logs
- Click **📤 Export** to save logs to `server_logs_YYYYMMDD_HHMMSS.txt`

---

## 👤 User Status System

| Status | Color | Meaning |
|--------|-------|---------|
| 🟢 Online | Green | Active and available |
| 🟡 Away | Yellow | Temporarily away |
| 🔴 Busy | Red | Do not disturb |

**To change status:**
- Click your status badge in the header, OR
- Use command: `/status away`

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Network
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 12345
MAX_CLIENTS = 50

# Security
ENCRYPTION_KEY = b'CyberChat2024Key'
ENABLE_ENCRYPTION = True

# Admin
ADMIN_PASSWORD = "admin123"
```

---

## 📊 Wireshark Capture

### Capture Chat Traffic
1. Open Wireshark
2. Select **Npcap Loopback Adapter** (for localhost)
3. Start capture
4. Apply filter: `tcp.port == 12345`
5. Chat between server and clients
6. Stop capture and save as `.pcap`

### What You'll See
- TCP handshake (SYN, SYN-ACK, ACK)
- Chat messages in TCP payload
- Connection teardown (FIN, ACK)

---

## 📂 Output Files

| File | Location | Description |
|------|----------|-------------|
| `cyber_chat.log` | Project folder | Application log file |
| `chat_history/*.txt` | chat_history folder | Exported chat conversations |
| `server_logs_*.txt` | Project folder | Exported server logs |

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
          │    config.py    │    utils.py    │ protocol.py│
          │   (Settings)    │   (Helpers)    │(Encryption)│
          └───────────────────────────────────────────────┘
```

---

## ✅ Project Deliverables

### Part 1: Packet Encapsulation
- [x] `group01_http_input.csv` - Input messages
- [x] `tcp_ip_encapsulation.ipynb` - Analysis notebook
- [ ] Wireshark `.pcap` capture

### Part 2: Chat Application
- [x] Modular chat application (7 files)
- [x] `cyber_chat.py` backup (single file)
- [ ] Chat traffic `.pcap` capture

---

## 👥 Authors

**Adir Buskila & Liav Wizman**  
Computer Networks Course, December 2025

---

<p align="center">
  <b>⚡ CYBER CHAT ⚡</b><br>
  <i>TCP/IP Network Project</i>
</p>
