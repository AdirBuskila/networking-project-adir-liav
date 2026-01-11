"""
⚡ CYBER CHAT - Server Module
Enhanced TCP Server with Admin Features
Students: Adir Buskila & Liav Weizman
"""

import socket
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from typing import Dict, Optional, Tuple

from config import (
    DEFAULT_HOST, DEFAULT_PORT, MAX_CLIENTS, BUFFER_SIZE,
    COLORS, FONTS, STATUS_ONLINE, STATUS_AWAY, STATUS_BUSY,
    ADMIN_PASSWORD, PING_INTERVAL
)
from utils import (
    ChatLogger, format_uptime, format_timestamp, 
    format_bytes, sanitize_username
)
from ui_components import (
    CyberButton, StatsCard, StatusIndicator, GradientHeader
)


# ═══════════════════════════════════════════════════════════════
# CLIENT CONNECTION CLASS
# ═══════════════════════════════════════════════════════════════

class ClientConnection:
    """Represents a connected client with metadata."""
    
    def __init__(self, socket: socket.socket, address: tuple, username: str):
        self.socket = socket
        self.address = address
        self.username = username
        self.status = STATUS_ONLINE
        self.connected_at = datetime.now()
        self.last_ping = time.time()
        self.ping_ms = 0
        self.messages_sent = 0
        self.bytes_sent = 0
        self.bytes_received = 0
    
    def send(self, data: bytes) -> bool:
        """Send data to client. Returns success status."""
        try:
            self.socket.send(data)
            self.bytes_sent += len(data)
            return True
        except Exception:
            return False
    
    def is_alive(self) -> bool:
        """Check if connection is still alive."""
        return time.time() - self.last_ping < PING_INTERVAL * 3


# ═══════════════════════════════════════════════════════════════
# CYBER SERVER
# ═══════════════════════════════════════════════════════════════

