#!/usr/bin/env python3
"""
Simple Print Server - System Tray Version
Runs the print server in the system tray with a menu
"""

import threading
import webbrowser
import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Try to import pystray for system tray
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("=" * 60)
    print("System Tray Mode Not Available")
    print("=" * 60)
    print("System tray mode is OPTIONAL - console mode works perfectly!")
    print()
    print("To enable system tray mode (optional):")
    print("  Run: install-tray.bat")
    print("  Or: pip install pystray pillow")
    print()
    print("If Pillow installation fails, see TROUBLESHOOTING.md")
    print("=" * 60)
    print("Starting in console mode...")
    print()

# Import the Flask app from server.py
try:
    # We'll run the server in a separate thread
    from server import app, ESCPOS_AVAILABLE
except ImportError:
    print("Error: Could not import server module. Make sure server.py is in the same directory.")
    sys.exit(1)

# Global variables
server_thread = None
server_running = False
icon = None
log_file_path = None

# Setup logging
def setup_logging():
    """Setup logging to file"""
    global log_file_path
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file_path = log_dir / f'server-{timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)  # Also log to console
        ]
    )
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()


def create_tray_icon():
    """Create a simple tray icon image"""
    # Create a 64x64 image with a printer icon
    image = Image.new('RGB', (64, 64), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simple printer icon
    # Printer body
    draw.rectangle([10, 20, 54, 50], fill='black', outline='black')
    # Paper
    draw.rectangle([20, 10, 44, 20], fill='white', outline='black')
    # Button
    draw.ellipse([45, 25, 50, 30], fill='white', outline='black')
    
    return image


def start_server():
    """Start the Flask server in a separate thread"""
    global server_thread, server_running, icon
    
    if server_running:
        return
    
    def run_server():
        global server_running
        server_running = True
        try:
            logger.info("=" * 60)
            logger.info("Simple Print Server - Starting")
            logger.info("=" * 60)
            logger.info(f"ESC/POS Library Available: {ESCPOS_AVAILABLE}")
            logger.info("Server starting on http://127.0.0.1:8888")
            logger.info("=" * 60)
            print("Print server started on http://127.0.0.1:8888")
            app.run(host='127.0.0.1', port=8888, debug=False, use_reloader=False)
        except Exception as e:
            logger.error(f"Server error: {e}")
            print(f"Server error: {e}")
        finally:
            server_running = False
            logger.info("Server stopped")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()


def stop_server():
    """Stop the Flask server"""
    global server_running, icon
    # Note: This is a workaround - Flask dev server doesn't have clean shutdown
    # The server will stop when the process exits
    server_running = False
    print("Print server will stop on next restart")
    if icon:
        icon.update_menu()


def open_example_page(icon_item=None, item=None):
    """Open the example HTML page in default browser"""
    example_path = Path(__file__).parent / 'example.html'
    if example_path.exists():
        webbrowser.open(f'file:///{example_path.absolute()}')
    else:
        webbrowser.open('http://localhost:8888')


def open_server_status(icon_item=None, item=None):
    """Open server health check page"""
    webbrowser.open('http://localhost:8888/health')


def open_log_file(icon_item=None, item=None):
    """Open log file in default text editor or show in window"""
    global log_file_path
    
    if log_file_path and log_file_path.exists():
        try:
            # Try to open with default text editor (Windows)
            os.startfile(str(log_file_path))
        except AttributeError:
            # For non-Windows systems
            import subprocess
            import platform
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', str(log_file_path)])
            else:  # Linux
                subprocess.call(['xdg-open', str(log_file_path)])
        except Exception as e:
            logger.error(f"Failed to open log file: {e}")
            # Fallback: show in message box
            show_log_in_window()
    else:
        # Show error message
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Log File", "Log file not found or not created yet.")
        root.destroy()


def show_log_in_window():
    """Show log file content in a window"""
    global log_file_path
    
    import tkinter as tk
    from tkinter import scrolledtext
    
    root = tk.Tk()
    root.title("Server Log")
    root.geometry("900x700")
    
    # Read log file
    log_content = ""
    if log_file_path and log_file_path.exists():
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
                # Show last 2000 lines if too long
                if len(log_content) > 50000:
                    lines = log_content.split('\n')
                    log_content = "... (showing last 2000 lines)\n\n" + "\n".join(lines[-2000:])
        except Exception as e:
            log_content = f"Error reading log file: {e}"
    else:
        log_content = "Log file not found or not created yet."
    
    # Create text widget
    text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=120, height=40, font=('Consolas', 9))
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    text_widget.insert('1.0', log_content)
    text_widget.config(state=tk.DISABLED)
    
    # Add refresh button
    def refresh_log():
        if log_file_path and log_file_path.exists():
            try:
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 50000:
                        lines = content.split('\n')
                        content = "... (showing last 2000 lines)\n\n" + "\n".join(lines[-2000:])
                text_widget.config(state=tk.NORMAL)
                text_widget.delete('1.0', tk.END)
                text_widget.insert('1.0', content)
                text_widget.config(state=tk.DISABLED)
                text_widget.see(tk.END)  # Scroll to bottom
            except Exception as e:
                pass
    
    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)
    
    refresh_btn = tk.Button(button_frame, text="Refresh", command=refresh_log)
    refresh_btn.pack(side=tk.LEFT, padx=5)
    
    close_btn = tk.Button(button_frame, text="Close", command=root.destroy)
    close_btn.pack(side=tk.LEFT, padx=5)
    
    # Auto-scroll to bottom
    text_widget.see(tk.END)
    
    root.mainloop()


