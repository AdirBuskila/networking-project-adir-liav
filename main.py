"""
⚡ CYBER CHAT - Main Entry Point
TCP/IP Network Project
Students: Adir Buskila & Liav Weizman

Run this file to launch the application.
Choose between Server or Client mode.

Usage:
    python main.py           # Opens launcher GUI
    python main.py server    # Directly start server
    python main.py client    # Directly start client
"""

import sys
import tkinter as tk
from tkinter import ttk

from config import COLORS, FONTS, LOGO, DEFAULT_HOST, DEFAULT_PORT


# ═══════════════════════════════════════════════════════════════
# CYBER LAUNCHER
# ═══════════════════════════════════════════════════════════════

class CyberLauncher:
    """
    Main launcher application.
    Provides a beautiful GUI to choose between Server and Client modes.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚡ CYBER CHAT")
        self.root.geometry("600x500")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.resizable(False, False)
        
        # Center on screen
        self.center_window()
        
        self.setup_ui()
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup the launcher UI."""
        
        # ═══ HEADER DECORATION ═══
        header_line = tk.Frame(self.root, bg=COLORS['accent_cyan'], height=3)
        header_line.pack(fill='x')
        
        # ═══ MAIN CARD ═══
        card = tk.Frame(self.root, bg=COLORS['bg_card'])
        card.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Title section
        title_frame = tk.Frame(card, bg=COLORS['bg_card'])
        title_frame.pack(pady=(30, 0))
        
        # Main title with glow effect (simulated)
        tk.Label(title_frame, text="⚡",
                font=('Segoe UI Emoji', 40),
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack()
        
        tk.Label(title_frame, text="CYBER CHAT",
                font=('Consolas', 42, 'bold'),
                fg=COLORS['accent_cyan'], bg=COLORS['bg_card']).pack()
        
        tk.Label(title_frame, text="TCP/IP Network Project v2.0",
                font=FONTS['body'],
                fg=COLORS['text_secondary'], bg=COLORS['bg_card']).pack(pady=(5, 0))
        
        # Authors
        authors_frame = tk.Frame(card, bg=COLORS['bg_card'])
        authors_frame.pack(pady=15)
        
        tk.Label(authors_frame, text="by ",
                font=FONTS['small'],
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(side='left')
        tk.Label(authors_frame, text="Adir Buskila",
                font=FONTS['small_bold'],
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(side='left')
        tk.Label(authors_frame, text=" & ",
                font=FONTS['small'],
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(side='left')
        tk.Label(authors_frame, text="Liav Weizman",
                font=FONTS['small_bold'],
                fg=COLORS['accent_pink'], bg=COLORS['bg_card']).pack(side='left')
        
        # Separator
        sep_frame = tk.Frame(card, bg=COLORS['bg_card'])
        sep_frame.pack(fill='x', padx=50, pady=20)
        
        tk.Frame(sep_frame, bg=COLORS['border'], height=1).pack(fill='x')
        tk.Label(sep_frame, text=" CHOOSE MODE ",
                font=FONTS['small'],
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).place(relx=0.5, rely=0.5, anchor='center')
        
        # ═══ BUTTONS ═══
        buttons_frame = tk.Frame(card, bg=COLORS['bg_card'])
        buttons_frame.pack(pady=20)
        
        # Server button
        server_frame = tk.Frame(buttons_frame, bg=COLORS['bg_card'])
        server_frame.pack(pady=10)
        
        server_btn = tk.Button(
            server_frame,
            text="🖥️  START SERVER",
            font=('Consolas', 16, 'bold'),
            bg=COLORS['accent_green'],
            fg=COLORS['bg_dark'],
            activebackground=COLORS['accent_cyan'],
            activeforeground=COLORS['bg_dark'],
            relief='flat',
            cursor='hand2',
            width=22,
            height=2,
            command=self.start_server
        )
        server_btn.pack()
        
        tk.Label(server_frame, text="Host a chat room for others to join",
                font=FONTS['tiny'],
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(pady=(5, 0))
        
        # Client button
        client_frame = tk.Frame(buttons_frame, bg=COLORS['bg_card'])
        client_frame.pack(pady=10)
        
        client_btn = tk.Button(
            client_frame,
            text="💬  JOIN AS CLIENT",
            font=('Consolas', 16, 'bold'),
            bg=COLORS['accent_purple'],
            fg=COLORS['text_primary'],
            activebackground=COLORS['accent_pink'],
            activeforeground=COLORS['text_primary'],
            relief='flat',
            cursor='hand2',
            width=22,
            height=2,
            command=self.start_client
        )
        client_btn.pack()
        
        tk.Label(client_frame, text="Connect to an existing server",
                font=FONTS['tiny'],
                fg=COLORS['text_dim'], bg=COLORS['bg_card']).pack(pady=(5, 0))
        
        # ═══ FOOTER INFO ═══
        footer = tk.Frame(card, bg=COLORS['bg_card'])
        footer.pack(side='bottom', pady=20)
        
        info_frame = tk.Frame(footer, bg=COLORS['bg_light'], padx=15, pady=8)
        info_frame.pack()
        
        tk.Label(info_frame, text="💡",
                font=FONTS['small'],
                fg=COLORS['accent_cyan'], bg=COLORS['bg_light']).pack(side='left')
        tk.Label(info_frame, text=f" Default: {DEFAULT_HOST}:{DEFAULT_PORT}  •  Start SERVER first!",
                font=FONTS['tiny'],
                fg=COLORS['text_secondary'], bg=COLORS['bg_light']).pack(side='left')
        
        # Features list
        features_frame = tk.Frame(card, bg=COLORS['bg_card'])
        features_frame.pack(pady=10)
        
        features = [
            "🔐 Encrypted Messages",
            "👥 User Status",
            "🔒 Private DMs",
            "📊 Live Stats"
        ]
        
        for i, feature in enumerate(features):
            tk.Label(features_frame, text=feature,
                    font=FONTS['tiny'],
                    fg=COLORS['text_dim'], bg=COLORS['bg_card']).grid(
                        row=0, column=i, padx=10)
        
        # Bottom glow line
        tk.Frame(self.root, bg=COLORS['accent_pink'], height=3).pack(fill='x', side='bottom')
        
        # Hover effects for buttons
        def on_enter_server(e):
            server_btn.configure(bg=COLORS['accent_cyan'])
        def on_leave_server(e):
            server_btn.configure(bg=COLORS['accent_green'])
        def on_enter_client(e):
            client_btn.configure(bg=COLORS['accent_pink'])
        def on_leave_client(e):
            client_btn.configure(bg=COLORS['accent_purple'])
        
        server_btn.bind('<Enter>', on_enter_server)
        server_btn.bind('<Leave>', on_leave_server)
        client_btn.bind('<Enter>', on_enter_client)
        client_btn.bind('<Leave>', on_leave_client)
    
    def start_server(self):
        """Launch the server application."""
        self.root.destroy()
        from server import CyberServer
        server = CyberServer()
        server.run()
    
    def start_client(self):
        """Launch the client application."""
        self.root.destroy()
        from client import CyberClient
        client = CyberClient()
        client.run()
    
    def run(self):
        """Start the launcher."""
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def main():
    """Main entry point with command-line argument support."""
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'server':
            from server import CyberServer
            print("⚡ Starting CYBER CHAT Server...")
            server = CyberServer()
            server.run()
            
        elif mode == 'client':
            from client import CyberClient
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
║    python main.py           Launch GUI chooser            ║
║    python main.py server    Start server directly         ║
║    python main.py client    Start client directly         ║
║    python main.py --help    Show this help                ║
║                                                           ║
║  Project by: Adir Buskila & Liav Weizman                  ║
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

