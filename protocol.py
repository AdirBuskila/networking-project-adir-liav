"""
⚡ CYBER CHAT - Protocol Module
Message encryption and protocol handling
Students: Adir Buskila & Liav Wizman
"""

import base64
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any

from config import ENCRYPTION_KEY, ENABLE_ENCRYPTION, MSG_TYPES


# ═══════════════════════════════════════════════════════════════
# SIMPLE XOR ENCRYPTION (No external dependencies!)
# For demonstration - shows understanding of encryption concepts
# ═══════════════════════════════════════════════════════════════

class CryptoEngine:
    """
    Simple XOR-based encryption for the chat.
    In production, you'd use AES from cryptography library.
    This demonstrates the concept without external dependencies.
    """
    
    def __init__(self, key: bytes = ENCRYPTION_KEY):
        # Expand key using SHA-256 for better security
        self.key = hashlib.sha256(key).digest()
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a message and return base64 encoded string."""
        if not ENABLE_ENCRYPTION:
            return plaintext
            
        data = plaintext.encode('utf-8')
        encrypted = bytes(b ^ self.key[i % len(self.key)] for i, b in enumerate(data))
        return base64.b64encode(encrypted).decode('ascii')
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64 encoded encrypted message."""
        if not ENABLE_ENCRYPTION:
            return ciphertext
            
        try:
            encrypted = base64.b64decode(ciphertext.encode('ascii'))
            decrypted = bytes(b ^ self.key[i % len(self.key)] for i, b in enumerate(encrypted))
            return decrypted.decode('utf-8')
        except Exception:
            return ciphertext  # Return as-is if decryption fails


# ═══════════════════════════════════════════════════════════════
# MESSAGE CLASS
# ═══════════════════════════════════════════════════════════════

class Message:
    """
    Structured message class for the chat protocol.
    Provides serialization, timestamps, and type safety.
    """
    
    def __init__(self, 
                 msg_type: str,
                 content: str,
                 sender: Optional[str] = None,
                 recipient: Optional[str] = None,
                 timestamp: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.type = msg_type
        self.content = content
        self.sender = sender
        self.recipient = recipient
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'type': self.type,
            'content': self.content,
            'sender': self.sender,
            'recipient': self.recipient,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            msg_type=data.get('type', 'MSG'),
            content=data.get('content', ''),
            sender=data.get('sender'),
            recipient=data.get('recipient'),
            timestamp=data.get('timestamp'),
            metadata=data.get('metadata', {})
        )
    
    def serialize(self, crypto: Optional[CryptoEngine] = None) -> bytes:
        """Serialize message to bytes for network transmission."""
        json_str = json.dumps(self.to_dict())
        if crypto:
            json_str = crypto.encrypt(json_str)
        return (json_str + '\n').encode('utf-8')
    
    @classmethod
    def deserialize(cls, data: bytes, crypto: Optional[CryptoEngine] = None) -> 'Message':
        """Deserialize bytes to message."""
        json_str = data.decode('utf-8').strip()
        if crypto:
            json_str = crypto.decrypt(json_str)
        return cls.from_dict(json.loads(json_str))
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.type}: {self.content}"


# ═══════════════════════════════════════════════════════════════
# PROTOCOL HELPERS
# ═══════════════════════════════════════════════════════════════