def show_about(icon_item=None, item=None):
    """Show about dialog"""
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    about_text = """Simple Print Server
Thermal Printer Bridge

A lightweight alternative to QZ Tray
No certificates required!

Server: http://localhost:8888
ESC/POS Available: """ + str(ESCPOS_AVAILABLE)
    
    messagebox.showinfo("About", about_text)
    root.destroy()


def quit_app(icon_item=None, item=None):
    """Quit the application"""
    global icon, server_running
    
    server_running = False
    if icon:
        icon.stop()
    sys.exit(0)


def create_menu():
    """Create the system tray menu"""
    def get_status_text(menu_item=None):
        return f"Server: {'Running ✓' if server_running else 'Stopped ✗'}"
    
    def can_start(menu_item=None):
        return not server_running
    
    def can_restart(menu_item=None):
        return server_running
    
    menu_items = [
        pystray.MenuItem(get_status_text, lambda icon_item=None, item=None: None, enabled=False),
        pystray.MenuItem("Start Server", 
                         lambda icon_item=None, item=None: start_server(),
                         default=False,
                         enabled=can_start),
        pystray.MenuItem("Restart Server", 
                         lambda icon_item=None, item=None: start_server(),
                         default=False,
                         enabled=can_restart),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open Example Page", open_example_page),
        pystray.MenuItem("Server Status", open_server_status),
        pystray.MenuItem("View Log", open_log_file),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("About", show_about),
        pystray.MenuItem("Quit", quit_app),
    ]
    return pystray.Menu(*menu_items)


def main():
    """Main function to start the system tray application"""
    global icon
    
    if not TRAY_AVAILABLE:
        print("=" * 60)
        print("Simple Print Server - Thermal Printer Bridge")
        print("=" * 60)
        print(f"ESC/POS Library Available: {ESCPOS_AVAILABLE}")
        print("System tray not available. Starting in console mode...")
        print("Server starting on http://localhost:8888")
        print("=" * 60)
        print("\nTo use system tray, install: pip install pystray pillow")
        print("Press Ctrl+C to stop the server\n")
        app.run(host='127.0.0.1', port=8888, debug=False)
        return
    
    # Create tray icon
    image = create_tray_icon()
    icon = pystray.Icon("Simple Print Server", image, "Simple Print Server", create_menu())
    
    # Start server automatically
    start_server()
    
    logger.info("Simple Print Server running in system tray")
    logger.info(f"Log file: {log_file_path}")
    print("Simple Print Server running in system tray")
    print(f"Log file: {log_file_path}")
    print("Right-click the tray icon for menu")
    print("Server: http://localhost:8888")
    print("Use 'View Log' from tray menu to see server logs")
    print("Press Ctrl+C or use Quit from tray menu to stop")
    
    # Run the tray icon
    try:
        icon.run()
    except KeyboardInterrupt:
        quit_app()


if __name__ == '__main__':
    main()

