# Troubleshooting Guide

> 📖 **Other Documentation:**
> - [README.md](README.md) - Installation, usage, and quick start guide
> - [API.md](API.md) - Complete API reference
> - [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute to this project

## Table of Contents

- [Pillow Installation Issues (System Tray Mode)](#pillow-installation-issues-system-tray-mode)
- [Other Common Issues](#other-common-issues)
- [Getting Help](#getting-help)

---

## Pillow Installation Issues (System Tray Mode)

If you're getting errors installing Pillow for system tray mode, here are several solutions:

### Solution 1: Use Pre-built Wheel (Recommended)

```bash
python -m pip install --upgrade pip
python -m pip install --only-binary :all: Pillow
python -m pip install pystray
```

### Solution 2: Install from PyPI with Specific Version

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install Pillow==10.4.0
python -m pip install pystray
```

### Solution 3: Use Conda (if available)

```bash
conda install pillow
pip install pystray
```

### Solution 4: Skip System Tray Mode

**System tray mode is completely optional!** The server works perfectly in console mode:

```bash
# Just use console mode instead
python server.py
# or
start-server.bat
```

Console mode has all the same functionality - it just runs in a terminal window instead of the system tray.

### Solution 5: Use Python 3.11 or 3.12

If you're using Python 3.13, Pillow might not have pre-built wheels yet. Consider using Python 3.11 or 3.12 which have better Pillow support:

1. Install Python 3.11 or 3.12 from python.org
2. Use that Python version for this project
3. Install dependencies normally

---

## Other Common Issues

### "Cannot connect to print server"

- Make sure `server.py` is running
- Check that port 8888 is not blocked by firewall
- Verify the server URL in your JavaScript code

### "Failed to connect to printer"

- Verify your printer's name matches exactly
- For USB printers, ensure drivers are installed
- Check that the printer is powered on and connected
- Try using 'file' type for testing first

### Permission Errors (Linux/macOS)

You may need to add your user to the `lp` group:

```bash
sudo usermod -a -G lp $USER
```

Then log out and log back in.

### Windows USB Printer Issues

For direct USB connection on Windows, you may need to install libusb drivers:

1. Download Zadig from https://zadig.akeo.ie/
2. Install WinUSB driver for your printer
3. Restart your computer

---

## Getting Help

If you continue to have issues:

1. Check that all core dependencies are installed: `pip install -r requirements.txt`
2. Try running in console mode: `python server.py`
3. Check the server console for error messages
4. Verify Python version: `python --version` (3.7+ required)
5. Review the [API Documentation](API.md) for correct usage
6. Check the [README.md](README.md) for installation instructions

**Still need help?**
- Open an issue on [GitHub](https://github.com/andresrobinson/simple-printer-bridge/issues)
- Check existing issues for similar problems

---

## Related Documentation

- [README.md](README.md) - Installation, usage, and quick start guide
- [API.md](API.md) - Complete API reference
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute to this project

