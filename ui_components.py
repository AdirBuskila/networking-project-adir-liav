"""
⚡ CYBER CHAT - UI Components Module
Reusable tkinter widgets with cyberpunk styling
Students: Adir Buskila & Liav Wizman
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional, Dict, Any
from datetime import datetime

from config import COLORS, FONTS


# ═══════════════════════════════════════════════════════════════
# STYLED BUTTON
# ═══════════════════════════════════════════════════════════════

class CyberButton(tk.Button):
    """Cyberpunk styled button with hover effects."""
    
    def __init__(self, parent, text: str, command: Callable = None,
                 color: str = 'accent_cyan', size: str = 'normal', **kwargs):
        
        # Color mapping
        bg_color = COLORS.get(color, color)
        fg_color = COLORS['bg_dark'] if color in ['accent_cyan', 'accent_green', 'accent_yellow'] else COLORS['text_primary']
        
        # Size mapping
        font = FONTS['body_bold'] if size == 'normal' else FONTS['small_bold']
        padding = {'ipadx': 15, 'ipady': 8} if size == 'normal' else {'ipadx': 10, 'ipady': 5}
        
        super().__init__(
            parent,
            text=text,
            font=font,
            bg=bg_color,
            fg=fg_color,
            activebackground=COLORS['accent_pink'],
            activeforeground=COLORS['text_primary'],
            relief='flat',
            cursor='hand2',
            command=command,
            **kwargs
        )
        
        self.default_bg = bg_color
        self.hover_bg = COLORS['accent_pink']
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        self.configure(bg=self.hover_bg)
    
    def _on_leave(self, e):
        self.configure(bg=self.default_bg)


# ═══════════════════════════════════════════════════════════════
# STYLED ENTRY
# ═══════════════════════════════════════════════════════════════

class CyberEntry(tk.Entry):
    """Cyberpunk styled entry with placeholder support."""
    
    def __init__(self, parent, placeholder: str = "", width: int = 25, **kwargs):
        super().__init__(
            parent,
            font=FONTS['body'],
            bg=COLORS['bg_light'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['accent_cyan'],
            relief='flat',
            width=width,
            **kwargs
        )
        
        self.placeholder = placeholder
        self.placeholder_color = COLORS['text_dim']
        self.default_fg = COLORS['text_primary']
        self.showing_placeholder = False
        
        if placeholder:
            self._show_placeholder()
            self.bind('<FocusIn>', self._on_focus_in)
            self.bind('<FocusOut>', self._on_focus_out)
    
    def _show_placeholder(self):
        self.delete(0, 'end')
        self.insert(0, self.placeholder)
        self.configure(fg=self.placeholder_color)
        self.showing_placeholder = True
    
    def _hide_placeholder(self):
        if self.showing_placeholder:
            self.delete(0, 'end')
            self.configure(fg=self.default_fg)
            self.showing_placeholder = False
    
    def _on_focus_in(self, e):
        self._hide_placeholder()
    
    def _on_focus_out(self, e):
        if not self.get():
            self._show_placeholder()
    
    def get_value(self) -> str:
        """Get entry value, ignoring placeholder."""
        if self.showing_placeholder:
            return ""
        return self.get()


# ═══════════════════════════════════════════════════════════════
# STYLED LABEL
# ═══════════════════════════════════════════════════════════════

class CyberLabel(tk.Label):
    """Cyberpunk styled label."""
    
    def __init__(self, parent, text: str, style: str = 'normal', 
                 color: str = None, **kwargs):
        
        # Style mapping
        styles = {
            'title': (FONTS['title'], COLORS['accent_cyan']),
            'header': (FONTS['header'], COLORS['accent_cyan']),
            'subheader': (FONTS['subheader'], COLORS['accent_pink']),
            'body': (FONTS['body'], COLORS['text_primary']),
            'normal': (FONTS['body'], COLORS['text_primary']),
            'dim': (FONTS['small'], COLORS['text_dim']),
            'accent': (FONTS['body_bold'], COLORS['accent_cyan']),
        }
        
        font, default_color = styles.get(style, styles['normal'])
        fg = COLORS.get(color, color) if color else default_color
        
        super().__init__(
            parent,
            text=text,
            font=font,
            fg=fg,
            bg=parent.cget('bg') if hasattr(parent, 'cget') else COLORS['bg_dark'],
            **kwargs
        )


# ═══════════════════════════════════════════════════════════════
# STATUS INDICATOR
# ═══════════════════════════════════════════════════════════════

class StatusIndicator(tk.Frame):
    """Status indicator with dot and text."""
    
    def __init__(self, parent, initial_status: str = 'offline', **kwargs):
        bg = parent.cget('bg') if hasattr(parent, 'cget') else COLORS['bg_dark']
        super().__init__(parent, bg=bg, **kwargs)
        
        self.status_colors = {
            'online': COLORS['status_online'],
            'away': COLORS['status_away'],
            'busy': COLORS['status_busy'],
            'offline': COLORS['status_offline']
        }
        
        self.dot = tk.Label(self, text="●", font=('Consolas', 16), bg=bg)
        self.dot.pack(side='left')
        
        self.text = tk.Label(self, font=FONTS['small_bold'], bg=bg)
        self.text.pack(side='left', padx=(3, 0))
        
        self.set_status(initial_status)
    
    def set_status(self, status: str):
        """Update status display."""
        color = self.status_colors.get(status, COLORS['status_offline'])
        self.dot.configure(fg=color)
        self.text.configure(text=status.upper(), fg=color)


# ═══════════════════════════════════════════════════════════════
# PING INDICATOR
# ═══════════════════════════════════════════════════════════════

class PingIndicator(tk.Frame):
    """Connection quality indicator showing ping."""
    
    def __init__(self, parent, **kwargs):
        bg = parent.cget('bg') if hasattr(parent, 'cget') else COLORS['bg_dark']
        super().__init__(parent, bg=bg, **kwargs)
        
        self.icon = tk.Label(self, text="📶", font=FONTS['small'], bg=bg)
        self.icon.pack(side='left')
        
        self.ping_label = tk.Label(self, text="-- ms", font=FONTS['small'],
                                   fg=COLORS['text_dim'], bg=bg)
        self.ping_label.pack(side='left', padx=(3, 0))
        
        self.bars = []
        for i in range(4):
            bar = tk.Label(self, text="▮", font=('Consolas', 8), 
                          fg=COLORS['text_dim'], bg=bg)
            bar.pack(side='left')
            self.bars.append(bar)
    
    def set_ping(self, ping_ms: float):
        """Update ping display."""
        self.ping_label.configure(text=f"{int(ping_ms)} ms")
        
        # Color based on ping quality
        if ping_ms < 50:
            color = COLORS['accent_green']
            active_bars = 4
        elif ping_ms < 100:
            color = COLORS['accent_cyan']
            active_bars = 3
        elif ping_ms < 200:
            color = COLORS['accent_yellow']
            active_bars = 2
        else:
            color = COLORS['accent_red']
            active_bars = 1
        
        self.ping_label.configure(fg=color)
        
        for i, bar in enumerate(self.bars):
            bar.configure(fg=color if i < active_bars else COLORS['text_dim'])


# ═══════════════════════════════════════════════════════════════
# MESSAGE BUBBLE
# ═══════════════════════════════════════════════════════════════

class MessageBubble(tk.Frame):
    """Chat message bubble with timestamp and styling."""
    
    def __init__(self, parent, sender: str, message: str, 
                 msg_type: str = 'recv', timestamp: str = None, **kwargs):
        super().__init__(parent, bg=COLORS['bg_medium'], **kwargs)
        
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
        
        if msg_type == 'sent':
            self._create_sent_bubble(message)
        elif msg_type == 'recv':
            self._create_recv_bubble(sender, message)
        elif msg_type == 'private_sent':
            self._create_private_sent_bubble(sender, message)
        elif msg_type == 'private_recv':
            self._create_private_recv_bubble(sender, message)
        elif msg_type == 'system':
            self._create_system_message(message)
    
    def _create_sent_bubble(self, message: str):
        """Create sent message bubble (right aligned, cyan border)."""
        container = tk.Frame(self, bg=COLORS['bg_medium'])
        container.pack(fill='x', pady=4, padx=8)
        
        # Time label
        time_lbl = tk.Label(container, text=self.timestamp, font=FONTS['tiny'],
                           fg=COLORS['text_dim'], bg=COLORS['bg_medium'])
        time_lbl.pack(side='right', padx=(5, 0))
        
        # Bubble
        bubble = tk.Frame(container, bg=COLORS['accent_cyan'])
        bubble.pack(side='right')
        
        inner = tk.Frame(bubble, bg=COLORS['bg_light'], padx=12, pady=8)
        inner.pack(padx=2, pady=2)
        
        tk.Label(inner, text=message, font=FONTS['message'],
                fg=COLORS['text_primary'], bg=COLORS['bg_light'],
                wraplength=300, justify='left').pack()
    
    def _create_recv_bubble(self, sender: str, message: str):
        """Create received message bubble (left aligned, purple border)."""
        container = tk.Frame(self, bg=COLORS['bg_medium'])
        container.pack(fill='x', pady=4, padx=8)
        
        # Sender label
        sender_frame = tk.Frame(container, bg=COLORS['bg_medium'])
        sender_frame.pack(anchor='w')
        
        tk.Label(sender_frame, text=f"👤 {sender}", font=FONTS['tiny'],
                fg=COLORS['accent_pink'], bg=COLORS['bg_medium']).pack(side='left')
        tk.Label(sender_frame, text=f" · {self.timestamp}", font=FONTS['tiny'],
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left')
        
        # Bubble
        bubble = tk.Frame(container, bg=COLORS['accent_purple'])
        bubble.pack(side='left')
        
        inner = tk.Frame(bubble, bg=COLORS['bg_card'], padx=12, pady=8)
        inner.pack(padx=2, pady=2)
        
        tk.Label(inner, text=message, font=FONTS['message'],
                fg=COLORS['text_primary'], bg=COLORS['bg_card'],
                wraplength=300, justify='left').pack()
    
    def _create_private_sent_bubble(self, recipient: str, message: str):
        """Create private sent message bubble."""
        container = tk.Frame(self, bg=COLORS['bg_medium'])
        container.pack(fill='x', pady=4, padx=8)
        
        # Header
        header = tk.Frame(container, bg=COLORS['bg_medium'])
        header.pack(anchor='e')
        
        tk.Label(header, text=f"🔒 To {recipient}", font=FONTS['tiny'],
                fg=COLORS['accent_purple'], bg=COLORS['bg_medium']).pack(side='right')
        tk.Label(header, text=f"{self.timestamp} · ", font=FONTS['tiny'],
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='right')
        
        # Bubble
        bubble = tk.Frame(container, bg=COLORS['accent_purple'])
        bubble.pack(side='right')
        
        inner = tk.Frame(bubble, bg=COLORS['bg_light'], padx=12, pady=8)
        inner.pack(padx=2, pady=2)
        
        tk.Label(inner, text=message, font=FONTS['message'],
                fg=COLORS['text_primary'], bg=COLORS['bg_light'],
                wraplength=300, justify='left').pack()
    
    def _create_private_recv_bubble(self, sender: str, message: str):
        """Create private received message bubble."""
        container = tk.Frame(self, bg=COLORS['bg_medium'])
        container.pack(fill='x', pady=4, padx=8)
        
        # Header
        header = tk.Frame(container, bg=COLORS['bg_medium'])
        header.pack(anchor='w')
        
        tk.Label(header, text=f"🔒 From {sender}", font=FONTS['tiny'],
                fg=COLORS['accent_pink'], bg=COLORS['bg_medium']).pack(side='left')
        tk.Label(header, text=f" · {self.timestamp}", font=FONTS['tiny'],
                fg=COLORS['text_dim'], bg=COLORS['bg_medium']).pack(side='left')
        
        # Bubble
        bubble = tk.Frame(container, bg=COLORS['accent_pink'])
        bubble.pack(side='left')
        
        inner = tk.Frame(bubble, bg=COLORS['bg_card'], padx=12, pady=8)
        inner.pack(padx=2, pady=2)
        
        tk.Label(inner, text=message, font=FONTS['message'],
                fg=COLORS['text_primary'], bg=COLORS['bg_card'],
                wraplength=300, justify='left').pack()
    
    def _create_system_message(self, message: str):
        """Create system message (centered, cyan text)."""
        container = tk.Frame(self, bg=COLORS['bg_medium'])
        container.pack(fill='x', pady=2, padx=8)
        
        tk.Label(container, text=f"⚡ {message}", font=FONTS['small'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_medium']).pack()


# ═══════════════════════════════════════════════════════════════
# TYPING INDICATOR
# ═══════════════════════════════════════════════════════════════

class TypingIndicator(tk.Frame):
    """Animated typing indicator showing who is typing."""
    
    def __init__(self, parent, **kwargs):
        bg = COLORS['bg_medium']
        super().__init__(parent, bg=bg, **kwargs)
        
        self.typing_users = set()
        self.animation_id = None
        self.dot_index = 0
        
        self.label = tk.Label(self, text="", font=FONTS['small'],
                             fg=COLORS['text_dim'], bg=bg)
        self.label.pack(padx=10, pady=5)
        
        # Hide by default
        self.pack_forget()
    
    def add_user(self, username: str):
        """Add a user to the typing list."""
        self.typing_users.add(username)
        self._update_display()
        self._start_animation()
    
    def remove_user(self, username: str):
        """Remove a user from the typing list."""
        self.typing_users.discard(username)
        self._update_display()
        if not self.typing_users:
            self._stop_animation()
    
    def _update_display(self):
        """Update the display text."""
        if not self.typing_users:
            self.pack_forget()
            return
        
        self.pack(fill='x')
        
        users = list(self.typing_users)
        if len(users) == 1:
            text = f"{users[0]} is typing"
        elif len(users) == 2:
            text = f"{users[0]} and {users[1]} are typing"
        else:
            text = f"{len(users)} people are typing"
        
        self.label.configure(text=text + "...")
    
    def _start_animation(self):
        """Start the dots animation."""
        if self.animation_id is None:
            self._animate()
    
    def _stop_animation(self):
        """Stop the dots animation."""
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
    
    def _animate(self):
        """Animate the dots."""
        if not self.typing_users:
            return
        
        dots = "." * ((self.dot_index % 3) + 1)
        users = list(self.typing_users)
        
        if len(users) == 1:
            text = f"{users[0]} is typing{dots}"
        elif len(users) == 2:
            text = f"{users[0]} and {users[1]} are typing{dots}"
        else:
            text = f"{len(users)} people are typing{dots}"
        
        self.label.configure(text=text)
        self.dot_index += 1
        self.animation_id = self.after(500, self._animate)


# ═══════════════════════════════════════════════════════════════
# USER LIST ITEM
# ═══════════════════════════════════════════════════════════════

class UserListItem(tk.Frame):
    """Clickable user list item with status indicator."""
    
    def __init__(self, parent, username: str, status: str = 'online',
                 is_self: bool = False, on_click: Callable = None, **kwargs):
        bg = COLORS['bg_card']
        super().__init__(parent, bg=bg, **kwargs)
        
        self.username = username
        self.on_click = on_click
        
        # Status colors
        status_colors = {
            'online': COLORS['status_online'],
            'away': COLORS['status_away'],
            'busy': COLORS['status_busy'],
            'offline': COLORS['status_offline']
        }
        
        status_color = status_colors.get(status, COLORS['status_offline'])
        text_color = COLORS['accent_green'] if is_self else COLORS['text_secondary']
        
        # Status dot
        self.dot = tk.Label(self, text="●", font=FONTS['small'],
                           fg=status_color, bg=bg)
        self.dot.pack(side='left', padx=(5, 3))
        
        # Username
        self.name_label = tk.Label(self, text=username, font=FONTS['small'],
                                   fg=text_color, bg=bg)
        self.name_label.pack(side='left')
        
        # Self indicator
        if is_self:
            tk.Label(self, text="(you)", font=FONTS['tiny'],
                    fg=COLORS['text_dim'], bg=bg).pack(side='left', padx=3)
        
        # Make clickable (for DM)
        if not is_self and on_click:
            self.configure(cursor='hand2')
            self.bind('<Button-1>', lambda e: on_click(username))
            self.name_label.bind('<Button-1>', lambda e: on_click(username))
            self.dot.bind('<Button-1>', lambda e: on_click(username))
            
            # Hover effects
            self.bind('<Enter>', self._on_enter)
            self.bind('<Leave>', self._on_leave)
            self.name_label.bind('<Enter>', self._on_enter)
            self.name_label.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        self.configure(bg=COLORS['bg_hover'])
        self.dot.configure(bg=COLORS['bg_hover'])
        self.name_label.configure(bg=COLORS['bg_hover'], fg=COLORS['accent_pink'])
    
    def _on_leave(self, e):
        self.configure(bg=COLORS['bg_card'])
        self.dot.configure(bg=COLORS['bg_card'])
        self.name_label.configure(bg=COLORS['bg_card'], fg=COLORS['text_secondary'])
    
    def update_status(self, status: str):
        """Update user status."""
        status_colors = {
            'online': COLORS['status_online'],
            'away': COLORS['status_away'],
            'busy': COLORS['status_busy'],
            'offline': COLORS['status_offline']
        }
        self.dot.configure(fg=status_colors.get(status, COLORS['status_offline']))


# ═══════════════════════════════════════════════════════════════
# STATS CARD
# ═══════════════════════════════════════════════════════════════

class StatsCard(tk.Frame):
    """Stats display card with icon, label, and value."""
    
    def __init__(self, parent, icon: str, label: str, value: str = "0", **kwargs):
        super().__init__(parent, bg=COLORS['bg_light'], **kwargs)
        
        self.icon_label = tk.Label(self, text=icon, font=FONTS['body'],
                                   fg=COLORS['accent_cyan'], bg=COLORS['bg_light'])
        self.icon_label.pack(side='left', padx=8, pady=5)
        
        self.text_label = tk.Label(self, text=label, font=FONTS['small'],
                                   fg=COLORS['text_secondary'], bg=COLORS['bg_light'])
        self.text_label.pack(side='left')
        
        self.value_label = tk.Label(self, text=value, font=FONTS['body_bold'],
                                    fg=COLORS['accent_cyan'], bg=COLORS['bg_light'])
        self.value_label.pack(side='right', padx=8)
    
    def set_value(self, value: str):
        """Update the displayed value."""
        self.value_label.configure(text=value)


# ═══════════════════════════════════════════════════════════════
# GRADIENT HEADER
# ═══════════════════════════════════════════════════════════════

class GradientHeader(tk.Frame):
    """Header with title and gradient-like effect."""
    
    def __init__(self, parent, title: str, subtitle: str = None, **kwargs):
        super().__init__(parent, bg=COLORS['bg_medium'], **kwargs)
        
        # Content frame
        content = tk.Frame(self, bg=COLORS['bg_medium'])
        content.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Title
        tk.Label(content, text=title, font=FONTS['header'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_medium']).pack(side='left')
        
        # Subtitle (optional)
        if subtitle:
            tk.Label(content, text=subtitle, font=FONTS['small'],
                    fg=COLORS['text_secondary'], bg=COLORS['bg_medium']).pack(side='left', padx=15)
        
        # Glow line
        tk.Frame(self, bg=COLORS['accent_cyan'], height=2).pack(fill='x', side='bottom')


# ═══════════════════════════════════════════════════════════════
# DIALOG BOX
# ═══════════════════════════════════════════════════════════════

class CyberDialog(tk.Toplevel):
    """Styled dialog box for the chat application."""
    
    def __init__(self, parent, title: str, width: int = 350, height: int = 150):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg=COLORS['bg_card'])
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
        
        self.result = None
    
    def add_content(self, widget_creator: Callable):
        """Add content to the dialog using a widget creator function."""
        content_frame = tk.Frame(self, bg=COLORS['bg_card'], padx=20, pady=15)
        content_frame.pack(fill='both', expand=True)
        widget_creator(content_frame)


# ═══════════════════════════════════════════════════════════════
# EMOJI PICKER (Simplified)
# ═══════════════════════════════════════════════════════════════

class EmojiPicker(tk.Toplevel):
    """Simple emoji picker popup."""
    
    EMOJIS = [
        '😊', '😄', '😂', '🤣', '😉', '😍', '🥰', '😘',
        '😎', '🤔', '😅', '😢', '😭', '😤', '😡', '🤯',
        '👍', '👎', '👏', '🙌', '🤝', '✌️', '🤟', '👋',
        '❤️', '🔥', '⭐', '✨', '💯', '🎉', '🎊', '🚀',
        '✅', '❌', '⚡', '💬', '🔒', '🔑', '👀', '💪'
    ]
    
    def __init__(self, parent, on_select: Callable):
        super().__init__(parent)
        
        self.title("Emoji")
        self.geometry("280x180")
        self.configure(bg=COLORS['bg_card'])
        self.transient(parent)
        
        self.on_select = on_select
        
        # Position near parent
        x = parent.winfo_rootx() + parent.winfo_width()
        y = parent.winfo_rooty()
        self.geometry(f"+{x}+{y}")
        
        # Create grid of emoji buttons
        frame = tk.Frame(self, bg=COLORS['bg_card'], padx=5, pady=5)
        frame.pack(fill='both', expand=True)
        
        for i, emoji in enumerate(self.EMOJIS):
            btn = tk.Button(frame, text=emoji, font=('Segoe UI Emoji', 14),
                           bg='#ffffff', fg='#000000',
                           activebackground='#e0e0e0',
                           relief='flat', cursor='hand2', width=2,
                           command=lambda e=emoji: self._select(e))
            btn.grid(row=i // 8, column=i % 8, padx=1, pady=1)
        
        # Grab focus and close when focus is lost
        self.grab_set()
        self.focus_force()
        self.bind('<Escape>', lambda e: self.destroy())
        self.bind('<FocusOut>', self._on_focus_out)
    
    def _on_focus_out(self, event):
        """Close picker when focus is lost (clicked outside)."""
        # Small delay to allow button clicks to register
        self.after(100, self._check_focus)
    
    def _check_focus(self):
        """Check if we should close."""
        try:
            if not self.focus_get():
                self.destroy()
        except tk.TclError:
            pass  # Window already destroyed
    
    def _select(self, emoji: str):
        """Handle emoji selection."""
        self.on_select(emoji)
        self.destroy()

