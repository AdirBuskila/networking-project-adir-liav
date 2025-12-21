"""
⚡ CYBER CHAT - Client Module
Enhanced Chat Client with Modern Features
Students: Adir Buskila & Liav Wizman
"""

import socket
import threading
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from typing import Optional

from config import (
    DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE, PING_INTERVAL,
    COLORS, FONTS, STATUS_ONLINE, STATUS_AWAY, STATUS_BUSY
)
from utils import (
    ChatHistory, ChatLogger, parse_address, format_timestamp,
    validate_username, validate_message, replace_emoji_shortcuts,
    play_notification_sound, parse_command
)
from ui_components import (
    CyberButton, CyberEntry, CyberLabel, StatusIndicator,
    PingIndicator, MessageBubble, TypingIndicator, UserListItem,
    CyberDialog, EmojiPicker
)


# ═══════════════════════════════════════════════════════════════
# CYBER CLIENT
# ═══════════════════════════════════════════════════════════════

class CyberClient:
    """Enhanced Chat Client with Modern UI and Features."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("💬 CYBER CHAT")
        self.root.geometry("900x650")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.minsize(700, 500)
        
        # Connection state
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.username: Optional[str] = None
        self.running = True
        self.my_status = STATUS_ONLINE
        
        # Features
        self.history: Optional[ChatHistory] = None
        self.logger = ChatLogger('CyberClient')
        self.typing_timer = None
        self.is_typing = False
        self.last_ping_time = 0
        self.current_ping = 0
        
        # Online users with statuses
        self.online_users = {}  # {username: status}
        
        # Start with login screen
        self.show_login()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    # ─────────────────────────────────────────────────────────────
    # LOGIN SCREEN
    # ─────────────────────────────────────────────────────────────
    
    def show_login(self):
        """Display the login screen."""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Background
        self.root.configure(bg=COLORS['bg_dark'])
        
        # Center card
        card = tk.Frame(self.root, bg=COLORS['bg_card'], padx=50, pady=40)
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo/Title
        tk.Label(card, text="⚡ CYBER CHAT ⚡",
                font=FONTS['title'], fg=COLORS['accent_cyan'],
                bg=COLORS['bg_card']).pack(pady=(0, 5))
        
        tk.Label(card, text="TCP/IP Network Project",
                font=FONTS['small'], fg=COLORS['text_secondary'],
                bg=COLORS['bg_card']).pack()
        
        tk.Label(card, text="by Adir Buskila & Liav Wizman",
                font=FONTS['small'], fg=COLORS['accent_pink'],
                bg=COLORS['bg_card']).pack(pady=(5, 30))
        
        # Separator
        tk.Frame(card, bg=COLORS['accent_cyan'], height=2).pack(fill='x', pady=15)
        
        # Server input
        tk.Label(card, text="SERVER ADDRESS",
                font=FONTS['small_bold'], fg=COLORS['text_dim'],
                bg=COLORS['bg_card']).pack(anchor='w', pady=(15, 5))
        
        self.server_entry = tk.Entry(card, font=FONTS['body'], width=30,
                                     bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                     insertbackground=COLORS['accent_cyan'],
                                     relief='flat')
        self.server_entry.insert(0, f"{DEFAULT_HOST}:{DEFAULT_PORT}")
        self.server_entry.pack(fill='x', ipady=10)
        
        # Username input
        tk.Label(card, text="YOUR USERNAME",
                font=FONTS['small_bold'], fg=COLORS['text_dim'],
                bg=COLORS['bg_card']).pack(anchor='w', pady=(20, 5))
        
        self.user_entry = tk.Entry(card, font=FONTS['body'], width=30,
                                   bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                   insertbackground=COLORS['accent_cyan'],
                                   relief='flat')
        self.user_entry.pack(fill='x', ipady=10)
        self.user_entry.bind('<Return>', lambda e: self.connect())
        self.user_entry.focus()
        
        # Connect button
        self.connect_btn = CyberButton(card, "⚡ CONNECT ⚡",
                                       command=self.connect, color='accent_cyan')
        self.connect_btn.pack(pady=25, ipadx=30, ipady=10)
        
        # Status label
        self.status_label = tk.Label(card, text="",
                                     font=FONTS['small'],
                                     fg=COLORS['text_dim'],
                                     bg=COLORS['bg_card'])
        self.status_label.pack()
        
        # Help text
        help_frame = tk.Frame(card, bg=COLORS['bg_card'])
        help_frame.pack(pady=20)
        
        tk.Label(help_frame, text="💡 ",
                font=FONTS['tiny'], fg=COLORS['accent_cyan'],
                bg=COLORS['bg_card']).pack(side='left')
        tk.Label(help_frame, text="Make sure the server is running first!",
                font=FONTS['tiny'], fg=COLORS['text_dim'],
                bg=COLORS['bg_card']).pack(side='left')
    
    # ─────────────────────────────────────────────────────────────
    # CHAT SCREEN
    # ─────────────────────────────────────────────────────────────
    
    def show_chat(self):
        """Display the main chat interface."""
        # Clear login screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # ═══ HEADER ═══
        header = tk.Frame(self.root, bg=COLORS['bg_medium'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=COLORS['bg_medium'])
        header_content.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Title
        tk.Label(header_content, text="⚡ CYBER CHAT",
                font=FONTS['subheader'], fg=COLORS['accent_cyan'],
                bg=COLORS['bg_medium']).pack(side='left')
        
        # Right side controls
        right_header = tk.Frame(header_content, bg=COLORS['bg_medium'])
        right_header.pack(side='right')
        
        # Ping indicator
        self.ping_indicator = PingIndicator(right_header)
        self.ping_indicator.pack(side='left', padx=10)
        
        # User info
        tk.Label(right_header, text=f"👤 {self.username}",
                font=FONTS['body_bold'], fg=COLORS['accent_green'],
                bg=COLORS['bg_medium']).pack(side='left', padx=10)
        
        # Status dropdown (simplified as buttons)
        status_frame = tk.Frame(right_header, bg=COLORS['bg_medium'])
        status_frame.pack(side='left', padx=5)
        
        self.status_btn = tk.Button(status_frame, text="● Online",
                                    font=FONTS['tiny'], bg=COLORS['status_online'],
                                    fg=COLORS['bg_dark'], relief='flat',
                                    cursor='hand2', command=self.cycle_status)
        self.status_btn.pack()
        
        # Disconnect button
        tk.Button(right_header, text="✕ Leave",
                 font=FONTS['small_bold'], bg=COLORS['accent_red'],
                 fg=COLORS['text_primary'], relief='flat',
                 cursor='hand2', command=self.disconnect).pack(side='left', padx=5)
        
        # Glow line
        tk.Frame(self.root, bg=COLORS['accent_cyan'], height=2).pack(fill='x')
        
        # ═══ MAIN CONTENT ═══
        main = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ─── LEFT PANEL (Users) ───
        left = tk.Frame(main, bg=COLORS['bg_card'], width=180)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        
        # Users header
        users_header = tk.Frame(left, bg=COLORS['bg_card'])
        users_header.pack(fill='x', padx=10, pady=10)
        
        tk.Label(users_header, text="👥 ONLINE",
                font=FONTS['body_bold'], fg=COLORS['accent_pink'],
                bg=COLORS['bg_card']).pack(side='left')
        
        self.users_count_label = tk.Label(users_header, text="(0)",
                                          font=FONTS['small'],
                                          fg=COLORS['text_dim'],
                                          bg=COLORS['bg_card'])
        self.users_count_label.pack(side='left', padx=5)
        
        # Users list frame (scrollable)
        users_container = tk.Frame(left, bg=COLORS['bg_card'])
        users_container.pack(fill='both', expand=True, padx=5)
        
        self.users_canvas = tk.Canvas(users_container, bg=COLORS['bg_card'],
                                      highlightthickness=0)
        self.users_scrollbar = tk.Scrollbar(users_container, orient='vertical',
                                            command=self.users_canvas.yview)
        self.users_frame = tk.Frame(self.users_canvas, bg=COLORS['bg_card'])
        
        self.users_canvas.configure(yscrollcommand=self.users_scrollbar.set)
        self.users_scrollbar.pack(side='right', fill='y')
        self.users_canvas.pack(side='left', fill='both', expand=True)
        
        self.users_window = self.users_canvas.create_window(
            (0, 0), window=self.users_frame, anchor='nw'
        )
        
        self.users_frame.bind('<Configure>', 
            lambda e: self.users_canvas.configure(scrollregion=self.users_canvas.bbox('all')))
        self.users_canvas.bind('<Configure>', 
            lambda e: self.users_canvas.itemconfig(self.users_window, width=e.width))
        
        # Buttons at bottom
        btn_frame = tk.Frame(left, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(btn_frame, text="🔄 Refresh",
                 font=FONTS['tiny'], bg=COLORS['bg_light'],
                 fg=COLORS['text_secondary'], relief='flat',
                 cursor='hand2', command=lambda: self.send("LIST")).pack(fill='x', pady=2)
        
        tk.Button(btn_frame, text="📥 Save Chat",
                 font=FONTS['tiny'], bg=COLORS['bg_light'],
                 fg=COLORS['text_secondary'], relief='flat',
                 cursor='hand2', command=self.save_chat).pack(fill='x', pady=2)
        
        # ─── RIGHT PANEL (Chat) ───
        right = tk.Frame(main, bg=COLORS['bg_card'])
        right.pack(side='right', fill='both', expand=True)
        
        # Messages area (scrollable)
        messages_container = tk.Frame(right, bg=COLORS['bg_medium'])
        messages_container.pack(fill='both', expand=True)
        
        self.chat_canvas = tk.Canvas(messages_container, bg=COLORS['bg_medium'],
                                     highlightthickness=0)
        self.chat_scrollbar = tk.Scrollbar(messages_container, orient='vertical',
                                           command=self.chat_canvas.yview)
        self.messages_frame = tk.Frame(self.chat_canvas, bg=COLORS['bg_medium'])
        
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
        self.chat_scrollbar.pack(side='right', fill='y')
        self.chat_canvas.pack(side='left', fill='both', expand=True)
        
        self.chat_window = self.chat_canvas.create_window(
            (0, 0), window=self.messages_frame, anchor='nw'
        )
        
        self.messages_frame.bind('<Configure>',
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox('all')))
        self.chat_canvas.bind('<Configure>',
            lambda e: self.chat_canvas.itemconfig(self.chat_window, width=e.width))
        
        # Typing indicator
        self.typing_indicator = TypingIndicator(right)
        
        # Input area
        input_container = tk.Frame(right, bg=COLORS['bg_light'], height=60)
        input_container.pack(fill='x', side='bottom')
        input_container.pack_propagate(False)
        
        input_inner = tk.Frame(input_container, bg=COLORS['bg_light'])
        input_inner.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Emoji button
        self.emoji_btn = tk.Button(input_inner, text="😊",
                                   font=FONTS['body'], bg=COLORS['bg_dark'],
                                   fg=COLORS['text_primary'], relief='flat',
                                   cursor='hand2', command=self.show_emoji_picker)
        self.emoji_btn.pack(side='left', padx=(0, 5))
        
        # Message input
        self.msg_entry = tk.Entry(input_inner, font=FONTS['body'],
                                  bg=COLORS['bg_dark'], fg=COLORS['text_primary'],
                                  insertbackground=COLORS['accent_cyan'],
                                  relief='flat')
        self.msg_entry.pack(side='left', fill='both', expand=True, padx=5, ipady=8)
        self.msg_entry.bind('<Return>', lambda e: self.send_chat())
        self.msg_entry.bind('<KeyRelease>', self.on_typing)
        self.msg_entry.focus()
        
        # Send button
        CyberButton(input_inner, "SEND ➤", command=self.send_chat,
                   color='accent_green', size='small').pack(side='right')
        
        # Welcome message
        self.add_system("🚀 Welcome to Cyber Chat! Type a message or click a user to DM.")
        self.add_system("💡 Commands: /status <online|away|busy>, /help")
        
        # Request user list
        self.root.after(300, lambda: self.send("LIST"))
        
        # Start ping
        self.start_ping()
    
    # ─────────────────────────────────────────────────────────────
    # CONNECTION
    # ─────────────────────────────────────────────────────────────
    
    def connect(self):
        """Connect to the chat server."""
        # Parse server address
        server_str = self.server_entry.get().strip()
        host, port = parse_address(server_str, DEFAULT_HOST, DEFAULT_PORT)
        
        # Validate username
        username = self.user_entry.get().strip()
        valid, error = validate_username(username)
        if not valid:
            self.status_label.configure(text=f"⚠️ {error}", fg=COLORS['accent_red'])
            return
        
        # Show connecting status
        self.status_label.configure(text="Connecting...", fg=COLORS['accent_orange'])
        self.connect_btn.configure(state='disabled')
        self.root.update()
        
        try:
            # Create socket and connect
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)  # 5 second timeout for connection
            self.socket.connect((host, port))
            self.socket.settimeout(None)  # Remove timeout for normal operation
            
            self.connected = True
            self.username = username
            
            # Initialize chat history
            self.history = ChatHistory(username)
            
            # Start receive thread
            threading.Thread(target=self.receive_loop, daemon=True).start()
            
            # Send username (server expects it after welcome)
            time.sleep(0.2)
            self.socket.send(username.encode())
            time.sleep(0.2)
            
            # Show chat interface
            self.show_chat()
            
        except ConnectionRefusedError:
            self.status_label.configure(
                text="❌ Connection refused! Is the server running?",
                fg=COLORS['accent_red']
            )
            self.connect_btn.configure(state='normal')
            
        except socket.timeout:
            self.status_label.configure(
                text="❌ Connection timed out!",
                fg=COLORS['accent_red']
            )
            self.connect_btn.configure(state='normal')
            
        except Exception as e:
            self.status_label.configure(
                text=f"❌ Error: {str(e)}",
                fg=COLORS['accent_red']
            )
            self.connect_btn.configure(state='normal')
    
    def disconnect(self):
        """Disconnect from the server."""
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
    
    # ─────────────────────────────────────────────────────────────
    # MESSAGING
    # ─────────────────────────────────────────────────────────────
    
    def send(self, message: str):
        """Send a raw message to the server."""
        if self.connected and message:
            try:
                self.socket.send(message.encode())
            except Exception:
                pass
    
    def send_chat(self):
        """Send a chat message (from input field)."""
        message = self.msg_entry.get().strip()
        if not message:
            return
        
        self.msg_entry.delete(0, 'end')
        
        # Replace emoji shortcuts
        message = replace_emoji_shortcuts(message)
        
        # Check for commands
        command, args = parse_command(message)
        
        if command:
            self.handle_command(command, args)
        else:
            # Validate message
            valid, error = validate_message(message)
            if not valid:
                self.add_system(f"❌ {error}")
                return
            
            # Send to server
            self.send(message)
        
        # Stop typing indicator
        self.stop_typing_indicator()
    
    def handle_command(self, command: str, args: str):
        """Handle client-side commands."""
        if command == 'help':
            self.add_system("📖 Available commands:")
            self.add_system("  /status <online|away|busy> - Change your status")
            self.add_system("  /dm <user> <message> - Send private message")
            self.add_system("  /clear - Clear chat window")
            self.add_system("  /save - Save chat history")
            self.add_system("  /ping - Check connection latency")
            
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
            
        elif command == 'ping':
            self.add_system(f"📶 Current ping: {self.current_ping}ms")
            
        else:
            self.add_system(f"❌ Unknown command: /{command}")
    
    # ─────────────────────────────────────────────────────────────
    # RECEIVE LOOP
    # ─────────────────────────────────────────────────────────────
    
    def receive_loop(self):
        """Receive messages from the server."""
        while self.connected and self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                # Handle multiple messages in one packet
                messages = data.decode().strip().split('\n')
                for msg in messages:
                    if '|' in msg:
                        msg_type, content = msg.split('|', 1)
                        self.root.after(0, lambda t=msg_type, c=content: 
                            self.process_message(t, c))
                            
            except Exception as e:
                self.logger.error(f"Receive error: {e}")
                break
        
        # Connection lost
        self.root.after(0, self.on_disconnect)
    
    def process_message(self, msg_type: str, content: str):
        """Process a received message."""
        
        if msg_type == "MSG":
            # Regular or private message
            if content.startswith("[Private from"):
                # Private message received
                parts = content.split("]: ", 1)
                sender = parts[0].replace("[Private from ", "")
                message = parts[1] if len(parts) > 1 else ""
                self.add_message(sender, message, 'private_recv')
                self.history.add_message(sender, message, 'private', self.username)
                play_notification_sound()
            elif content.startswith("["):
                # Regular message
                parts = content.split("]: ", 1)
                sender = parts[0].replace("[", "")
                message = parts[1] if len(parts) > 1 else ""
                self.add_message(sender, message, 'recv')
                self.history.add_message(sender, message)
                
        elif msg_type == "SENT":
            # Message sent confirmation
            if content.startswith("[Private to"):
                parts = content.split("]: ", 1)
                target = parts[0].replace("[Private to ", "")
                message = parts[1] if len(parts) > 1 else ""
                self.add_message(target, message, 'private_sent')
                self.history.add_message(self.username, message, 'private', target)
            elif content.startswith("[You]:"):
                message = content.replace("[You]: ", "")
                self.add_message(self.username, message, 'sent')
                self.history.add_message(self.username, message)
                
        elif msg_type == "SYSTEM":
            self.add_system(content)
            self.history.add_message("SYSTEM", content, 'system')
            
        elif msg_type == "USERS":
            self.update_users(content)
            
        elif msg_type == "ERROR":
            self.add_system(f"❌ {content}")
            
        elif msg_type == "KICK":
            messagebox.showerror("Kicked", f"You were kicked: {content}")
            self.disconnect()
            
        elif msg_type == "TYPING":
            # Someone is typing
            self.typing_indicator.add_user(content)
            
        elif msg_type == "STOP_TYPING":
            self.typing_indicator.remove_user(content)
            
        elif msg_type == "PONG":
            # Ping response
            try:
                self.current_ping = int((time.time() - self.last_ping_time) * 1000)
                self.ping_indicator.set_ping(self.current_ping)
            except Exception:
                pass
    
    # ─────────────────────────────────────────────────────────────
    # UI UPDATES
    # ─────────────────────────────────────────────────────────────
    
    def add_message(self, sender: str, message: str, msg_type: str = 'recv'):
        """Add a message to the chat display."""
        bubble = MessageBubble(self.messages_frame, sender, message, msg_type)
        bubble.pack(fill='x')
        
        # Scroll to bottom
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
    
    def add_system(self, message: str):
        """Add a system message to the chat."""
        bubble = MessageBubble(self.messages_frame, "", message, 'system')
        bubble.pack(fill='x')
        
        # Scroll to bottom
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
    
    def update_users(self, users_str: str):
        """Update the users list display."""
        # Clear existing users
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        # Parse users (format: "Online: user1(status), user2(status), ...")
        users_part = users_str.replace("Online:", "").strip()
        if not users_part:
            return
        
        users = []
        for user_entry in users_part.split(","):
            user_entry = user_entry.strip()
            if not user_entry:
                continue
            
            # Parse "username(status)" format
            if "(" in user_entry:
                username = user_entry.split("(")[0]
                status = user_entry.split("(")[1].rstrip(")")
            else:
                username = user_entry
                status = STATUS_ONLINE
            
            users.append((username, status))
            self.online_users[username] = status
        
        # Update count
        self.users_count_label.configure(text=f"({len(users)})")
        
        # Create user list items
        for username, status in users:
            is_self = username == self.username
            
            item = UserListItem(
                self.users_frame,
                username,
                status,
                is_self=is_self,
                on_click=self.open_dm_dialog if not is_self else None
            )
            item.pack(fill='x', pady=1)
    
    def clear_chat(self):
        """Clear the chat display."""
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self.add_system("Chat cleared.")
    
    # ─────────────────────────────────────────────────────────────
    # FEATURES
    # ─────────────────────────────────────────────────────────────
    
    def open_dm_dialog(self, username: str):
        """Open a dialog to send a private message."""
        dialog = CyberDialog(self.root, f"DM to {username}", 400, 150)
        
        def create_content(frame):
            tk.Label(frame, text=f"🔒 Private message to {username}",
                    font=FONTS['body_bold'], fg=COLORS['accent_purple'],
                    bg=COLORS['bg_card']).pack(pady=(0, 15))
            
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
            
            CyberButton(frame, "SEND", command=send_dm,
                       color='accent_purple', size='small').pack(pady=15)
        
        dialog.add_content(create_content)
    
    def show_emoji_picker(self):
        """Show the emoji picker popup."""
        def insert_emoji(emoji: str):
            self.msg_entry.insert('end', emoji)
            self.msg_entry.focus()
        
        EmojiPicker(self.emoji_btn, insert_emoji)
    
    def cycle_status(self):
        """Cycle through status options."""
        statuses = [STATUS_ONLINE, STATUS_AWAY, STATUS_BUSY]
        current_idx = statuses.index(self.my_status) if self.my_status in statuses else 0
        new_status = statuses[(current_idx + 1) % len(statuses)]
        
        self.send(f"STATUS:{new_status}")
        self.my_status = new_status
        self.update_status_button()
    
    def update_status_button(self):
        """Update the status button appearance."""
        status_config = {
            STATUS_ONLINE: ("● Online", COLORS['status_online']),
            STATUS_AWAY: ("● Away", COLORS['status_away']),
            STATUS_BUSY: ("● Busy", COLORS['status_busy'])
        }
        text, color = status_config.get(self.my_status, ("● Online", COLORS['status_online']))
        self.status_btn.configure(text=text, bg=color)
    
    def save_chat(self):
        """Save the chat history to a file."""
        if self.history:
            try:
                filename = self.history.export_txt()
                self.add_system(f"💾 Chat saved to: {filename}")
            except Exception as e:
                self.add_system(f"❌ Failed to save: {e}")
    
    # ─────────────────────────────────────────────────────────────
    # TYPING INDICATOR
    # ─────────────────────────────────────────────────────────────
    
    def on_typing(self, event):
        """Handle typing events."""
        if not self.is_typing:
            self.is_typing = True
            # Optionally send typing indicator to server
            # self.send(f"TYPING:{self.username}")
        
        # Reset timer
        if self.typing_timer:
            self.root.after_cancel(self.typing_timer)
        
        self.typing_timer = self.root.after(2000, self.stop_typing_indicator)
    
    def stop_typing_indicator(self):
        """Stop the typing indicator."""
        if self.is_typing:
            self.is_typing = False
            # Optionally send stop typing to server
            # self.send(f"STOP_TYPING:{self.username}")
    
    # ─────────────────────────────────────────────────────────────
    # PING
    # ─────────────────────────────────────────────────────────────
    
    def start_ping(self):
        """Start periodic ping to measure latency."""
        self.do_ping()
    
    def do_ping(self):
        """Send a ping and schedule next one."""
        if not self.connected:
            return
        
        self.last_ping_time = time.time()
        # For simplicity, we use LIST command which server always responds to
        # A proper implementation would have PING/PONG messages
        
        # Schedule next ping
        self.root.after(PING_INTERVAL * 1000, self.do_ping)
    
    # ─────────────────────────────────────────────────────────────
    # LIFECYCLE
    # ─────────────────────────────────────────────────────────────
    
    def on_disconnect(self):
        """Handle disconnection from server."""
        if self.connected:
            self.connected = False
            messagebox.showwarning("Disconnected", "Lost connection to server")
            self.show_login()
    
    def on_close(self):
        """Handle window close."""
        self.running = False
        
        if self.connected:
            try:
                self.send("QUIT")
            except Exception:
                pass
        
        self.root.destroy()
    
    def run(self):
        """Start the client application."""
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    client = CyberClient()
    client.run()

