"""
⚡ CYBER CHAT - Complete Single-File Chat Application
TCP/IP Network Project
Students: Adir Buskila & Liav Wizman

This is the single-file backup version with ALL features from the modular version.
Run this file and choose: SERVER or CLIENT

Usage:
    python cyber_chat.py           # Opens launcher GUI
    python cyber_chat.py server    # Start server directly
    python cyber_chat.py client    # Start client directly
"""

import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
import time
import random
import sys
import os
import json
import hashlib
import base64
from typing import Dict, Optional, List, Callable, Any
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

HOST = '127.0.0.1'
PORT = 12345
MAX_CLIENTS = 50
BUFFER_SIZE = 4096
PING_INTERVAL = 5

# User Status Types
STATUS_ONLINE = 'online'
STATUS_AWAY = 'away'
STATUS_BUSY = 'busy'

# Encryption (XOR-based for demonstration)
ENCRYPTION_KEY = b'CyberChat2024Key'
ENABLE_ENCRYPTION = False  # Set to True to enable

# 🎨 CYBERPUNK COLOR SCHEME
COLORS = {
    'bg_dark': '#0a0a0f',
    'bg_medium': '#12121a', 
    'bg_light': '#1a1a2e',
    'bg_card': '#16213e',
    'bg_hover': '#1f2940',
    'accent_cyan': '#00fff5',
    'accent_pink': '#ff00ff',
    'accent_purple': '#7b2cbf',
    'accent_blue': '#0077ff',
    'accent_green': '#00ff88',
    'accent_orange': '#ff6600',
    'accent_red': '#ff3366',
    'accent_yellow': '#ffcc00',
    'text_primary': '#ffffff',
    'text_secondary': '#8892b0',
    'text_dim': '#495670',
    'status_online': '#00ff88',
    'status_away': '#ffcc00',
    'status_busy': '#ff3366',
    'status_offline': '#495670',
    'border': '#233554',
}

FONTS = {
    'title': ('Consolas', 28, 'bold'),
    'header': ('Consolas', 22, 'bold'),
    'subheader': ('Consolas', 16, 'bold'),
    'body': ('Consolas', 11),
    'body_bold': ('Consolas', 11, 'bold'),
    'small': ('Consolas', 9),
    'small_bold': ('Consolas', 9, 'bold'),
    'tiny': ('Consolas', 8),
    'message': ('Consolas', 10),
}

# Emoji shortcuts
EMOJI_SHORTCUTS = {
    ':)': '😊', ':(': '😢', ':D': '😄', ';)': '😉',
    ':P': '😛', '<3': '❤️', ':fire:': '🔥', ':+1:': '👍',
    ':-1:': '👎', ':star:': '⭐', ':check:': '✅', ':x:': '❌',
    ':wave:': '👋', ':clap:': '👏', ':rocket:': '🚀', ':lock:': '🔒',
    ':key:': '🔑', ':eyes:': '👀', ':thinking:': '🤔', ':100:': '💯',
}

EMOJIS = [
    '😊', '😄', '😂', '🤣', '😉', '😍', '🥰', '😘',
    '😎', '🤔', '😅', '😢', '😭', '😤', '😡', '🤯',
    '👍', '👎', '👏', '🙌', '🤝', '✌️', '🤟', '👋',
    '❤️', '🔥', '⭐', '✨', '💯', '🎉', '🎊', '🚀',
    '✅', '❌', '⚡', '💬', '🔒', '🔑', '👀', '💪'
]

# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def format_timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")

