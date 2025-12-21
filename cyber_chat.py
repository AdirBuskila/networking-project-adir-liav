"""
⚡ CYBER CHAT - Complete Chat Application
TCP/IP Network Project
Students: Adir Buskila & Liav Wizman

Run this file and choose: SERVER or CLIENT
"""

import socket
import threading
import tkinter as tk
from tkinter import ttk, font, scrolledtext, messagebox
from datetime import datetime
import time
import random
import sys

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

HOST = '127.0.0.1'
PORT = 12345
MAX_CLIENTS = 10

# 🎨 CYBERPUNK COLOR SCHEME
COLORS = {
    'bg_dark': '#0a0a0f',
    'bg_medium': '#12121a', 
    'bg_light': '#1a1a2e',
    'bg_card': '#16213e',
    'accent_cyan': '#00fff5',
    'accent_pink': '#ff00ff',
    'accent_purple': '#7b2cbf',
    'accent_blue': '#0077ff',
    'accent_green': '#00ff88',
    'accent_orange': '#ff6600',
    'accent_red': '#ff3366',
    'text_primary': '#ffffff',
    'text_secondary': '#8892b0',
    'text_dim': '#495670',
    'border': '#233554',
}

# ═══════════════════════════════════════════════════════════════
# LAUNCHER - Choose Server or Client
# ═══════════════════════════════════════════════════════════════

