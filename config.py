"""
⚡ CYBER CHAT - Configuration Module
TCP/IP Network Project
Students: Adir Buskila & Liav Wizman
"""

# ═══════════════════════════════════════════════════════════════
# NETWORK CONFIGURATION
# ═══════════════════════════════════════════════════════════════

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 12345
MAX_CLIENTS = 50
BUFFER_SIZE = 4096
PING_INTERVAL = 5  # seconds

# ═══════════════════════════════════════════════════════════════
# USER STATUS TYPES
# ═══════════════════════════════════════════════════════════════

STATUS_ONLINE = 'online'
STATUS_AWAY = 'away'
STATUS_BUSY = 'busy'

# ═══════════════════════════════════════════════════════════════
# 🎨 CYBERPUNK COLOR SCHEME
# ═══════════════════════════════════════════════════════════════

COLORS = {
    # Background shades
    'bg_dark': '#0a0a0f',
    'bg_medium': '#12121a', 
    'bg_light': '#1a1a2e',
    'bg_card': '#16213e',
    'bg_hover': '#1f2940',
    
    # Accent colors
    'accent_cyan': '#00fff5',
    'accent_pink': '#ff00ff',
    'accent_purple': '#7b2cbf',
    'accent_blue': '#0077ff',
    'accent_green': '#00ff88',
    'accent_orange': '#ff6600',
    'accent_red': '#ff3366',
    'accent_yellow': '#ffcc00',
    
    # Text colors
    'text_primary': '#ffffff',
    'text_secondary': '#8892b0',
    'text_dim': '#495670',
    
    # Status colors
    'status_online': '#00ff88',
    'status_away': '#ffcc00',
    'status_busy': '#ff3366',
    'status_offline': '#495670',
    
    # UI elements
    'border': '#233554',
    'border_glow': '#00fff540',
    'shadow': '#00000080',
}

# ═══════════════════════════════════════════════════════════════
# FONTS
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# ASCII ART LOGO
# ═══════════════════════════════════════════════════════════════

LOGO = """
   ██████╗██╗   ██╗██████╗ ███████╗██████╗      ██████╗██╗  ██╗ █████╗ ████████╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██╔════╝██║  ██║██╔══██╗╚══██╔══╝
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ██║     ███████║███████║   ██║   
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██║     ██╔══██║██╔══██║   ██║   
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ╚██████╗██║  ██║██║  ██║   ██║   
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
"""

# ═══════════════════════════════════════════════════════════════
# ADMIN CONFIGURATION
# ═══════════════════════════════════════════════════════════════

ADMIN_PASSWORD = "admin123"  # For server admin commands

# ═══════════════════════════════════════════════════════════════
# FILE PATHS
# ═══════════════════════════════════════════════════════════════

LOG_FILE = "cyber_chat.log"
HISTORY_DIR = "chat_history"