def format_uptime(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_bytes(num_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"

def sanitize_username(username: str) -> str:
    return ''.join(c for c in username if c.isalnum() or c in '_-')[:20]

def validate_username(username: str) -> tuple:
    if not username:
        return (False, "Username cannot be empty")
    if len(username) < 2:
        return (False, "Username must be at least 2 characters")
    if len(username) > 20:
        return (False, "Username cannot exceed 20 characters")
    if not username[0].isalpha():
        return (False, "Username must start with a letter")
    if not all(c.isalnum() or c in '_-' for c in username):
        return (False, "Username can only contain letters, numbers, _ and -")
    return (True, "")

def validate_message(message: str) -> tuple:
    if not message.strip():
        return (False, "Message cannot be empty")
    if len(message) > 2000:
        return (False, "Message too long (max 2000 characters)")
    return (True, "")

def parse_address(address: str) -> tuple:
    try:
        if ':' in address:
            parts = address.split(':')
            return (parts[0] or HOST, int(parts[1]))
        return (address or HOST, PORT)
    except (ValueError, IndexError):
        return (HOST, PORT)

def replace_emoji_shortcuts(text: str) -> str:
    for shortcut, emoji in EMOJI_SHORTCUTS.items():
        text = text.replace(shortcut, emoji)
    return text

def parse_command(text: str) -> tuple:
    text = text.strip()
    if not text.startswith('/'):
        return (None, text)
    parts = text[1:].split(' ', 1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ''
    return (command, args)

def play_notification_sound():
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_OK)
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════
# CLIENT CONNECTION CLASS
# ═══════════════════════════════════════════════════════════════

class ClientConnection:
    """Represents a connected client with metadata."""
    
    def __init__(self, sock: socket.socket, address: tuple, username: str):
        self.socket = sock
        self.address = address
        self.username = username
        self.status = STATUS_ONLINE
        self.connected_at = datetime.now()
        self.last_ping = time.time()
        self.messages_sent = 0
        self.bytes_sent = 0
        self.bytes_received = 0
    
    def send(self, data: bytes) -> bool:
        try:
            self.socket.send(data)
            self.bytes_sent += len(data)
            return True
        except Exception:
            return False

# ═══════════════════════════════════════════════════════════════
# CHAT HISTORY
# ═══════════════════════════════════════════════════════════════

class ChatHistory:
    """Manages chat history storage."""
    
    def __init__(self, username: str):
        self.username = username
        self.history_dir = Path("chat_history")
        self.history_dir.mkdir(exist_ok=True)
        self.messages: List[Dict[str, Any]] = []
    
    def add_message(self, sender: str, content: str, msg_type: str = 'msg',
                    recipient: Optional[str] = None):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'sender': sender,
            'content': content,
            'type': msg_type,
            'recipient': recipient
        }
        self.messages.append(entry)
    
    def export_txt(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.history_dir / f"chat_{self.username}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"═══════════════════════════════════════════════════\n")
            f.write(f"  CYBER CHAT - Chat History Export\n")
            f.write(f"  User: {self.username}\n")
            f.write(f"  Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"═══════════════════════════════════════════════════\n\n")
            
            for msg in self.messages:
                time_str = msg['timestamp'].split('T')[1][:8] if 'T' in msg['timestamp'] else msg['timestamp']
                
                if msg['type'] == 'system':
                    f.write(f"[{time_str}] ⚡ SYSTEM: {msg['content']}\n")
                elif msg['type'] == 'private':
                    direction = "to" if msg['sender'] == self.username else "from"
                    other = msg['recipient'] if msg['sender'] == self.username else msg['sender']
                    f.write(f"[{time_str}] 🔒 Private {direction} {other}: {msg['content']}\n")
                else:
                    prefix = "You" if msg['sender'] == self.username else msg['sender']
                    f.write(f"[{time_str}] {prefix}: {msg['content']}\n")
            
            f.write(f"\n═══════════════════════════════════════════════════\n")
            f.write(f"  Total messages: {len(self.messages)}\n")
            f.write(f"═══════════════════════════════════════════════════\n")
        
        return str(filename)

# ═══════════════════════════════════════════════════════════════
# LAUNCHER - Choose Server or Client
# ═══════════════════════════════════════════════════════════════

class CyberLauncher:
    """Main launcher to choose between Server and Client."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚡ CYBER CHAT")
        self.root.geometry("600x500")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.resizable(False, False)
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        # Header line
        tk.Frame(self.root, bg=COLORS['accent_cyan'], height=3).pack(fill='x')
        
        # Main card
        card = tk.Frame(self.root, bg=COLORS['bg_card'])
        card.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Title
        tk.Label(card, text="⚡", font=('Segoe UI Emoji', 40),
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack(pady=(30, 0))
        
        tk.Label(card, text="CYBER CHAT", font=FONTS['title'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack()
        
        tk.Label(card, text="TCP/IP Network Project v2.0", font=FONTS['body'],
                fg=COLORS['text_secondary'], bg=COLORS['bg_card']).pack(pady=(5, 0))
        
        # Authors
        authors_frame = tk.Frame(card, bg=COLORS['bg_card'])
        authors_frame.pack(pady=15)
        tk.Label(authors_frame, text="by ", font=FONTS['small'],
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(side='left')
        tk.Label(authors_frame, text="Adir Buskila", font=FONTS['small_bold'],
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(side='left')
        tk.Label(authors_frame, text=" & ", font=FONTS['small'],
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(side='left')
        tk.Label(authors_frame, text="Liav Wizman", font=FONTS['small_bold'],
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(side='left')
        
        # Separator
        sep_frame = tk.Frame(card, bg=COLORS['bg_card'])
        sep_frame.pack(fill='x', padx=50, pady=20)
        tk.Frame(sep_frame, bg=COLORS['border'], height=1).pack(fill='x')
        
        # Buttons
        buttons_frame = tk.Frame(card, bg=COLORS['bg_card'])
        buttons_frame.pack(pady=20)
        
        # Server button
        server_frame = tk.Frame(buttons_frame, bg=COLORS['bg_card'])
        server_frame.pack(pady=10)
        
        server_btn = tk.Button(server_frame, text="🖥️  START SERVER",
                              font=('Consolas', 16, 'bold'),
                              bg=COLORS['accent_green'], fg=COLORS['bg_dark'],
                              activebackground=COLORS['accent_cyan'],
                              relief='flat', cursor='hand2', width=22, height=2,
                              command=self.start_server)
        server_btn.pack()
        tk.Label(server_frame, text="Host a chat room for others to join",
                font=FONTS['tiny'], fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(pady=(5, 0))
        
        # Client button
        client_frame = tk.Frame(buttons_frame, bg=COLORS['bg_card'])
        client_frame.pack(pady=10)
        
        client_btn = tk.Button(client_frame, text="💬  JOIN AS CLIENT",
                              font=('Consolas', 16, 'bold'),
                              bg=COLORS['accent_purple'], fg=COLORS['text_primary'],
                              activebackground=COLORS['accent_pink'],
                              relief='flat', cursor='hand2', width=22, height=2,
                              command=self.start_client)
        client_btn.pack()
        tk.Label(client_frame, text="Connect to an existing server",
                font=FONTS['tiny'], fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(pady=(5, 0))
        
        # Footer
        footer = tk.Frame(card, bg=COLORS['bg_card'])
        footer.pack(side='bottom', pady=20)
        
        info_frame = tk.Frame(footer, bg=COLORS['bg_light'], padx=15, pady=8)
        info_frame.pack()
        tk.Label(info_frame, text="💡", font=FONTS['small'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_light']).pack(side='left')
        tk.Label(info_frame, text=f" Default: {HOST}:{PORT}  •  Start SERVER first!",
                font=FONTS['tiny'], fg=COLORS['text_secondary'], bg=COLORS['bg_light']).pack(side='left')
        
        # Bottom line
        tk.Frame(self.root, bg=COLORS['accent_pink'], height=3).pack(fill='x', side='bottom')
        
        # Hover effects
        def on_enter_server(e): server_btn.configure(bg=COLORS['accent_cyan'])
        def on_leave_server(e): server_btn.configure(bg=COLORS['accent_green'])
        def on_enter_client(e): client_btn.configure(bg=COLORS['accent_pink'])
        def on_leave_client(e): client_btn.configure(bg=COLORS['accent_purple'])
        
        server_btn.bind('<Enter>', on_enter_server)
        server_btn.bind('<Leave>', on_leave_server)
        client_btn.bind('<Enter>', on_enter_client)
        client_btn.bind('<Leave>', on_leave_client)
        
    def start_server(self):
        self.root.destroy()
        server = CyberServer()
        server.run()
        
    def start_client(self):
        self.root.destroy()
        client = CyberClient()
        client.run()
        
    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# SERVER
# ═══════════════════════════════════════════════════════════════

class CyberServer:
    """Enhanced Chat Server with Dashboard and Admin Features."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🖥️ CYBER CHAT SERVER")
        self.root.geometry("950x650")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.minsize(800, 500)
        
        self.server_socket: Optional[socket.socket] = None
        self.clients: Dict[str, ClientConnection] = {}
        self.lock = threading.Lock()
        self.running = False
        self.start_time: Optional[float] = None
        
        self.stats = {
            'messages': 0,
            'bytes_sent': 0,
            'bytes_recv': 0,
            'peak_clients': 0,
            'total_connections': 0
        }
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS['bg_medium'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=COLORS['bg_medium'])
        header_content.pack(fill='both', expand=True, padx=20, pady=12)
        
        # Title
        title_frame = tk.Frame(header_content, bg=COLORS['bg_medium'])
        title_frame.pack(side='left')
        
        tk.Label(title_frame, text="🖥️ CYBER CHAT SERVER", font=FONTS['header'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_medium']).pack(side='left')
        tk.Label(title_frame, text="v2.0", font=FONTS['small'],
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left', padx=10)
        
        # Status indicator
        self.status_frame = tk.Frame(header_content, bg=COLORS['bg_medium'])
        self.status_frame.pack(side='right')
        
        self.status_dot = tk.Label(self.status_frame, text="●", font=('Consolas', 16),
                                   fg=COLORS['accent_red'], bg=COLORS['bg_medium'])
        self.status_dot.pack(side='left')
        
        self.status_text = tk.Label(self.status_frame, text="OFFLINE", font=FONTS['small_bold'],
                                    fg=COLORS['accent_red'], bg=COLORS['bg_medium'])
        self.status_text.pack(side='left', padx=(3, 0))
        
        # Glow line
        tk.Frame(self.root, bg=COLORS['accent_cyan'], height=2).pack(fill='x')
        
        # Main content
        content = tk.Frame(self.root, bg=COLORS['bg_dark'])
        content.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Left panel
        left = tk.Frame(content, bg=COLORS['bg_card'], width=280)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        
        # Controls Section
        ctrl = tk.Frame(left, bg=COLORS['bg_card'])
        ctrl.pack(fill='x', padx=15, pady=15)
        
        tk.Label(ctrl, text="⚡ CONTROLS", font=FONTS['body_bold'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack(anchor='w', pady=(0, 12))
        
        # Server address
        addr_frame = tk.Frame(ctrl, bg=COLORS['bg_light'])
        addr_frame.pack(fill='x', pady=(0, 10))
        tk.Label(addr_frame, text=f"📍 {HOST}:{PORT}", font=FONTS['small'],
                fg=COLORS['text_secondary'], bg=COLORS['bg_light']).pack(pady=5)
        
        # Buttons
        self.start_btn = tk.Button(ctrl, text="▶ START SERVER", font=FONTS['body_bold'],
                                   bg=COLORS['accent_green'], fg=COLORS['bg_dark'],
                                   relief='flat', cursor='hand2', command=self.start_server)
        self.start_btn.pack(fill='x', pady=3, ipady=6)
        
        self.stop_btn = tk.Button(ctrl, text="■ STOP SERVER", font=FONTS['body_bold'],
                                  bg=COLORS['accent_red'], fg=COLORS['text_primary'],
                                  relief='flat', cursor='hand2', state='disabled',
                                  command=self.stop_server)
        self.stop_btn.pack(fill='x', pady=3, ipady=6)
        
        # Separator
        tk.Frame(left, bg=COLORS['border'], height=1).pack(fill='x', padx=15, pady=10)
        
        # Stats Section
        stats_section = tk.Frame(left, bg=COLORS['bg_card'])
        stats_section.pack(fill='x', padx=15)
        
        tk.Label(stats_section, text="📊 STATISTICS", font=FONTS['body_bold'],
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(anchor='w', pady=(0, 10))
        
        self.stat_clients = self.create_stat(stats_section, "👥", "Connected", "0")
        self.stat_messages = self.create_stat(stats_section, "📨", "Messages", "0")
        self.stat_uptime = self.create_stat(stats_section, "⏱️", "Uptime", "00:00:00")
        self.stat_peak = self.create_stat(stats_section, "📈", "Peak Users", "0")
        self.stat_data = self.create_stat(stats_section, "📦", "Data TX/RX", "0 B")
        
        # Separator
        tk.Frame(left, bg=COLORS['border'], height=1).pack(fill='x', padx=15, pady=10)
        
        # Users Section
        users_section = tk.Frame(left, bg=COLORS['bg_card'])
        users_section.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        users_header = tk.Frame(users_section, bg=COLORS['bg_card'])
        users_header.pack(fill='x')
        
        tk.Label(users_header, text="👤 CONNECTED USERS", font=FONTS['body_bold'],
                fg=COLORS['accent_purple'], bg=COLORS['bg_card']).pack(side='left', pady=(0, 8))
        
        self.kick_btn = tk.Button(users_header, text="🚫 Kick", font=FONTS['tiny'],
                                  bg=COLORS['accent_red'], fg=COLORS['text_primary'],
                                  relief='flat', cursor='hand2', command=self.kick_selected_user)
        self.kick_btn.pack(side='right')
        
        self.users_list = tk.Listbox(users_section, font=FONTS['small'],
                                     bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                     relief='flat', highlightthickness=0,
                                     selectbackground=COLORS['accent_purple'])
        self.users_list.pack(fill='both', expand=True)
        
        # Right panel - Logs
        right = tk.Frame(content, bg=COLORS['bg_card'])
        right.pack(side='right', fill='both', expand=True)
        
        # Logs header
        logs_header = tk.Frame(right, bg=COLORS['bg_card'])
        logs_header.pack(fill='x', padx=15, pady=10)
        
        tk.Label(logs_header, text="📜 SERVER LOGS", font=FONTS['body_bold'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack(side='left')
        
        tk.Button(logs_header, text="🗑️ Clear", font=FONTS['tiny'],
                 bg=COLORS['bg_light'], fg=COLORS['text_secondary'],
                 relief='flat', cursor='hand2', command=self.clear_logs).pack(side='right')
        
        tk.Button(logs_header, text="📤 Export", font=FONTS['tiny'],
                 bg=COLORS['bg_light'], fg=COLORS['text_secondary'],
                 relief='flat', cursor='hand2', command=self.export_logs).pack(side='right', padx=5)
        
        # Log text
        self.log_text = scrolledtext.ScrolledText(right, font=FONTS['small'],
                                                  bg=COLORS['bg_medium'],
                                                  fg=COLORS['text_primary'],
                                                  relief='flat', wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        self.log_text.configure(state='disabled')
        
        # Log tags
        for tag, color in [('info', COLORS['accent_cyan']), ('success', COLORS['accent_green']),
                           ('warning', COLORS['accent_orange']), ('error', COLORS['accent_red']),
                           ('msg', COLORS['accent_pink']), ('admin', COLORS['accent_purple']),
                           ('system', COLORS['text_dim'])]:
            self.log_text.tag_configure(tag, foreground=color)
        
        # Admin panel
        admin_panel = tk.Frame(self.root, bg=COLORS['bg_medium'], height=50)
        admin_panel.pack(fill='x', side='bottom')
        admin_panel.pack_propagate(False)
        
        admin_content = tk.Frame(admin_panel, bg=COLORS['bg_medium'])
        admin_content.pack(fill='both', expand=True, padx=15, pady=8)
        
        tk.Label(admin_content, text="👑 ADMIN:", font=FONTS['small_bold'],
                fg=COLORS['accent_purple'], bg=COLORS['bg_medium']).pack(side='left')
        
        self.broadcast_entry = tk.Entry(admin_content, font=FONTS['small'],
                                        bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                        insertbackground=COLORS['accent_cyan'],
                                        relief='flat', width=40)
        self.broadcast_entry.pack(side='left', padx=10, ipady=4)
        self.broadcast_entry.bind('<Return>', lambda e: self.send_broadcast())
        
        tk.Button(admin_content, text="📢 Broadcast", font=FONTS['small_bold'],
                 bg=COLORS['accent_purple'], fg=COLORS['text_primary'],
                 relief='flat', cursor='hand2', command=self.send_broadcast).pack(side='left')
        
        self.log("Server initialized. Ready to start...", 'info')
    
    def create_stat(self, parent, icon: str, label: str, value: str):
        frame = tk.Frame(parent, bg=COLORS['bg_light'])
        frame.pack(fill='x', pady=2)
        
        tk.Label(frame, text=icon, font=FONTS['body'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_light']).pack(side='left', padx=8, pady=5)
        tk.Label(frame, text=label, font=FONTS['small'],
                fg=COLORS['text_secondary'], bg=COLORS['bg_light']).pack(side='left')
        val = tk.Label(frame, text=value, font=FONTS['body_bold'],
                      fg=COLORS['accent_cyan'], bg=COLORS['bg_light'])
        val.pack(side='right', padx=8)
        return val
        
    def log(self, message: str, tag: str = 'info'):
        ts = format_timestamp()
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"[{ts}] ", 'system')
        self.log_text.insert('end', f"{message}\n", tag)
        self.log_text.see('end')
        self.log_text.configure(state='disabled')
    
    def clear_logs(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')
        self.log("Logs cleared", 'system')
    
    def export_logs(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"server_logs_{timestamp}.txt"
            
            self.log_text.configure(state='normal')
            content = self.log_text.get('1.0', 'end')
            self.log_text.configure(state='disabled')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"═══════════════════════════════════════\n")
                f.write(f"  CYBER CHAT SERVER LOGS\n")
                f.write(f"  Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"═══════════════════════════════════════\n\n")
                f.write(content)
            
            self.log(f"Logs exported to {filename}", 'success')
        except Exception as e:
            self.log(f"Failed to export logs: {e}", 'error')
        
    def update_stats(self):
        if not self.running:
            return
        
        with self.lock:
            client_count = len(self.clients)
            if client_count > self.stats['peak_clients']:
                self.stats['peak_clients'] = client_count
        
        self.stat_clients.configure(text=str(client_count))
        self.stat_messages.configure(text=str(self.stats['messages']))
        self.stat_peak.configure(text=str(self.stats['peak_clients']))
        
        total_data = self.stats['bytes_sent'] + self.stats['bytes_recv']
        self.stat_data.configure(text=format_bytes(total_data))
        
        if self.start_time:
            uptime = int(time.time() - self.start_time)
            self.stat_uptime.configure(text=format_uptime(uptime))
        
        self.root.after(1000, self.update_stats)
    
    def update_users_list(self):
        self.users_list.delete(0, 'end')
        with self.lock:
            for username, conn in self.clients.items():
                status_icon = {'online': '🟢', 'away': '🟡', 'busy': '🔴'}.get(conn.status, '⚪')
                addr = f"{conn.address[0]}:{conn.address[1]}"
                self.users_list.insert('end', f"  {status_icon} {username} ({addr})")
                
    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(MAX_CLIENTS)
            
            self.running = True
            self.start_time = time.time()
            
            self.status_dot.configure(fg=COLORS['accent_green'])
            self.status_text.configure(text="ONLINE", fg=COLORS['accent_green'])
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
            
            self.log(f"Server started on {HOST}:{PORT}", 'success')
            self.log(f"Max clients: {MAX_CLIENTS}", 'info')
            
            threading.Thread(target=self.accept_loop, daemon=True).start()
            self.update_stats()
            
        except Exception as e:
            self.log(f"Failed to start server: {e}", 'error')
            
    def stop_server(self):
        self.running = False
        
        with self.lock:
            for username, conn in list(self.clients.items()):
                try:
                    conn.send("SYSTEM|Server shutting down. Goodbye!\n".encode())
                    conn.socket.close()
                except Exception:
                    pass
            self.clients.clear()
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        
        self.status_dot.configure(fg=COLORS['accent_red'])
        self.status_text.configure(text="OFFLINE", fg=COLORS['accent_red'])
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        self.update_users_list()
        
        self.log("Server stopped", 'warning')
        
    def accept_loop(self):
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.stats['total_connections'] += 1
                
                self.root.after(0, lambda a=address: 
                    self.log(f"New connection from {a[0]}:{a[1]}", 'info'))
                
                threading.Thread(target=self.handle_client, args=(client_socket, address),
                               daemon=True).start()
            except Exception:
                if self.running:
                    self.root.after(0, lambda: self.log("Accept error", 'error'))
                break
                
    def handle_client(self, client_socket: socket.socket, address: tuple):
        username = None
        
        try:
            client_socket.send("WELCOME|Enter your username: ".encode())
            
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                client_socket.close()
                return
            
            username = sanitize_username(data.decode().strip())
            
            if not username:
                client_socket.send("ERROR|Invalid username\n".encode())
                client_socket.close()
                return
            
            with self.lock:
                if username in self.clients:
                    client_socket.send(f"ERROR|Username '{username}' is already taken\n".encode())
                    client_socket.close()
                    return
                
                conn = ClientConnection(client_socket, address, username)
                self.clients[username] = conn
            
            self.root.after(0, lambda: self.log(f"'{username}' joined the chat", 'success'))
            self.root.after(0, self.update_users_list)
            
            client_socket.send(f"OK|Welcome to Cyber Chat, {username}! 🚀\n".encode())
            
            self.broadcast_system(f"'{username}' has joined the chat", exclude=username)
            self.broadcast_userlist()
            
            while self.running:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                self.stats['bytes_recv'] += len(data)
                
                with self.lock:
                    if username in self.clients:
                        self.clients[username].last_ping = time.time()
                
                message = data.decode().strip()
                if not message:
                    continue
                
                self.handle_message(username, message)
                
        except Exception as e:
            pass
        
        finally:
            with self.lock:
                if username and username in self.clients:
                    del self.clients[username]
            
            if username:
                self.root.after(0, lambda: self.log(f"'{username}' left the chat", 'warning'))
                self.broadcast_system(f"'{username}' has left the chat")
                self.broadcast_userlist()
            
            self.root.after(0, self.update_users_list)
            
            try:
                client_socket.close()
            except Exception:
                pass
    
    def handle_message(self, sender: str, message: str):
        self.stats['messages'] += 1
        self.root.after(0, lambda: self.log(f"[{sender}] {message}", 'msg'))
        
        upper_msg = message.upper()
        
        if upper_msg == "QUIT":
            with self.lock:
                if sender in self.clients:
                    self.clients[sender].socket.close()
            return
        
        elif upper_msg == "LIST":
            with self.lock:
                users = list(self.clients.keys())
                statuses = {u: c.status for u, c in self.clients.items()}
            
            user_str = ", ".join(f"{u}({statuses[u]})" for u in users)
            self.send_to_user(sender, f"USERS|Online: {user_str}\n")
        
        elif upper_msg.startswith("STATUS:"):
            new_status = message.split(":", 1)[1].strip().lower()
            if new_status in [STATUS_ONLINE, STATUS_AWAY, STATUS_BUSY]:
                with self.lock:
                    if sender in self.clients:
                        self.clients[sender].status = new_status
                self.send_to_user(sender, f"OK|Status changed to {new_status}\n")
                self.broadcast_system(f"'{sender}' is now {new_status}")
                self.broadcast_userlist()
        
        elif upper_msg.startswith("TO:"):
            parts = message.split(":", 2)
            if len(parts) >= 3:
                target = parts[1].strip()
                pm_content = parts[2].strip()
                self.send_private(sender, target, pm_content)
        
        else:
            self.broadcast_message(sender, message)
    
    def send_to_user(self, username: str, message: str) -> bool:
        with self.lock:
            if username not in self.clients:
                return False
            conn = self.clients[username]
        
        try:
            data = message.encode() if isinstance(message, str) else message
            conn.send(data)
            self.stats['bytes_sent'] += len(data)
            return True
        except Exception:
            return False
    
    def send_private(self, sender: str, target: str, message: str):
        with self.lock:
            if target not in self.clients:
                self.send_to_user(sender, f"ERROR|User '{target}' not found\n")
                return
        
        self.send_to_user(target, f"MSG|[Private from {sender}]: {message}\n")
        self.send_to_user(sender, f"SENT|[Private to {target}]: {message}\n")
        
        self.root.after(0, lambda: 
            self.log(f"[DM] {sender} → {target}: {message}", 'admin'))
    
    def broadcast_message(self, sender: str, message: str):
        with self.lock:
            clients_copy = dict(self.clients)
        
        for username, conn in clients_copy.items():
            try:
                if username == sender:
                    conn.send(f"SENT|[You]: {message}\n".encode())
                else:
                    conn.send(f"MSG|[{sender}]: {message}\n".encode())
                conn.messages_sent += 1
            except Exception:
                pass
    
    def broadcast_system(self, message: str, exclude: str = None):
        with self.lock:
            clients_copy = dict(self.clients)
        
        for username, conn in clients_copy.items():
            if username != exclude:
                try:
                    conn.send(f"SYSTEM|{message}\n".encode())
                except Exception:
                    pass
    
    def broadcast_userlist(self):
        with self.lock:
            users = list(self.clients.keys())
            statuses = {u: c.status for u, c in self.clients.items()}
            clients_copy = dict(self.clients)
        
        user_str = ", ".join(f"{u}({statuses[u]})" for u in users)
        
        for conn in clients_copy.values():
            try:
                conn.send(f"USERS|Online: {user_str}\n".encode())
            except Exception:
                pass
    
    def kick_selected_user(self):
        selection = self.users_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to kick")
            return
        
        item = self.users_list.get(selection[0])
        username = item.split()[1]
        
        if messagebox.askyesno("Confirm Kick", f"Kick user '{username}'?"):
            self.kick_user(username, "Kicked by server admin")
    
    def kick_user(self, username: str, reason: str = "Kicked by admin"):
        with self.lock:
            if username not in self.clients:
                self.log(f"User '{username}' not found", 'warning')
                return
            conn = self.clients[username]
        
        try:
            conn.send(f"KICK|{reason}\n".encode())
            conn.socket.close()
        except Exception:
            pass
        
        self.log(f"Kicked '{username}': {reason}", 'admin')
    
    def send_broadcast(self):
        message = self.broadcast_entry.get().strip()
        if not message:
            return
        
        self.broadcast_entry.delete(0, 'end')
        self.broadcast_system(f"📢 ADMIN: {message}")
        self.log(f"[BROADCAST] {message}", 'admin')
                
    def on_close(self):
        if self.running:
            if messagebox.askyesno("Confirm Exit", "Server is running. Stop and exit?"):
                self.stop_server()
            else:
                return
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# CLIENT
# ═══════════════════════════════════════════════════════════════

class CyberClient:
    """Enhanced Chat Client with Modern Features."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💬 CYBER CHAT")
        self.root.geometry("900x650")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.minsize(700, 500)
        
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.username: Optional[str] = None
        self.running = True
        self.my_status = STATUS_ONLINE
        
        self.history: Optional[ChatHistory] = None
        self.online_users = {}
        
        self.show_login()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.configure(bg=COLORS['bg_dark'])
        
        # Center card
        card = tk.Frame(self.root, bg=COLORS['bg_card'], padx=50, pady=40)
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(card, text="⚡ CYBER CHAT ⚡", font=FONTS['title'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack(pady=(0, 5))
        
        tk.Label(card, text="TCP/IP Network Project", font=FONTS['small'],
                fg=COLORS['text_secondary'], bg=COLORS['bg_card']).pack()
        
        tk.Label(card, text="by Adir Buskila & Liav Wizman", font=FONTS['small'],
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(pady=(5, 30))
        
        tk.Frame(card, bg=COLORS['accent_cyan'], height=2).pack(fill='x', pady=15)
        
        # Server input
        tk.Label(card, text="SERVER ADDRESS", font=FONTS['small_bold'],
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(anchor='w', pady=(15, 5))
        
        self.server_entry = tk.Entry(card, font=FONTS['body'], width=30,
                                     bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                     insertbackground=COLORS['accent_cyan'], relief='flat')
        self.server_entry.insert(0, f"{HOST}:{PORT}")
        self.server_entry.pack(fill='x', ipady=10)
        
        # Username input
        tk.Label(card, text="YOUR USERNAME", font=FONTS['small_bold'],
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(anchor='w', pady=(20, 5))
        
        self.user_entry = tk.Entry(card, font=FONTS['body'], width=30,
                                   bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                   insertbackground=COLORS['accent_cyan'], relief='flat')
        self.user_entry.pack(fill='x', ipady=10)
        self.user_entry.bind('<Return>', lambda e: self.connect())
        self.user_entry.focus()
        
        # Connect button
        self.connect_btn = tk.Button(card, text="⚡ CONNECT ⚡", font=FONTS['body_bold'],
                                     bg=COLORS['accent_cyan'], fg=COLORS['bg_dark'],
                                     relief='flat', cursor='hand2', command=self.connect)
        self.connect_btn.pack(pady=25, ipadx=30, ipady=10)
        
        # Status label
        self.status_label = tk.Label(card, text="", font=FONTS['small'],
                                     fg=COLORS['text_dim'], bg=COLORS['bg_card'])
        self.status_label.pack()
        
        # Help text
        help_frame = tk.Frame(card, bg=COLORS['bg_card'])
        help_frame.pack(pady=20)
        tk.Label(help_frame, text="💡 ", font=FONTS['tiny'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack(side='left')
        tk.Label(help_frame, text="Make sure the server is running first!",
                font=FONTS['tiny'], fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(side='left')
    
    def show_chat(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.root, bg=COLORS['bg_medium'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=COLORS['bg_medium'])
        header_content.pack(fill='both', expand=True, padx=15, pady=10)
        
        tk.Label(header_content, text="⚡ CYBER CHAT", font=FONTS['subheader'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_medium']).pack(side='left')
        
        # Right side
        right_header = tk.Frame(header_content, bg=COLORS['bg_medium'])
        right_header.pack(side='right')
        
        tk.Label(right_header, text=f"👤 {self.username}", font=FONTS['body_bold'],
                fg=COLORS['accent_green'], bg=COLORS['bg_medium']).pack(side='left', padx=10)
        
        # Status button
        self.status_btn = tk.Button(right_header, text="● Online", font=FONTS['tiny'],
                                    bg=COLORS['status_online'], fg=COLORS['bg_dark'],
                                    relief='flat', cursor='hand2', command=self.cycle_status)
        self.status_btn.pack(side='left', padx=5)
        
        tk.Button(right_header, text="✕ Leave", font=FONTS['small_bold'],
                 bg=COLORS['accent_red'], fg=COLORS['text_primary'],
                 relief='flat', cursor='hand2', command=self.disconnect).pack(side='left', padx=5)
        
        tk.Frame(self.root, bg=COLORS['accent_cyan'], height=2).pack(fill='x')
        
        # Main content
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel (Users)
        left = tk.Frame(main, bg=COLORS['bg_card'], width=180)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        
        users_header = tk.Frame(left, bg=COLORS['bg_card'])
        users_header.pack(fill='x', padx=10, pady=10)
        
        tk.Label(users_header, text="👥 ONLINE", font=FONTS['body_bold'],
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(side='left')
        
        self.users_count_label = tk.Label(users_header, text="(0)", font=FONTS['small'],
                                          fg=COLORS['text_dim'], bg=COLORS['bg_card'])
        self.users_count_label.pack(side='left', padx=5)
        
        # Users list
        users_container = tk.Frame(left, bg=COLORS['bg_card'])
        users_container.pack(fill='both', expand=True, padx=5)
        
        self.users_canvas = tk.Canvas(users_container, bg=COLORS['bg_card'], highlightthickness=0)
        users_scrollbar = tk.Scrollbar(users_container, orient='vertical', command=self.users_canvas.yview)
        self.users_frame = tk.Frame(self.users_canvas, bg=COLORS['bg_card'])
        
        self.users_canvas.configure(yscrollcommand=users_scrollbar.set)
        users_scrollbar.pack(side='right', fill='y')
        self.users_canvas.pack(side='left', fill='both', expand=True)
        
        self.users_window = self.users_canvas.create_window((0, 0), window=self.users_frame, anchor='nw')
        
        self.users_frame.bind('<Configure>',
            lambda e: self.users_canvas.configure(scrollregion=self.users_canvas.bbox('all')))
        self.users_canvas.bind('<Configure>',
            lambda e: self.users_canvas.itemconfig(self.users_window, width=e.width))
        
        # Buttons
        btn_frame = tk.Frame(left, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(btn_frame, text="🔄 Refresh", font=FONTS['tiny'],
                 bg=COLORS['bg_light'], fg=COLORS['text_secondary'],
                 relief='flat', cursor='hand2', command=lambda: self.send("LIST")).pack(fill='x', pady=2)
        
        tk.Button(btn_frame, text="📥 Save Chat", font=FONTS['tiny'],
                 bg=COLORS['bg_light'], fg=COLORS['text_secondary'],
                 relief='flat', cursor='hand2', command=self.save_chat).pack(fill='x', pady=2)
        
        # Right panel (Chat)
        right = tk.Frame(main, bg=COLORS['bg_card'])
        right.pack(side='right', fill='both', expand=True)
        
        # Messages area
        messages_container = tk.Frame(right, bg=COLORS['bg_medium'])
        messages_container.pack(fill='both', expand=True)
        
        self.chat_canvas = tk.Canvas(messages_container, bg=COLORS['bg_medium'], highlightthickness=0)
        chat_scrollbar = tk.Scrollbar(messages_container, orient='vertical', command=self.chat_canvas.yview)
        self.messages_frame = tk.Frame(self.chat_canvas, bg=COLORS['bg_medium'])
        
        self.chat_canvas.configure(yscrollcommand=chat_scrollbar.set)
        chat_scrollbar.pack(side='right', fill='y')
        self.chat_canvas.pack(side='left', fill='both', expand=True)
        
        self.chat_window = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor='nw')
        
        self.messages_frame.bind('<Configure>',
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox('all')))
        self.chat_canvas.bind('<Configure>',
            lambda e: self.chat_canvas.itemconfig(self.chat_window, width=e.width))
        
        # Input area
        input_container = tk.Frame(right, bg=COLORS['bg_light'], height=60)
        input_container.pack(fill='x', side='bottom')
        input_container.pack_propagate(False)
        
        input_inner = tk.Frame(input_container, bg=COLORS['bg_light'])
        input_inner.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Emoji button
        self.emoji_btn = tk.Button(input_inner, text="😊", font=FONTS['body'],
                                   bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                                   relief='flat', cursor='hand2', command=self.show_emoji_picker)
        self.emoji_btn.pack(side='left', padx=(0, 5))
        
        # Message input
        self.msg_entry = tk.Entry(input_inner, font=FONTS['body'],
                                  bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                                  insertbackground=COLORS['accent_cyan'], relief='flat')
        self.msg_entry.pack(side='left', fill='both', expand=True, padx=5, ipady=8)
        self.msg_entry.bind('<Return>', lambda e: self.send_chat())
        self.msg_entry.focus()
        
        # Send button
        tk.Button(input_inner, text="SEND ➤", font=FONTS['small_bold'],
                 bg=COLORS['accent_green'], fg=COLORS['bg_dark'],
                 relief='flat', cursor='hand2', command=self.send_chat).pack(side='right')
        
        # Welcome message
        self.add_system("🚀 Welcome to Cyber Chat! Type a message or click a user to DM.")
        self.add_system("💡 Commands: /help, /status <online|away|busy>, /dm <user> <msg>, /clear, /save")
        
        # Request user list
        self.root.after(300, lambda: self.send("LIST"))
    
    def connect(self):
        server_str = self.server_entry.get().strip()
        host, port = parse_address(server_str)
        
        username = self.user_entry.get().strip()
        valid, error = validate_username(username)
        if not valid:
            self.status_label.configure(text=f"⚠️ {error}", fg=COLORS['accent_red'])
            return
        
        self.status_label.configure(text="Connecting...", fg=COLORS['accent_orange'])
        self.connect_btn.configure(state='disabled')
        self.root.update()
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((host, port))
            self.socket.settimeout(None)
            
            self.connected = True
            self.username = username
            
            self.history = ChatHistory(username)
            
            threading.Thread(target=self.receive_loop, daemon=True).start()
            
            time.sleep(0.2)
            self.socket.send(username.encode())
            time.sleep(0.2)
            
            self.show_chat()
            
        except ConnectionRefusedError:
            self.status_label.configure(text="❌ Connection refused! Is the server running?",
                                       fg=COLORS['accent_red'])
            self.connect_btn.configure(state='normal')
            
        except socket.timeout:
            self.status_label.configure(text="❌ Connection timed out!", fg=COLORS['accent_red'])
            self.connect_btn.configure(state='normal')
            
        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {str(e)}", fg=COLORS['accent_red'])
            self.connect_btn.configure(state='normal')
    
    def disconnect(self):
        if self.connected:
            try:
                self.send("QUIT")
            except Exception:
                pass
            
            self.connected = False
            
            if self.socket:
                try:
                    self.socket.close()
                except Exception:
                    pass
        
        self.show_login()
    
    def send(self, message: str):
        if self.connected and message:
            try:
                self.socket.send(message.encode())
            except Exception:
                pass
    
    def send_chat(self):
        message = self.msg_entry.get().strip()
        if not message:
            return
        
        self.msg_entry.delete(0, 'end')
        message = replace_emoji_shortcuts(message)
        
        command, args = parse_command(message)
        
        if command:
            self.handle_command(command, args)
        else:
            valid, error = validate_message(message)
            if not valid:
                self.add_system(f"❌ {error}")
                return
            
            self.send(message)
    
    def handle_command(self, command: str, args: str):
        if command == 'help':
            self.add_system("📖 Available commands:")
            self.add_system("  /status <online|away|busy> - Change your status")
            self.add_system("  /dm <user> <message> - Send private message")
            self.add_system("  /clear - Clear chat window")
            self.add_system("  /save - Save chat history")
            
        elif command == 'status':
            status = args.lower()
            if status in [STATUS_ONLINE, STATUS_AWAY, STATUS_BUSY]:
                self.send(f"STATUS:{status}")
                self.my_status = status
                self.update_status_button()
            else:
                self.add_system("❌ Invalid status. Use: online, away, or busy")
                
        elif command == 'dm':
            parts = args.split(' ', 1)
            if len(parts) >= 2:
                target, msg = parts
                self.send(f"TO:{target}:{msg}")
            else:
                self.add_system("❌ Usage: /dm <username> <message>")
                
        elif command == 'clear':
            self.clear_chat()
            
        elif command == 'save':
            self.save_chat()
            
        else:
            self.add_system(f"❌ Unknown command: /{command}")
    
    def receive_loop(self):
        while self.connected and self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                messages = data.decode().strip().split('\n')
                for msg in messages:
                    if '|' in msg:
                        msg_type, content = msg.split('|', 1)
                        self.root.after(0, lambda t=msg_type, c=content: 
                            self.process_message(t, c))
                            
            except Exception:
                break
        
        self.root.after(0, self.on_disconnect)
    
    def process_message(self, msg_type: str, content: str):
        if msg_type == "MSG":
            if content.startswith("[Private from"):
                parts = content.split("]: ", 1)
                sender = parts[0].replace("[Private from ", "")
                message = parts[1] if len(parts) > 1 else ""
                self.add_message(sender, message, 'private_recv')
                if self.history:
                    self.history.add_message(sender, message, 'private', self.username)
                play_notification_sound()
            elif content.startswith("["):
                parts = content.split("]: ", 1)
                sender = parts[0].replace("[", "")
                message = parts[1] if len(parts) > 1 else ""
                self.add_message(sender, message, 'recv')
                if self.history:
                    self.history.add_message(sender, message)
                
        elif msg_type == "SENT":
            if content.startswith("[Private to"):
                parts = content.split("]: ", 1)
                target = parts[0].replace("[Private to ", "")
                message = parts[1] if len(parts) > 1 else ""
                self.add_message(target, message, 'private_sent')
                if self.history:
                    self.history.add_message(self.username, message, 'private', target)
            elif content.startswith("[You]:"):
                message = content.replace("[You]: ", "")
                self.add_message(self.username, message, 'sent')
                if self.history:
                    self.history.add_message(self.username, message)
                
        elif msg_type == "SYSTEM":
            self.add_system(content)
            if self.history:
                self.history.add_message("SYSTEM", content, 'system')
            
        elif msg_type == "USERS":
            self.update_users(content)
            
        elif msg_type == "ERROR":
            self.add_system(f"❌ {content}")
            
        elif msg_type == "KICK":
            messagebox.showerror("Kicked", f"You were kicked: {content}")
            self.disconnect()
    
    def add_message(self, sender: str, message: str, msg_type: str = 'recv'):
        frame = tk.Frame(self.messages_frame, bg=COLORS['bg_medium'])
        frame.pack(fill='x', pady=4, padx=8)
        
        timestamp = datetime.now().strftime("%H:%M")
        
        if msg_type == 'sent':
            container = tk.Frame(frame, bg=COLORS['bg_medium'])
            container.pack(fill='x')
            
            time_lbl = tk.Label(container, text=timestamp, font=FONTS['tiny'],
                               fg=COLORS['text_dim'], bg=COLORS['bg_medium'])
            time_lbl.pack(side='right', padx=(5, 0))
            
            bubble = tk.Frame(container, bg=COLORS['accent_cyan'])
            bubble.pack(side='right')
            
            inner = tk.Frame(bubble, bg=COLORS['bg_light'], padx=12, pady=8)
            inner.pack(padx=2, pady=2)
            
            tk.Label(inner, text=message, font=FONTS['message'],
                    fg=COLORS['text_primary'], bg=COLORS['bg_light'],
                    wraplength=300, justify='left').pack()
            
        elif msg_type == 'recv':
            tk.Label(frame, text=f"👤 {sender} · {timestamp}", font=FONTS['tiny'],
                    fg=COLORS['accent_pink'], bg=COLORS['bg_medium']).pack(anchor='w')
            
            bubble = tk.Frame(frame, bg=COLORS['accent_purple'])
            bubble.pack(side='left')
            
            inner = tk.Frame(bubble, bg=COLORS['bg_card'], padx=12, pady=8)
            inner.pack(padx=2, pady=2)
            
            tk.Label(inner, text=message, font=FONTS['message'],
                    fg=COLORS['text_primary'], bg=COLORS['bg_card'],
                    wraplength=300, justify='left').pack()
            
        elif msg_type == 'private_sent':
            tk.Label(frame, text=f"🔒 To {sender} · {timestamp}", font=FONTS['tiny'],
                    fg=COLORS['accent_purple'], bg=COLORS['bg_medium']).pack(anchor='e')
            
            bubble = tk.Frame(frame, bg=COLORS['accent_purple'])
            bubble.pack(side='right')
            
            inner = tk.Frame(bubble, bg=COLORS['bg_light'], padx=12, pady=8)
            inner.pack(padx=2, pady=2)
            
            tk.Label(inner, text=message, font=FONTS['message'],
                    fg=COLORS['text_primary'], bg=COLORS['bg_light'],
                    wraplength=300, justify='left').pack()
            
        elif msg_type == 'private_recv':
            tk.Label(frame, text=f"🔒 From {sender} · {timestamp}", font=FONTS['tiny'],
                    fg=COLORS['accent_pink'], bg=COLORS['bg_medium']).pack(anchor='w')
            
            bubble = tk.Frame(frame, bg=COLORS['accent_pink'])
            bubble.pack(side='left')
            
            inner = tk.Frame(bubble, bg=COLORS['bg_card'], padx=12, pady=8)
            inner.pack(padx=2, pady=2)
            
            tk.Label(inner, text=message, font=FONTS['message'],
                    fg=COLORS['text_primary'], bg=COLORS['bg_card'],
                    wraplength=300, justify='left').pack()
        
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
    
    def add_system(self, message: str):
        frame = tk.Frame(self.messages_frame, bg=COLORS['bg_medium'])
        frame.pack(fill='x', pady=2, padx=8)
        
        tk.Label(frame, text=f"⚡ {message}", font=FONTS['small'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_medium']).pack()
        
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
    
    def update_users(self, users_str: str):
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        users_part = users_str.replace("Online:", "").strip()
        if not users_part:
            return
        
        users = []
        for user_entry in users_part.split(","):
            user_entry = user_entry.strip()
            if not user_entry:
                continue
            
            if "(" in user_entry:
                username = user_entry.split("(")[0].strip()
                status = user_entry.split("(")[1].rstrip(")").strip()
            else:
                username = user_entry
                status = STATUS_ONLINE
            
            users.append((username, status))
            self.online_users[username] = status
        
        self.users_count_label.configure(text=f"({len(users)})")
        
        status_colors = {
            'online': COLORS['status_online'],
            'away': COLORS['status_away'],
            'busy': COLORS['status_busy'],
        }
        
        for username, status in users:
            is_self = username == self.username
            status_color = status_colors.get(status, COLORS['status_offline'])
            text_color = COLORS['accent_green'] if is_self else COLORS['text_secondary']
            
            item = tk.Frame(self.users_frame, bg=COLORS['bg_card'])
            item.pack(fill='x', pady=1)
            
            tk.Label(item, text="●", font=FONTS['small'],
                    fg=status_color, bg=COLORS['bg_card']).pack(side='left', padx=(5, 3))
            
            name_lbl = tk.Label(item, text=username, font=FONTS['small'],
                               fg=text_color, bg=COLORS['bg_card'])
            name_lbl.pack(side='left')
            
            if is_self:
                tk.Label(item, text="(you)", font=FONTS['tiny'],
                        fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(side='left', padx=3)
            else:
                # Make clickable for DM
                item.configure(cursor='hand2')
                item.bind('<Button-1>', lambda e, u=username: self.open_dm_dialog(u))
                name_lbl.bind('<Button-1>', lambda e, u=username: self.open_dm_dialog(u))
                
                def on_enter(e, i=item, n=name_lbl):
                    i.configure(bg=COLORS['bg_hover'])
                    n.configure(bg=COLORS['bg_hover'], fg=COLORS['accent_pink'])
                def on_leave(e, i=item, n=name_lbl):
                    i.configure(bg=COLORS['bg_card'])
                    n.configure(bg=COLORS['bg_card'], fg=COLORS['text_secondary'])
                
                item.bind('<Enter>', on_enter)
                item.bind('<Leave>', on_leave)
    
    def open_dm_dialog(self, username: str):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"DM to {username}")
        dialog.geometry("400x150")
        dialog.configure(bg=COLORS['bg_card'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center on parent
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, bg=COLORS['bg_card'], padx=20, pady=15)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text=f"🔒 Private message to {username}", font=FONTS['body_bold'],
                fg=COLORS['accent_purple'], bg=COLORS['bg_card']).pack(pady=(0, 15))
        
        entry = tk.Entry(frame, font=FONTS['body'], width=35,
                        bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                        insertbackground=COLORS['accent_cyan'], relief='flat')
        entry.pack(ipady=8)
        entry.focus()
        
        def send_dm():
            msg = entry.get().strip()
            if msg:
                self.send(f"TO:{username}:{msg}")
                dialog.destroy()
        
        entry.bind('<Return>', lambda e: send_dm())
        
        tk.Button(frame, text="SEND", font=FONTS['small_bold'],
                 bg=COLORS['accent_purple'], fg=COLORS['text_primary'],
                 relief='flat', cursor='hand2', command=send_dm).pack(pady=15)
    
    def show_emoji_picker(self):
        picker = tk.Toplevel(self.root)
        picker.title("Emoji")
        picker.geometry("280x180")
        picker.configure(bg=COLORS['bg_card'])
        picker.transient(self.root)
        picker.overrideredirect(True)
        
        x = self.emoji_btn.winfo_rootx() + self.emoji_btn.winfo_width()
        y = self.emoji_btn.winfo_rooty()
        picker.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(picker, bg=COLORS['bg_card'], padx=5, pady=5)
        frame.pack(fill='both', expand=True)
        
        def select_emoji(emoji):
            self.msg_entry.insert('end', emoji)
            self.msg_entry.focus()
            picker.destroy()
        
        for i, emoji in enumerate(EMOJIS):
            btn = tk.Button(frame, text=emoji, font=('Segoe UI Emoji', 14),
                           bg=COLORS['bg_light'], relief='flat', cursor='hand2', width=2,
                           command=lambda e=emoji: select_emoji(e))
            btn.grid(row=i // 8, column=i % 8, padx=1, pady=1)
        
        picker.bind('<FocusOut>', lambda e: picker.destroy())
    
    def cycle_status(self):
        statuses = [STATUS_ONLINE, STATUS_AWAY, STATUS_BUSY]
        current_idx = statuses.index(self.my_status) if self.my_status in statuses else 0
        new_status = statuses[(current_idx + 1) % len(statuses)]
        
        self.send(f"STATUS:{new_status}")
        self.my_status = new_status
        self.update_status_button()
    
    def update_status_button(self):
        status_config = {
            STATUS_ONLINE: ("● Online", COLORS['status_online']),
            STATUS_AWAY: ("● Away", COLORS['status_away']),
            STATUS_BUSY: ("● Busy", COLORS['status_busy'])
        }
        text, color = status_config.get(self.my_status, ("● Online", COLORS['status_online']))
        self.status_btn.configure(text=text, bg=color)
    
    def clear_chat(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self.add_system("Chat cleared.")
    
    def save_chat(self):
        if self.history:
            try:
                filename = self.history.export_txt()
                self.add_system(f"💾 Chat saved to: {filename}")
            except Exception as e:
                self.add_system(f"❌ Failed to save: {e}")
    
    def on_disconnect(self):
        if self.connected:
            self.connected = False
            messagebox.showwarning("Disconnected", "Lost connection to server")
            self.show_login()
    
    def on_close(self):
        self.running = False
        if self.connected:
            try:
                self.send("QUIT")
            except Exception:
                pass
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Main entry point with command-line argument support."""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'server':
            print("⚡ Starting CYBER CHAT Server...")
            server = CyberServer()
            server.run()
            
        elif mode == 'client':
            print("⚡ Starting CYBER CHAT Client...")
            client = CyberClient()
            client.run()
            
        elif mode in ['--help', '-h', 'help']:
            print("""
╔═══════════════════════════════════════════════════════════╗
║              ⚡ CYBER CHAT - Help                          ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Usage:                                                   ║
║    python cyber_chat.py           Launch GUI chooser      ║
║    python cyber_chat.py server    Start server directly   ║
║    python cyber_chat.py client    Start client directly   ║
║    python cyber_chat.py --help    Show this help          ║
║                                                           ║
║  This is the single-file backup version with ALL features.║
║  For the modular version, use: python main.py             ║
║                                                           ║
║  Project by: Adir Buskila & Liav Wizman                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
            """)
            
        else:
            print(f"❌ Unknown mode: {mode}")
            print("   Use: server, client, or --help")
            
    else:
        # No arguments - show launcher GUI
        launcher = CyberLauncher()
        launcher.run()


if __name__ == "__main__":
    main()
