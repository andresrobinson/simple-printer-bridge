#!/usr/bin/env python3
"""
Cross-platform installation script for Simple Print Server
"""

import sys
import subprocess
import os

def print_header(text):
    """Print a formatted header"""
    print("=" * 60)
    print(text)
    print("=" * 60)
    print()

def print_step(step, text):
    """Print a step message"""
    print(f"[{step}] {text}")

def check_python():
    """Check if Python is installed and has correct version"""
    print_step("1/3", "Checking Python installation...")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro} found")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("ERROR: Python 3.7 or higher is required!")
        return False
    
    print("✓ Python version OK")
    print()
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    print_step("2/3", "Upgrading pip...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"
        ])
        print("✓ pip upgraded")
        print()
        return True
    except subprocess.CalledProcessError:
        print("⚠ Warning: Failed to upgrade pip, continuing anyway...")
        print()
        return True  # Non-critical, continue anyway

def install_requirements():
    """Install required packages from requirements.txt"""
    print_step("2/3", "Installing Python packages...")
    
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print(f"ERROR: {requirements_file} not found!")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print("✓ Packages installed successfully")
        print()
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install packages!")
        print(f"Exit code: {e.returncode}")
        print()
        print("Try running with administrator/sudo privileges:")
        if sys.platform == "win32":
            print("  Run as Administrator")
        else:
            print("  sudo python install.py")
        return False

def main():
    """Main installation function"""
    print_header("Simple Print Server - Installation")
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Upgrade pip
    upgrade_pip()
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Success message
    print_step("3/3", "Installation complete!")
    print()
    print_header("Next steps")
    print("1. Start the server: python server.py")
    print("2. Open example.html in your browser")
    print("3. Connect to your printer and start printing!")
    print()
    
    # Platform-specific notes
    if sys.platform == "win32":
        print("Note for Windows users:")
        print("- For USB printers, you may need to install libusb drivers")
        print("- Download Zadig from https://zadig.akeo.ie/")
        print("- Install WinUSB driver for your printer")
    elif sys.platform == "linux":
        print("Note for Linux users:")
        print("- You may need to add your user to the 'lp' group:")
        print("  sudo usermod -a -G lp $USER")
        print("- Then log out and log back in")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)