class CyberServer:
    """Enhanced Chat Server with Dashboard and Admin Features."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🖥️ CYBER CHAT SERVER")
        self.root.geometry("950x650")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.minsize(800, 500)
        
        # Server state
        self.server_socket: Optional[socket.socket] = None
        self.clients: Dict[str, ClientConnection] = {}
        self.lock = threading.Lock()
        self.running = False
        self.start_time: Optional[float] = None
        
        # Statistics
        self.stats = {
            'messages': 0,
            'bytes_sent': 0,
            'bytes_recv': 0,
            'peak_clients': 0,
            'total_connections': 0
        }
        
        # Logger
        self.logger = ChatLogger('CyberServer')
        
        # Setup UI
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    # ─────────────────────────────────────────────────────────────
    # UI SETUP
    # ─────────────────────────────────────────────────────────────
    
    def setup_ui(self):
        """Setup the server dashboard UI."""
        
        # ═══ HEADER ═══
        header = tk.Frame(self.root, bg=COLORS['bg_medium'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=COLORS['bg_medium'])
        header_content.pack(fill='both', expand=True, padx=20, pady=12)
        
        # Title
        title_frame = tk.Frame(header_content, bg=COLORS['bg_medium'])
        title_frame.pack(side='left')
        
        tk.Label(title_frame, text="🖥️ CYBER CHAT SERVER",
                font=FONTS['header'], fg=COLORS['accent_cyan'],
                bg=COLORS['bg_medium']).pack(side='left')
        
        tk.Label(title_frame, text="v2.0",
                font=FONTS['small'], fg=COLORS['text_dim'],
                bg=COLORS['bg_medium']).pack(side='left', padx=10)
        
        # Status indicator (right side)
        self.status_indicator = StatusIndicator(header_content, 'offline')
        self.status_indicator.pack(side='right')
        
        # Glow line
        tk.Frame(self.root, bg=COLORS['accent_cyan'], height=2).pack(fill='x')
        
        # ═══ MAIN CONTENT ═══
        content = tk.Frame(self.root, bg=COLORS['bg_dark'])
        content.pack(fill='both', expand=True, padx=15, pady=10)
        
        # ─── LEFT PANEL ───
        left = tk.Frame(content, bg=COLORS['bg_card'], width=280)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        
        # Controls Section
        ctrl_section = tk.Frame(left, bg=COLORS['bg_card'])
        ctrl_section.pack(fill='x', padx=15, pady=15)
        
        tk.Label(ctrl_section, text="⚡ CONTROLS",
                font=FONTS['body_bold'], fg=COLORS['accent_cyan'],
                bg=COLORS['bg_card']).pack(anchor='w', pady=(0, 12))
        
        # Server address display
        addr_frame = tk.Frame(ctrl_section, bg=COLORS['bg_light'])
        addr_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(addr_frame, text=f"📍 {DEFAULT_HOST}:{DEFAULT_PORT}",
                font=FONTS['small'], fg=COLORS['text_secondary'],
                bg=COLORS['bg_light']).pack(pady=5)
        
        # Start/Stop buttons
        self.start_btn = CyberButton(ctrl_section, "▶ START SERVER",
                                     command=self.start_server, color='accent_green')
        self.start_btn.pack(fill='x', pady=3, ipady=6)
        
        self.stop_btn = CyberButton(ctrl_section, "■ STOP SERVER",
                                    command=self.stop_server, color='accent_red')
        self.stop_btn.pack(fill='x', pady=3, ipady=6)
        self.stop_btn.configure(state='disabled')
        
        # Separator
        tk.Frame(left, bg=COLORS['border'], height=1).pack(fill='x', padx=15, pady=10)
        
        # Stats Section
        stats_section = tk.Frame(left, bg=COLORS['bg_card'])
        stats_section.pack(fill='x', padx=15)
        
        tk.Label(stats_section, text="📊 STATISTICS",
                font=FONTS['body_bold'], fg=COLORS['accent_pink'],
                bg=COLORS['bg_card']).pack(anchor='w', pady=(0, 10))
        
        # Stats cards
        self.stat_clients = StatsCard(stats_section, "👥", "Connected", "0")
        self.stat_clients.pack(fill='x', pady=2)
        
        self.stat_messages = StatsCard(stats_section, "📨", "Messages", "0")
        self.stat_messages.pack(fill='x', pady=2)
        
        self.stat_uptime = StatsCard(stats_section, "⏱️", "Uptime", "00:00:00")
        self.stat_uptime.pack(fill='x', pady=2)
        
        self.stat_peak = StatsCard(stats_section, "📈", "Peak Users", "0")
        self.stat_peak.pack(fill='x', pady=2)
        
        self.stat_data = StatsCard(stats_section, "📦", "Data TX/RX", "0 B")
        self.stat_data.pack(fill='x', pady=2)
        
        # Separator
        tk.Frame(left, bg=COLORS['border'], height=1).pack(fill='x', padx=15, pady=10)
        
        # Users Section
        users_section = tk.Frame(left, bg=COLORS['bg_card'])
        users_section.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        users_header = tk.Frame(users_section, bg=COLORS['bg_card'])
        users_header.pack(fill='x')
        
        tk.Label(users_header, text="👤 CONNECTED USERS",
                font=FONTS['body_bold'], fg=COLORS['accent_purple'],
                bg=COLORS['bg_card']).pack(side='left', pady=(0, 8))
        
        # Kick button
        self.kick_btn = tk.Button(users_header, text="🚫 Kick",
                                  font=FONTS['tiny'], bg=COLORS['accent_red'],
                                  fg=COLORS['text_primary'], relief='flat',
                                  cursor='hand2', command=self.kick_selected_user)
        self.kick_btn.pack(side='right')
        
        # Users listbox
        self.users_list = tk.Listbox(users_section, font=FONTS['small'],
                                     bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                     relief='flat', highlightthickness=0,
                                     selectbackground=COLORS['accent_purple'])
        self.users_list.pack(fill='both', expand=True)
        
        # ─── RIGHT PANEL (LOGS) ───
        right = tk.Frame(content, bg=COLORS['bg_card'])
        right.pack(side='right', fill='both', expand=True)
        
        # Logs header
        logs_header = tk.Frame(right, bg=COLORS['bg_card'])
        logs_header.pack(fill='x', padx=15, pady=10)
        
        tk.Label(logs_header, text="📜 SERVER LOGS",
                font=FONTS['body_bold'], fg=COLORS['accent_cyan'],
                bg=COLORS['bg_card']).pack(side='left')
        
        # Clear logs button
        tk.Button(logs_header, text="🗑️ Clear", font=FONTS['tiny'],
                 bg=COLORS['bg_light'], fg=COLORS['text_secondary'],
                 relief='flat', cursor='hand2',
                 command=self.clear_logs).pack(side='right')
        
        # Export logs button
        tk.Button(logs_header, text="📤 Export", font=FONTS['tiny'],
                 bg=COLORS['bg_light'], fg=COLORS['text_secondary'],
                 relief='flat', cursor='hand2',
                 command=self.export_logs).pack(side='right', padx=5)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(right, font=FONTS['small'],
                                                  bg=COLORS['bg_medium'],
                                                  fg=COLORS['text_primary'],
                                                  relief='flat', wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        self.log_text.configure(state='disabled')
        
        # Configure log tags
        log_tags = {
            'info': COLORS['accent_cyan'],
            'success': COLORS['accent_green'],
            'warning': COLORS['accent_orange'],
            'error': COLORS['accent_red'],
            'msg': COLORS['accent_pink'],
            'admin': COLORS['accent_purple'],
            'system': COLORS['text_dim']
        }
        for tag, color in log_tags.items():
            self.log_text.tag_configure(tag, foreground=color)
        
        # ═══ ADMIN PANEL (BOTTOM) ═══
        admin_panel = tk.Frame(self.root, bg=COLORS['bg_medium'], height=50)
        admin_panel.pack(fill='x', side='bottom')
        admin_panel.pack_propagate(False)
        
        admin_content = tk.Frame(admin_panel, bg=COLORS['bg_medium'])
        admin_content.pack(fill='both', expand=True, padx=15, pady=8)
        
        tk.Label(admin_content, text="👑 ADMIN:",
                font=FONTS['small_bold'], fg=COLORS['accent_purple'],
                bg=COLORS['bg_medium']).pack(side='left')
        
        # Broadcast input
        self.broadcast_entry = tk.Entry(admin_content, font=FONTS['small'],
                                        bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                        insertbackground=COLORS['accent_cyan'],
                                        relief='flat', width=40)
        self.broadcast_entry.pack(side='left', padx=10, ipady=4)
        self.broadcast_entry.bind('<Return>', lambda e: self.send_broadcast())
        
        CyberButton(admin_content, "📢 Broadcast", command=self.send_broadcast,
                   color='accent_purple', size='small').pack(side='left')
        
        # Initial log
        self.log("Server initialized. Ready to start...", 'info')
    
    # ─────────────────────────────────────────────────────────────
    # LOGGING
    # ─────────────────────────────────────────────────────────────
    
    def log(self, message: str, tag: str = 'info'):
        """Add a log entry to the log display."""
        timestamp = format_timestamp()
        
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"[{timestamp}] ", 'system')
        self.log_text.insert('end', f"{message}\n", tag)
        self.log_text.see('end')
        self.log_text.configure(state='disabled')
        
        # Also log to file
        self.logger.info(f"[{tag.upper()}] {message}")
    
    def clear_logs(self):
        """Clear the log display."""
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')
        self.log("Logs cleared", 'system')
    
    def export_logs(self):
        """Export logs to file."""
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
    
    # ─────────────────────────────────────────────────────────────
    # STATS UPDATE
    # ─────────────────────────────────────────────────────────────
    
    def update_stats(self):
        """Update the statistics display."""
        if not self.running:
            return
        
        with self.lock:
            client_count = len(self.clients)
            
            # Update peak
            if client_count > self.stats['peak_clients']:
                self.stats['peak_clients'] = client_count
        
        # Update UI
        self.stat_clients.set_value(str(client_count))
        self.stat_messages.set_value(str(self.stats['messages']))
        self.stat_peak.set_value(str(self.stats['peak_clients']))
        
        # Calculate total data
        total_data = self.stats['bytes_sent'] + self.stats['bytes_recv']
        self.stat_data.set_value(format_bytes(total_data))
        
        # Update uptime
        if self.start_time:
            uptime = int(time.time() - self.start_time)
            self.stat_uptime.set_value(format_uptime(uptime))
        
        # Schedule next update
        self.root.after(1000, self.update_stats)
    
    def update_users_list(self):
        """Update the users listbox."""
        self.users_list.delete(0, 'end')
        
        with self.lock:
            for username, conn in self.clients.items():
                status_icon = {
                    STATUS_ONLINE: '🟢',
                    STATUS_AWAY: '🟡',
                    STATUS_BUSY: '🔴'
                }.get(conn.status, '⚪')
                
                addr = f"{conn.address[0]}:{conn.address[1]}"
                self.users_list.insert('end', f"  {status_icon} {username} ({addr})")
    
    # ─────────────────────────────────────────────────────────────
    # SERVER CONTROL
    # ─────────────────────────────────────────────────────────────
    
    def start_server(self):
        """Start the TCP server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((DEFAULT_HOST, DEFAULT_PORT))
            self.server_socket.listen(MAX_CLIENTS)
            
            self.running = True
            self.start_time = time.time()
            
            # Update UI
            self.status_indicator.set_status('online')
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
            
            self.log(f"Server started on {DEFAULT_HOST}:{DEFAULT_PORT}", 'success')
            self.log(f"Max clients: {MAX_CLIENTS}", 'info')
            
            # Start accept thread
            threading.Thread(target=self.accept_loop, daemon=True).start()
            
            # Start stats update
            self.update_stats()
            
        except Exception as e:
            self.log(f"Failed to start server: {e}", 'error')
    
    def stop_server(self):
        """Stop the TCP server."""
        self.running = False
        
        # Notify and disconnect all clients
        with self.lock:
            for username, conn in list(self.clients.items()):
                try:
                    conn.send("SYSTEM|Server shutting down. Goodbye!\n".encode())
                    conn.socket.close()
                except Exception:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        
        # Update UI
        self.status_indicator.set_status('offline')
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        self.update_users_list()
        
        self.log("Server stopped", 'warning')
    
    # ─────────────────────────────────────────────────────────────
    # CLIENT HANDLING
    # ─────────────────────────────────────────────────────────────
    
    def accept_loop(self):
        """Accept incoming client connections."""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.stats['total_connections'] += 1
                
                self.root.after(0, lambda a=address: 
                    self.log(f"New connection from {a[0]}:{a[1]}", 'info'))
                
                # Handle client in separate thread
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                ).start()
                
            except Exception:
                if self.running:
                    self.root.after(0, lambda: self.log("Accept error", 'error'))
                break
    
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle a single client connection."""
        username = None
        
        try:
            # Send welcome prompt
            client_socket.send("WELCOME|Enter your username: ".encode())
            
            # Receive username
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                client_socket.close()
                return
            
            username = sanitize_username(data.decode().strip())
            
            if not username:
                client_socket.send("ERROR|Invalid username\n".encode())
                client_socket.close()
                return
            
            # Check if username is taken
            with self.lock:
                if username in self.clients:
                    client_socket.send(f"ERROR|Username '{username}' is already taken\n".encode())
                    client_socket.close()
                    return
                
                # Register client
                conn = ClientConnection(client_socket, address, username)
                self.clients[username] = conn
            
            # Notify
            self.root.after(0, lambda: self.log(f"'{username}' joined the chat", 'success'))
            self.root.after(0, self.update_users_list)
            
            # Welcome the user
            client_socket.send(f"OK|Welcome to Cyber Chat, {username}! 🚀\n".encode())
            
            # Broadcast join
            self.broadcast_system(f"'{username}' has joined the chat", exclude=username)
            self.broadcast_userlist()
            
            # Main message loop
            while self.running:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                self.stats['bytes_recv'] += len(data)
                
                # Update last ping
                with self.lock:
                    if username in self.clients:
                        self.clients[username].last_ping = time.time()
                
                message = data.decode().strip()
                if not message:
                    continue
                
                self.handle_message(username, message)
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Client error: {e}", 'error'))
        
        finally:
            # Cleanup
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
        """Process a message from a client."""
        self.stats['messages'] += 1
        
        # Log the message
        self.root.after(0, lambda: self.log(f"[{sender}] {message}", 'msg'))
        
        # Check for commands
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
            
            # Format user list with statuses
            user_str = ", ".join(f"{u}({statuses[u]})" for u in users)
            self.send_to_user(sender, f"USERS|Online: {user_str}\n")
        
        elif upper_msg.startswith("STATUS:"):
            # Change status: STATUS:away
            new_status = message.split(":", 1)[1].strip().lower()
            if new_status in [STATUS_ONLINE, STATUS_AWAY, STATUS_BUSY]:
                with self.lock:
                    if sender in self.clients:
                        self.clients[sender].status = new_status
                self.send_to_user(sender, f"OK|Status changed to {new_status}\n")
                self.broadcast_system(f"'{sender}' is now {new_status}")
                self.broadcast_userlist()
        
        elif upper_msg.startswith("TO:"):
            # Private message: TO:username:message
            parts = message.split(":", 2)
            if len(parts) >= 3:
                target = parts[1].strip()
                pm_content = parts[2].strip()
                self.send_private(sender, target, pm_content)
        
        else:
            # Regular broadcast message
            self.broadcast_message(sender, message)
    
    # ─────────────────────────────────────────────────────────────
    # MESSAGING
    # ─────────────────────────────────────────────────────────────
    
    def send_to_user(self, username: str, message: str) -> bool:
        """Send a message to a specific user."""
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
        """Send a private message from one user to another."""
        with self.lock:
            if target not in self.clients:
                self.send_to_user(sender, f"ERROR|User '{target}' not found\n")
                return
        
        # Send to recipient
        self.send_to_user(target, f"MSG|[Private from {sender}]: {message}\n")
        
        # Confirm to sender
        self.send_to_user(sender, f"SENT|[Private to {target}]: {message}\n")
        
        self.root.after(0, lambda: 
            self.log(f"[DM] {sender} → {target}: {message}", 'admin'))
    
    def broadcast_message(self, sender: str, message: str):
        """Broadcast a message to all users."""
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
        """Broadcast a system message to all users."""
        with self.lock:
            clients_copy = dict(self.clients)
        
        for username, conn in clients_copy.items():
            if username != exclude:
                try:
                    conn.send(f"SYSTEM|{message}\n".encode())
                except Exception:
                    pass
    
    def broadcast_userlist(self):
        """Broadcast updated user list to all clients."""
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
    
    # ─────────────────────────────────────────────────────────────
    # ADMIN FUNCTIONS
    # ─────────────────────────────────────────────────────────────
    
    def kick_selected_user(self):
        """Kick the selected user from the server."""
        selection = self.users_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to kick")
            return
        
        # Parse username from listbox item
        item = self.users_list.get(selection[0])
        # Format: "  🟢 username (ip:port)"
        username = item.split()[1]  # Get username after status emoji
        
        if messagebox.askyesno("Confirm Kick", f"Kick user '{username}'?"):
            self.kick_user(username, "Kicked by server admin")
    
    def kick_user(self, username: str, reason: str = "Kicked by admin"):
        """Kick a user from the server."""
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
        """Send an admin broadcast message."""
        message = self.broadcast_entry.get().strip()
        if not message:
            return
        
        self.broadcast_entry.delete(0, 'end')
        
        # Send to all clients
        self.broadcast_system(f"📢 ADMIN: {message}")
        
        self.log(f"[BROADCAST] {message}", 'admin')
    
    # ─────────────────────────────────────────────────────────────
    # LIFECYCLE
    # ─────────────────────────────────────────────────────────────
    
    def on_close(self):
        """Handle window close."""
        if self.running:
            if messagebox.askyesno("Confirm Exit", "Server is running. Stop and exit?"):
                self.stop_server()
            else:
                return
        
        self.root.destroy()
    
    def run(self):
        """Start the server GUI."""
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    server = CyberServer()
    server.run()