class Protocol:
    """Helper class for creating common message types."""
    
    def __init__(self, use_encryption: bool = ENABLE_ENCRYPTION):
        self.crypto = CryptoEngine() if use_encryption else None
    
    # ─────────────────────────────────────────────────────────────
    # Message Creators
    # ─────────────────────────────────────────────────────────────
    
    def welcome(self, prompt: str = "Username: ") -> bytes:
        """Create welcome message."""
        return Message(MSG_TYPES['WELCOME'], prompt).serialize(self.crypto)
    
    def ok(self, content: str) -> bytes:
        """Create OK response."""
        return Message(MSG_TYPES['OK'], content).serialize(self.crypto)
    
    def error(self, content: str) -> bytes:
        """Create error message."""
        return Message(MSG_TYPES['ERROR'], content).serialize(self.crypto)
    
    def chat_message(self, sender: str, content: str, recipient: Optional[str] = None) -> bytes:
        """Create chat message."""
        return Message(
            MSG_TYPES['MSG'], 
            content, 
            sender=sender, 
            recipient=recipient
        ).serialize(self.crypto)
    
    def sent_confirmation(self, content: str, recipient: Optional[str] = None) -> bytes:
        """Create sent confirmation."""
        return Message(
            MSG_TYPES['SENT'], 
            content, 
            recipient=recipient
        ).serialize(self.crypto)
    
    def system(self, content: str) -> bytes:
        """Create system message."""
        return Message(MSG_TYPES['SYSTEM'], content).serialize(self.crypto)
    
    def users_list(self, users: list, statuses: Optional[dict] = None) -> bytes:
        """Create users list message."""
        return Message(
            MSG_TYPES['USERS'], 
            ','.join(users),
            metadata={'statuses': statuses or {}}
        ).serialize(self.crypto)
    
    def typing(self, username: str) -> bytes:
        """Create typing indicator."""
        return Message(MSG_TYPES['TYPING'], '', sender=username).serialize(self.crypto)
    
    def stop_typing(self, username: str) -> bytes:
        """Create stop typing indicator."""
        return Message(MSG_TYPES['STOP_TYPING'], '', sender=username).serialize(self.crypto)
    
    def ping(self) -> bytes:
        """Create ping message."""
        return Message(
            MSG_TYPES['PING'], 
            '', 
            metadata={'sent_at': datetime.now().timestamp()}
        ).serialize(self.crypto)
    
    def pong(self, ping_time: float) -> bytes:
        """Create pong response."""
        return Message(
            MSG_TYPES['PONG'], 
            '',
            metadata={'ping_time': ping_time, 'pong_time': datetime.now().timestamp()}
        ).serialize(self.crypto)
    
    def status_update(self, username: str, status: str) -> bytes:
        """Create status update message."""
        return Message(
            MSG_TYPES['STATUS'], 
            status, 
            sender=username
        ).serialize(self.crypto)
    
    def kick(self, username: str, reason: str = "Kicked by admin") -> bytes:
        """Create kick message."""
        return Message(
            MSG_TYPES['KICK'], 
            reason,
            recipient=username
        ).serialize(self.crypto)
    
    def broadcast(self, content: str, from_admin: bool = False) -> bytes:
        """Create broadcast message."""
        return Message(
            MSG_TYPES['BROADCAST'], 
            content,
            metadata={'from_admin': from_admin}
        ).serialize(self.crypto)
    
    # ─────────────────────────────────────────────────────────────
    # Message Parser
    # ─────────────────────────────────────────────────────────────
    
    def parse(self, data: bytes) -> Optional[Message]:
        """Parse received data into a Message object."""
        try:
            return Message.deserialize(data, self.crypto)
        except json.JSONDecodeError:
            # Fall back to legacy format: TYPE|CONTENT
            try:
                text = data.decode('utf-8').strip()
                if '|' in text:
                    parts = text.split('|', 1)
                    return Message(parts[0], parts[1] if len(parts) > 1 else '')
                return Message('MSG', text)
            except Exception:
                return None
        except Exception:
            return None


# ═══════════════════════════════════════════════════════════════
# LEGACY PROTOCOL SUPPORT
# For backwards compatibility with simple TYPE|CONTENT format
# ═══════════════════════════════════════════════════════════════

class LegacyProtocol:
    """Simple TYPE|CONTENT protocol for basic operation."""
    
    @staticmethod
    def encode(msg_type: str, content: str) -> bytes:
        """Encode a message in legacy format."""
        return f"{msg_type}|{content}\n".encode('utf-8')
    
    @staticmethod
    def decode(data: bytes) -> tuple:
        """Decode a legacy format message. Returns (type, content)."""
        text = data.decode('utf-8').strip()
        if '|' in text:
            parts = text.split('|', 1)
            return (parts[0], parts[1] if len(parts) > 1 else '')
        return ('MSG', text)


# ═══════════════════════════════════════════════════════════════
# TEXT FORMATTING (for rich messages)
# ═══════════════════════════════════════════════════════════════

class TextFormatter:
    """Parse and apply text formatting like **bold** and *italic*."""
    
    FORMATS = {
        'bold': ('**', '**'),
        'italic': ('*', '*'),
        'code': ('`', '`'),
        'underline': ('__', '__'),
    }
    
    @staticmethod
    def parse_formatting(text: str) -> list:
        """
        Parse text and return list of (text, format_type) tuples.
        """
        segments = []
        current_text = ""
        i = 0
        
        while i < len(text):
            # Check for formatting markers
            found_format = False
            for fmt_name, (start, end) in TextFormatter.FORMATS.items():
                if text[i:].startswith(start):
                    # Find closing marker
                    end_pos = text.find(end, i + len(start))
                    if end_pos != -1:
                        # Save current plain text
                        if current_text:
                            segments.append((current_text, 'normal'))
                            current_text = ""
                        # Add formatted text
                        formatted_text = text[i + len(start):end_pos]
                        segments.append((formatted_text, fmt_name))
                        i = end_pos + len(end)
                        found_format = True
                        break
            
            if not found_format:
                current_text += text[i]
                i += 1
        
        if current_text:
            segments.append((current_text, 'normal'))
        
        return segments if segments else [(text, 'normal')]