class CyberLauncher:
    """Main launcher to choose between Server and Client."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚡ CYBER CHAT")
        self.root.geometry("500x400")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="⚡ CYBER CHAT ⚡",
                        font=('Consolas', 32, 'bold'),
                        fg=COLORS['accent_cyan'], bg=COLORS['bg_dark'])
        title.pack(pady=(50, 10))
        
        subtitle = tk.Label(self.root, text="TCP/IP Network Project",
                           font=('Consolas', 12),
                           fg=COLORS['text_secondary'], bg=COLORS['bg_dark'])
        subtitle.pack()
        
        authors = tk.Label(self.root, text="by Adir Buskila & Liav Wizman",
                          font=('Consolas', 10),
                          fg=COLORS['accent_pink'], bg=COLORS['bg_dark'])
        authors.pack(pady=(5, 40))
        
        # Buttons frame
        btn_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=20)
        
        # Server button
        server_btn = tk.Button(btn_frame, text="🖥️ START SERVER",
                              font=('Consolas', 14, 'bold'),
                              bg=COLORS['accent_green'], fg=COLORS['bg_dark'],
                              activebackground=COLORS['accent_cyan'],
                              width=20, height=2, relief='flat',
                              cursor='hand2', command=self.start_server)
        server_btn.pack(pady=10)
        
        # Client button  
        client_btn = tk.Button(btn_frame, text="💬 JOIN AS CLIENT",
                              font=('Consolas', 14, 'bold'),
                              bg=COLORS['accent_purple'], fg=COLORS['text_primary'],
                              activebackground=COLORS['accent_pink'],
                              width=20, height=2, relief='flat',
                              cursor='hand2', command=self.start_client)
        client_btn.pack(pady=10)
        
        # Info
        info = tk.Label(self.root, text="Start SERVER first, then open CLIENT(s)",
                       font=('Consolas', 9),
                       fg=COLORS['text_dim'], bg=COLORS['bg_dark'])
        info.pack(pady=30)
        
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
    """Chat Server with Dashboard."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🖥️ CYBER CHAT SERVER")
        self.root.geometry("900x600")
        self.root.configure(bg=COLORS['bg_dark'])
        
        self.server_socket = None
        self.clients = {}
        self.lock = threading.Lock()
        self.running = False
        self.start_time = None
        self.stats = {'messages': 0, 'bytes_sent': 0, 'bytes_recv': 0}
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS['bg_medium'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=COLORS['bg_medium'])
        header_content.pack(fill='both', expand=True, padx=20, pady=12)
        
        tk.Label(header_content, text="🖥️ CYBER CHAT SERVER",
                font=('Consolas', 22, 'bold'),
                fg=COLORS['accent_cyan'], bg=COLORS['bg_medium']).pack(side='left')
        
        # Status
        self.status_frame = tk.Frame(header_content, bg=COLORS['bg_medium'])
        self.status_frame.pack(side='right')
        
        self.status_dot = tk.Label(self.status_frame, text="●", font=('Consolas', 20),
                                   fg=COLORS['accent_red'], bg=COLORS['bg_medium'])
        self.status_dot.pack(side='left')
        
        self.status_text = tk.Label(self.status_frame, text="OFFLINE",
                                    font=('Consolas', 12, 'bold'),
                                    fg=COLORS['accent_red'], bg=COLORS['bg_medium'])
        self.status_text.pack(side='left', padx=5)
        
        tk.Frame(self.root, bg=COLORS['accent_cyan'], height=2).pack(fill='x')
        
        # Main content
        content = tk.Frame(self.root, bg=COLORS['bg_dark'])
        content.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Left panel
        left = tk.Frame(content, bg=COLORS['bg_card'], width=250)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        
        # Controls
        ctrl = tk.Frame(left, bg=COLORS['bg_card'])
        ctrl.pack(fill='x', padx=15, pady=15)
        
        tk.Label(ctrl, text="⚡ CONTROLS", font=('Consolas', 11, 'bold'),
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack(anchor='w', pady=(0, 10))
        
        self.start_btn = tk.Button(ctrl, text="▶ START SERVER",
                                   font=('Consolas', 10, 'bold'),
                                   bg=COLORS['accent_green'], fg=COLORS['bg_dark'],
                                   relief='flat', cursor='hand2',
                                   command=self.start_server)
        self.start_btn.pack(fill='x', pady=3, ipady=6)
        
        self.stop_btn = tk.Button(ctrl, text="■ STOP SERVER",
                                  font=('Consolas', 10, 'bold'),
                                  bg=COLORS['accent_red'], fg=COLORS['text_primary'],
                                  relief='flat', cursor='hand2', state='disabled',
                                  command=self.stop_server)
        self.stop_btn.pack(fill='x', pady=3, ipady=6)
        
        tk.Frame(left, bg=COLORS['border'], height=1).pack(fill='x', padx=15, pady=10)
        
        # Stats
        stats_frame = tk.Frame(left, bg=COLORS['bg_card'])
        stats_frame.pack(fill='x', padx=15)
        
        tk.Label(stats_frame, text="📊 STATS", font=('Consolas', 11, 'bold'),
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(anchor='w', pady=(0, 8))
        
        self.clients_label = self.create_stat(stats_frame, "👥 Connected", "0")
        self.msgs_label = self.create_stat(stats_frame, "📨 Messages", "0")
        self.uptime_label = self.create_stat(stats_frame, "⏱️ Uptime", "00:00:00")
        
        tk.Frame(left, bg=COLORS['border'], height=1).pack(fill='x', padx=15, pady=10)
        
        # Users
        users_frame = tk.Frame(left, bg=COLORS['bg_card'])
        users_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        tk.Label(users_frame, text="👤 USERS", font=('Consolas', 11, 'bold'),
                fg=COLORS['accent_purple'], bg=COLORS['bg_card']).pack(anchor='w', pady=(0, 5))
        
        self.users_list = tk.Listbox(users_frame, font=('Consolas', 10),
                                     bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                     relief='flat', highlightthickness=0)
        self.users_list.pack(fill='both', expand=True)
        
        # Right panel - Logs
        right = tk.Frame(content, bg=COLORS['bg_card'])
        right.pack(side='right', fill='both', expand=True)
        
        tk.Label(right, text="📜 SERVER LOGS", font=('Consolas', 11, 'bold'),
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack(anchor='w', padx=15, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(right, font=('Consolas', 9),
                                                  bg=COLORS['bg_medium'],
                                                  fg=COLORS['text_primary'],
                                                  relief='flat')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        self.log_text.configure(state='disabled')
        
        for tag, color in [('info', COLORS['accent_cyan']), ('success', COLORS['accent_green']),
                           ('warning', COLORS['accent_orange']), ('error', COLORS['accent_red']),
                           ('msg', COLORS['accent_pink'])]:
            self.log_text.tag_configure(tag, foreground=color)
            
        self.log("Ready to start...", 'info')
        
    def create_stat(self, parent, label, default):
        frame = tk.Frame(parent, bg=COLORS['bg_light'])
        frame.pack(fill='x', pady=2)
        tk.Label(frame, text=label, font=('Consolas', 9),
                fg=COLORS['text_secondary'], bg=COLORS['bg_light']).pack(side='left', padx=8, pady=5)
        val = tk.Label(frame, text=default, font=('Consolas', 10, 'bold'),
                      fg=COLORS['accent_cyan'], bg=COLORS['bg_light'])
        val.pack(side='right', padx=8, pady=5)
        return val
        
    def log(self, msg, tag='info'):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"[{ts}] {msg}\n", tag)
        self.log_text.see('end')
        self.log_text.configure(state='disabled')
        
    def update_stats(self):
        if not self.running: return
        with self.lock:
            self.clients_label.configure(text=str(len(self.clients)))
        self.msgs_label.configure(text=str(self.stats['messages']))
        if self.start_time:
            up = int(time.time() - self.start_time)
            self.uptime_label.configure(text=f"{up//3600:02d}:{(up%3600)//60:02d}:{up%60:02d}")
        self.root.after(1000, self.update_stats)
        
    def update_users(self):
        self.users_list.delete(0, 'end')
        with self.lock:
            for u in self.clients: self.users_list.insert('end', f"  ● {u}")
                
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
            
            threading.Thread(target=self.accept_loop, daemon=True).start()
            self.update_stats()
        except Exception as e:
            self.log(f"Failed: {e}", 'error')
            
    def stop_server(self):
        self.running = False
        with self.lock:
            for u, (s, _) in self.clients.items():
                try: s.send("SYSTEM|Server shutting down\n".encode()); s.close()
                except: pass
            self.clients.clear()
        if self.server_socket:
            try: self.server_socket.close()
            except: pass
        self.status_dot.configure(fg=COLORS['accent_red'])
        self.status_text.configure(text="OFFLINE", fg=COLORS['accent_red'])
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        self.update_users()
        self.log("Server stopped", 'warning')
        
    def accept_loop(self):
        while self.running:
            try:
                cs, addr = self.server_socket.accept()
                self.root.after(0, lambda a=addr: self.log(f"Connection from {a}", 'info'))
                threading.Thread(target=self.handle_client, args=(cs, addr), daemon=True).start()
            except: break
                
    def handle_client(self, cs, addr):
        username = None
        try:
            cs.send("WELCOME|Username: ".encode())
            username = cs.recv(1024).decode().strip()
            if not username: cs.close(); return
            
            with self.lock:
                if username in self.clients:
                    cs.send(f"ERROR|'{username}' taken\n".encode()); cs.close(); return
                self.clients[username] = (cs, addr)
                
            self.root.after(0, lambda: self.log(f"'{username}' joined", 'success'))
            self.root.after(0, self.update_users)
            cs.send(f"OK|Welcome {username}!\n".encode())
            self.broadcast_sys(f"'{username}' joined", username)
            self.broadcast_userlist()  # Auto-refresh for all clients
            
            while self.running:
                data = cs.recv(4096)
                if not data: break
                msg = data.decode().strip()
                if not msg: continue
                
                self.stats['messages'] += 1
                self.root.after(0, lambda u=username, m=msg: self.log(f"[{u}] {m}", 'msg'))
                
                if msg.upper() == "QUIT": break
                elif msg.upper() == "LIST":
                    with self.lock: users = ", ".join(self.clients.keys())
                    cs.send(f"USERS|Online: {users}\n".encode())
                elif msg.upper().startswith("TO:"):
                    p = msg.split(":", 2)
                    if len(p) >= 3: self.send_private(username, p[1].strip(), p[2].strip())
                else:
                    self.broadcast_msg(username, msg)
        except: pass
        finally:
            with self.lock:
                if username and username in self.clients: del self.clients[username]
            if username:
                self.root.after(0, lambda: self.log(f"'{username}' left", 'warning'))
                self.broadcast_sys(f"'{username}' left")
                self.broadcast_userlist()  # Auto-refresh for all clients
            self.root.after(0, self.update_users)
            
    def send_private(self, sender, target, msg):
        with self.lock:
            if target not in self.clients:
                if sender in self.clients:
                    self.clients[sender][0].send(f"ERROR|'{target}' not found\n".encode())
                return
            ts, ss = self.clients[target][0], self.clients[sender][0]
        try:
            ts.send(f"MSG|[Private from {sender}]: {msg}\n".encode())
            ss.send(f"SENT|[Private to {target}]: {msg}\n".encode())
        except: pass
        
    def broadcast_msg(self, sender, msg):
        with self.lock: cc = dict(self.clients)
        for u, (s, _) in cc.items():
            try:
                if u == sender: s.send(f"SENT|[You]: {msg}\n".encode())
                else: s.send(f"MSG|[{sender}]: {msg}\n".encode())
            except: pass
            
    def broadcast_sys(self, msg, exclude=None):
        with self.lock: cc = dict(self.clients)
        for u, (s, _) in cc.items():
            if u != exclude:
                try: s.send(f"SYSTEM|{msg}\n".encode())
                except: pass
                
    def broadcast_userlist(self):
        """Send updated user list to all clients."""
        with self.lock:
            users = ", ".join(self.clients.keys())
            cc = dict(self.clients)
        for u, (s, _) in cc.items():
            try: s.send(f"USERS|Online: {users}\n".encode())
            except: pass
                
    def on_close(self):
        if self.running: self.stop_server()
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# CLIENT
# ═══════════════════════════════════════════════════════════════

class CyberClient:
    """Chat Client with GUI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💬 CYBER CHAT")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS['bg_dark'])
        
        self.socket = None
        self.connected = False
        self.username = None
        self.running = True
        
        self.show_login()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def show_login(self):
        for w in self.root.winfo_children(): w.destroy()
        
        # Center card
        card = tk.Frame(self.root, bg=COLORS['bg_card'], padx=40, pady=30)
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(card, text="⚡ CYBER CHAT ⚡", font=('Consolas', 28, 'bold'),
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack(pady=(0, 5))
        tk.Label(card, text="by Adir Buskila & Liav Wizman", font=('Consolas', 10),
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(pady=(0, 25))
        
        tk.Frame(card, bg=COLORS['accent_cyan'], height=2).pack(fill='x', pady=10)
        
        # Server input
        tk.Label(card, text="SERVER", font=('Consolas', 9, 'bold'),
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(anchor='w', pady=(10, 0))
        self.server_entry = tk.Entry(card, font=('Consolas', 12), width=25,
                                     bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                     insertbackground=COLORS['accent_cyan'], relief='flat')
        self.server_entry.insert(0, f"{HOST}:{PORT}")
        self.server_entry.pack(fill='x', pady=5, ipady=8)
        
        # Username input
        tk.Label(card, text="USERNAME", font=('Consolas', 9, 'bold'),
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(anchor='w', pady=(10, 0))
        self.user_entry = tk.Entry(card, font=('Consolas', 12), width=25,
                                   bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                   insertbackground=COLORS['accent_cyan'], relief='flat')
        self.user_entry.pack(fill='x', pady=5, ipady=8)
        self.user_entry.bind('<Return>', lambda e: self.connect())
        
        # Connect button
        self.connect_btn = tk.Button(card, text="⚡ CONNECT ⚡", font=('Consolas', 12, 'bold'),
                                     bg=COLORS['accent_cyan'], fg=COLORS['bg_dark'],
                                     relief='flat', cursor='hand2', command=self.connect)
        self.connect_btn.pack(pady=20, ipadx=20, ipady=8)
        
        self.status_label = tk.Label(card, text="", font=('Consolas', 10),
                                     fg=COLORS['text_dim'], bg=COLORS['bg_card'])
        self.status_label.pack()
        
    def show_chat(self):
        for w in self.root.winfo_children(): w.destroy()
        
        # Header
        header = tk.Frame(self.root, bg=COLORS['bg_medium'], height=55)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        hc = tk.Frame(header, bg=COLORS['bg_medium'])
        hc.pack(fill='both', expand=True, padx=15, pady=10)
        
        tk.Label(hc, text="⚡ CYBER CHAT", font=('Consolas', 16, 'bold'),
                fg=COLORS['accent_cyan'], bg=COLORS['bg_medium']).pack(side='left')
        
        tk.Label(hc, text=f"👤 {self.username}", font=('Consolas', 11, 'bold'),
                fg=COLORS['accent_green'], bg=COLORS['bg_medium']).pack(side='right', padx=10)
        
        tk.Button(hc, text="✕", font=('Consolas', 10, 'bold'),
                 bg=COLORS['accent_red'], fg=COLORS['text_primary'],
                 relief='flat', cursor='hand2', command=self.disconnect).pack(side='right')
        
        tk.Frame(self.root, bg=COLORS['accent_cyan'], height=2).pack(fill='x')
        
        # Main area
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Users panel
        left = tk.Frame(main, bg=COLORS['bg_card'], width=150)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        
        tk.Label(left, text="👥 ONLINE", font=('Consolas', 10, 'bold'),
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(pady=10)
        
        self.users_frame = tk.Frame(left, bg=COLORS['bg_card'])
        self.users_frame.pack(fill='both', expand=True, padx=5)
        
        tk.Button(left, text="🔄 Refresh", font=('Consolas', 9),
                 bg=COLORS['bg_light'], fg=COLORS['text_secondary'],
                 relief='flat', cursor='hand2',
                 command=lambda: self.send("LIST")).pack(pady=10)
        
        # Chat panel
        right = tk.Frame(main, bg=COLORS['bg_card'])
        right.pack(side='right', fill='both', expand=True)
        
        # Messages area
        self.chat_canvas = tk.Canvas(right, bg=COLORS['bg_medium'], highlightthickness=0)
        scrollbar = tk.Scrollbar(right, command=self.chat_canvas.yview)
        self.messages_frame = tk.Frame(self.chat_canvas, bg=COLORS['bg_medium'])
        
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.chat_canvas.pack(side='top', fill='both', expand=True)
        
        self.canvas_window = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor='nw')
        self.messages_frame.bind('<Configure>', lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox('all')))
        self.chat_canvas.bind('<Configure>', lambda e: self.chat_canvas.itemconfig(self.canvas_window, width=e.width))
        
        # Input area
        input_frame = tk.Frame(right, bg=COLORS['bg_light'], height=50)
        input_frame.pack(fill='x', side='bottom')
        input_frame.pack_propagate(False)
        
        ic = tk.Frame(input_frame, bg=COLORS['bg_light'])
        ic.pack(fill='both', expand=True, padx=10, pady=8)
        
        self.msg_entry = tk.Entry(ic, font=('Consolas', 11),
                                  bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                                  insertbackground=COLORS['accent_cyan'], relief='flat')
        self.msg_entry.pack(side='left', fill='both', expand=True, padx=(0, 10), ipady=5)
        self.msg_entry.bind('<Return>', lambda e: self.send_chat())
        
        tk.Button(ic, text="SEND ➤", font=('Consolas', 10, 'bold'),
                 bg=COLORS['accent_green'], fg=COLORS['bg_dark'],
                 relief='flat', cursor='hand2', command=self.send_chat).pack(side='right', ipadx=10)
        
        self.add_system("🚀 Connected! Type a message or click a user to DM.")
        self.root.after(300, lambda: self.send("LIST"))
        
    def add_message(self, sender, msg, type='recv'):
        frame = tk.Frame(self.messages_frame, bg=COLORS['bg_medium'])
        frame.pack(fill='x', pady=4, padx=8)
        
        if type == 'sent':
            bubble = tk.Frame(frame, bg=COLORS['accent_cyan'])
            bubble.pack(side='right')
            inner = tk.Frame(bubble, bg=COLORS['bg_light'], padx=10, pady=6)
            inner.pack(padx=1, pady=1)
            tk.Label(inner, text=msg, font=('Consolas', 10), fg=COLORS['text_primary'],
                    bg=COLORS['bg_light'], wraplength=300, justify='left').pack()
        elif type == 'recv':
            tk.Label(frame, text=f"👤 {sender}", font=('Consolas', 8, 'bold'),
                    fg=COLORS['accent_pink'], bg=COLORS['bg_medium']).pack(anchor='w')
            bubble = tk.Frame(frame, bg=COLORS['accent_purple'])
            bubble.pack(side='left')
            inner = tk.Frame(bubble, bg=COLORS['bg_card'], padx=10, pady=6)
            inner.pack(padx=1, pady=1)
            tk.Label(inner, text=msg, font=('Consolas', 10), fg=COLORS['text_primary'],
                    bg=COLORS['bg_card'], wraplength=300, justify='left').pack()
        elif type == 'private_sent':
            tk.Label(frame, text=f"🔒 To {sender}", font=('Consolas', 8),
                    fg=COLORS['accent_purple'], bg=COLORS['bg_medium']).pack(side='right')
            bubble = tk.Frame(frame, bg=COLORS['accent_purple'])
            bubble.pack(side='right', padx=(0, 5))
            inner = tk.Frame(bubble, bg=COLORS['bg_light'], padx=10, pady=6)
            inner.pack(padx=1, pady=1)
            tk.Label(inner, text=msg, font=('Consolas', 10), fg=COLORS['text_primary'],
                    bg=COLORS['bg_light'], wraplength=300).pack()
        elif type == 'private_recv':
            tk.Label(frame, text=f"🔒 From {sender}", font=('Consolas', 8, 'bold'),
                    fg=COLORS['accent_purple'], bg=COLORS['bg_medium']).pack(anchor='w')
            bubble = tk.Frame(frame, bg=COLORS['accent_pink'])
            bubble.pack(side='left')
            inner = tk.Frame(bubble, bg=COLORS['bg_card'], padx=10, pady=6)
            inner.pack(padx=1, pady=1)
            tk.Label(inner, text=msg, font=('Consolas', 10), fg=COLORS['text_primary'],
                    bg=COLORS['bg_card'], wraplength=300).pack()
                    
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
        
    def add_system(self, msg):
        frame = tk.Frame(self.messages_frame, bg=COLORS['bg_medium'])
        frame.pack(fill='x', pady=2, padx=8)
        tk.Label(frame, text=f"⚡ {msg}", font=('Consolas', 9),
                fg=COLORS['accent_cyan'], bg=COLORS['bg_medium']).pack()
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
        
    def update_users(self, users_str):
        for w in self.users_frame.winfo_children(): w.destroy()
        users = users_str.replace("Online:", "").strip().split(", ")
        for u in users:
            u = u.strip()
            if not u: continue
            color = COLORS['accent_green'] if u == self.username else COLORS['text_secondary']
            lbl = tk.Label(self.users_frame, text=f"● {u}", font=('Consolas', 9),
                          fg=color, bg=COLORS['bg_card'], cursor='hand2')
            lbl.pack(anchor='w', pady=1)
            if u != self.username:
                lbl.bind('<Button-1>', lambda e, user=u: self.open_dm(user))
                lbl.bind('<Enter>', lambda e, l=lbl: l.configure(fg=COLORS['accent_pink']))
                lbl.bind('<Leave>', lambda e, l=lbl: l.configure(fg=COLORS['text_secondary']))
                
    def open_dm(self, user):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"DM to {user}")
        dialog.geometry("350x120")
        dialog.configure(bg=COLORS['bg_card'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"🔒 Private message to {user}", font=('Consolas', 11, 'bold'),
                fg=COLORS['accent_purple'], bg=COLORS['bg_card']).pack(pady=12)
        
        entry = tk.Entry(dialog, font=('Consolas', 11), width=30,
                        bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                        insertbackground=COLORS['accent_cyan'], relief='flat')
        entry.pack(padx=15, ipady=6)
        entry.focus()
        
        def send_dm():
            m = entry.get().strip()
            if m: self.send(f"TO:{user}:{m}"); dialog.destroy()
        entry.bind('<Return>', lambda e: send_dm())
        
        tk.Button(dialog, text="SEND", font=('Consolas', 10, 'bold'),
                 bg=COLORS['accent_purple'], fg=COLORS['text_primary'],
                 relief='flat', cursor='hand2', command=send_dm).pack(pady=10)
        
    def connect(self):
        server = self.server_entry.get().strip()
        try: host, port = server.split(':'); port = int(port)
        except: host, port = HOST, PORT
        
        username = self.user_entry.get().strip()
        if not username:
            self.status_label.configure(text="⚠️ Enter username", fg=COLORS['accent_red'])
            return
            
        self.status_label.configure(text="Connecting...", fg=COLORS['accent_orange'])
        self.root.update()
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            self.username = username
            
            threading.Thread(target=self.receive_loop, daemon=True).start()
            time.sleep(0.2)
            self.socket.send(username.encode())
            time.sleep(0.2)
            
            self.show_chat()
        except ConnectionRefusedError:
            self.status_label.configure(text="❌ Server not running!", fg=COLORS['accent_red'])
        except Exception as e:
            self.status_label.configure(text=f"❌ {e}", fg=COLORS['accent_red'])
            
    def disconnect(self):
        if self.connected:
            try: self.send("QUIT")
            except: pass
            self.connected = False
            if self.socket: self.socket.close()
        self.show_login()
        
    def send(self, msg):
        if self.connected and msg:
            try: self.socket.send(msg.encode())
            except: pass
            
    def send_chat(self):
        msg = self.msg_entry.get().strip()
        if msg:
            self.send(msg)
            self.msg_entry.delete(0, 'end')
            
    def receive_loop(self):
        while self.connected and self.running:
            try:
                data = self.socket.recv(4096)
                if not data: break
                for line in data.decode().strip().split('\n'):
                    if '|' in line:
                        t, c = line.split('|', 1)
                        self.root.after(0, lambda type=t, content=c: self.process(type, content))
            except: break
        self.root.after(0, self.on_disconnect)
        
    def process(self, type, content):
        if type == "MSG":
            if content.startswith("[Private from"):
                p = content.split("]: ", 1)
                sender = p[0].replace("[Private from ", "")
                msg = p[1] if len(p) > 1 else ""
                self.add_message(sender, msg, 'private_recv')
            elif content.startswith("["):
                p = content.split("]: ", 1)
                sender = p[0].replace("[", "")
                msg = p[1] if len(p) > 1 else ""
                self.add_message(sender, msg, 'recv')
        elif type == "SENT":
            if content.startswith("[Private to"):
                p = content.split("]: ", 1)
                target = p[0].replace("[Private to ", "")
                msg = p[1] if len(p) > 1 else ""
                self.add_message(target, msg, 'private_sent')
            elif content.startswith("[You]:"):
                self.add_message("", content.replace("[You]: ", ""), 'sent')
        elif type == "SYSTEM":
            self.add_system(content)
        elif type == "USERS":
            self.update_users(content)
        elif type == "ERROR":
            self.add_system(f"❌ {content}")
            
    def on_disconnect(self):
        if self.connected:
            self.connected = False
            messagebox.showwarning("Disconnected", "Lost connection to server")
            self.show_login()
            
    def on_close(self):
        self.running = False
        if self.connected:
            try: self.send("QUIT")
            except: pass
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'server':
            CyberServer().run()
        elif sys.argv[1].lower() == 'client':
            CyberClient().run()
    else:
        CyberLauncher().run()

