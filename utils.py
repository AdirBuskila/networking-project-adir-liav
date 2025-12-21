"""
⚡ CYBER CHAT - Utilities Module
Logging, helpers, and common utilities
Students: Adir Buskila & Liav Wizman
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from config import LOG_FILE, HISTORY_DIR, COLORS


# ═══════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════

class ChatLogger:
    """Custom logger for the chat application."""
    
    def __init__(self, name: str, log_file: str = LOG_FILE):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        if log_file:
            fh = logging.FileHandler(log_file, encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            self.logger.addHandler(fh)
        
        # Console handler (optional)
        # ch = logging.StreamHandler()
        # ch.setLevel(logging.INFO)
        # self.logger.addHandler(ch)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self.logger.warning(msg)
    
    def error(self, msg: str):
        self.logger.error(msg)
    
    def debug(self, msg: str):
        self.logger.debug(msg)


# ═══════════════════════════════════════════════════════════════
# CHAT HISTORY MANAGER
# ═══════════════════════════════════════════════════════════════

class ChatHistory:
    """Manages chat history storage and retrieval."""
    
    def __init__(self, username: str):
        self.username = username
        self.history_dir = Path(HISTORY_DIR)
        self.history_dir.mkdir(exist_ok=True)
        self.messages: List[Dict[str, Any]] = []
    
    def add_message(self, sender: str, content: str, msg_type: str = 'msg',
                    recipient: Optional[str] = None):
        """Add a message to history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'sender': sender,
            'content': content,
            'type': msg_type,
            'recipient': recipient
        }
        self.messages.append(entry)
    
    def save(self) -> str:
        """Save chat history to file. Returns filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.history_dir / f"chat_{self.username}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'username': self.username,
                'saved_at': datetime.now().isoformat(),
                'message_count': len(self.messages),
                'messages': self.messages
            }, f, indent=2, ensure_ascii=False)
        
        return str(filename)
    
    def export_txt(self) -> str:
        """Export chat history as readable text file."""
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
    
    def load(self, filename: str) -> bool:
        """Load chat history from file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.messages = data.get('messages', [])
            return True
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════
# TIME UTILITIES
# ═══════════════════════════════════════════════════════════════

def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format a datetime for display."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%H:%M:%S")


def format_uptime(seconds: int) -> str:
    """Format uptime seconds as HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_relative_time(timestamp: str) -> str:
    """Get relative time string (e.g., '2 minutes ago')."""
    try:
        if 'T' in timestamp:
            dt = datetime.fromisoformat(timestamp)
        else:
            dt = datetime.strptime(timestamp, "%H:%M:%S")
            dt = dt.replace(year=datetime.now().year, 
                          month=datetime.now().month, 
                          day=datetime.now().day)
        
        diff = datetime.now() - dt
        seconds = int(diff.total_seconds())
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            mins = seconds // 60
            return f"{mins} minute{'s' if mins > 1 else ''} ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = seconds // 86400
            return f"{days} day{'s' if days > 1 else ''} ago"
    except Exception:
        return timestamp


# ═══════════════════════════════════════════════════════════════
# STRING UTILITIES
# ═══════════════════════════════════════════════════════════════

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_username(username: str) -> str:
    """Sanitize username - remove special characters."""
    # Allow alphanumeric, underscore, hyphen
    return ''.join(c for c in username if c.isalnum() or c in '_-')[:20]


def parse_command(text: str) -> tuple:
    """
    Parse command text. Returns (command, args) or (None, text) if not a command.
    Commands start with /
    """
    text = text.strip()
    if not text.startswith('/'):
        return (None, text)
    
    parts = text[1:].split(' ', 1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ''
    return (command, args)


# ═══════════════════════════════════════════════════════════════
# NETWORK UTILITIES
# ═══════════════════════════════════════════════════════════════

def parse_address(address: str, default_host: str = '127.0.0.1', 
                  default_port: int = 12345) -> tuple:
    """Parse address string like 'host:port' or just 'host'."""
    try:
        if ':' in address:
            parts = address.split(':')
            return (parts[0] or default_host, int(parts[1]))
        return (address or default_host, default_port)
    except (ValueError, IndexError):
        return (default_host, default_port)


def format_bytes(num_bytes: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


# ═══════════════════════════════════════════════════════════════
# COLOR UTILITIES
# ═══════════════════════════════════════════════════════════════

def get_status_color(status: str) -> str:
    """Get color for user status."""
    status_colors = {
        'online': COLORS['status_online'],
        'away': COLORS['status_away'],
        'busy': COLORS['status_busy'],
        'offline': COLORS['status_offline']
    }
    return status_colors.get(status, COLORS['status_offline'])


def get_user_color(username: str) -> str:
    """Generate a consistent color for a username."""
    # Hash username to get consistent color
    colors = [
        COLORS['accent_cyan'],
        COLORS['accent_pink'],
        COLORS['accent_purple'],
        COLORS['accent_blue'],
        COLORS['accent_green'],
        COLORS['accent_orange'],
    ]
    return colors[hash(username) % len(colors)]


# ═══════════════════════════════════════════════════════════════
# EMOJI UTILITIES
# ═══════════════════════════════════════════════════════════════

EMOJI_SHORTCUTS = {
    ':)': '😊',
    ':(': '😢',
    ':D': '😄',
    ';)': '😉',
    ':P': '😛',
    '<3': '❤️',
    ':fire:': '🔥',
    ':+1:': '👍',
    ':-1:': '👎',
    ':star:': '⭐',
    ':check:': '✅',
    ':x:': '❌',
    ':wave:': '👋',
    ':clap:': '👏',
    ':rocket:': '🚀',
    ':lock:': '🔒',
    ':key:': '🔑',
    ':eyes:': '👀',
    ':thinking:': '🤔',
    ':100:': '💯',
}


def replace_emoji_shortcuts(text: str) -> str:
    """Replace emoji shortcuts with actual emojis."""
    for shortcut, emoji in EMOJI_SHORTCUTS.items():
        text = text.replace(shortcut, emoji)
    return text


# ═══════════════════════════════════════════════════════════════
# SOUND UTILITIES (Optional - Windows only)
# ═══════════════════════════════════════════════════════════════

def play_notification_sound():
    """Play notification sound (Windows only, fails silently otherwise)."""
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_OK)
    except Exception:
        pass  # Silently fail on non-Windows systems


# ═══════════════════════════════════════════════════════════════
# VALIDATION UTILITIES
# ═══════════════════════════════════════════════════════════════

def validate_username(username: str) -> tuple:
    """
    Validate username. Returns (is_valid, error_message).
    """
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
    """
    Validate message. Returns (is_valid, error_message).
    """
    if not message.strip():
        return (False, "Message cannot be empty")
    
    if len(message) > 2000:
        return (False, "Message too long (max 2000 characters)")
    
    return (True, "")

