# Simple Print Server - Thermal Printer Bridge

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

A lightweight alternative to QZ Tray for thermal printers that runs on Python. **No certificates or signing required!**

> **Note:** This project is ready for production use. Perfect for store sales systems, POS applications, and any scenario where you need to print from a browser to thermal printers.

## Features

- ✅ Simple Python server (no compilation needed)
- ✅ **Multiple printer support** - Connect and print to multiple printers simultaneously
- ✅ Works with USB, Serial, Network, and File printers
- ✅ Easy-to-use JavaScript client library
- ✅ ESC/POS command support
- ✅ Receipt printing with formatting
- ✅ System tray mode (Windows) - Run in background
- ✅ Auto-start on Windows boot (optional)
- ✅ No certificate requirements
- ✅ Cross-platform (Windows, Linux, macOS)

## Installation

### Quick Install (Recommended)

**Windows:**
- Double-click `install.bat` (or run `install.ps1` in PowerShell)
- Double-click `start-server.bat` to start the server

**Linux/macOS:**
```bash
python install.py
python server.py
```

### Manual Installation

#### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or use the installation scripts:
- **Windows:** `install.bat` or `install.ps1`
- **Cross-platform:** `python install.py`

**Note for Windows users:** 
- You may need to install libusb drivers for USB printers:
  - Download Zadig from https://zadig.akeo.ie/
  - Install WinUSB driver for your printer
- If Pillow installation fails for system tray mode, try:
  ```bash
  python -m pip install --upgrade pip setuptools wheel
  python -m pip install Pillow
  python -m pip install pystray
  ```

#### 2. Start the Print Server

**Option A: System Tray (Recommended)**
- **Note:** System tray mode requires additional dependencies that may have installation issues on some systems
- First install tray dependencies: run `install-tray.bat` (or see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if it fails)
- Double-click `start-server-tray.bat` (or run `start-server-tray.ps1` in PowerShell)
- Server runs in the system tray - right-click the icon for menu options
- **Auto-start on Windows boot:** 
  - Run `add-to-startup.bat` (or `add-to-startup.ps1`) **as Administrator** to add the server to Windows startup
  - The server will start automatically when you log in
  - To remove from startup, run `remove-from-startup.bat` (or `remove-from-startup.ps1`)
- **If tray installation fails:** Just use console mode (Option B) - it works the same!

**Option B: Console Mode**
- Double-click `start-server.bat` (or run `start-server.ps1` in PowerShell)
- Server runs in a console window

**Linux/macOS:**
```bash
# System tray mode (requires: pip install pystray pillow)
python server-tray.py

# Console mode
python server.py
```

**Note:** System tray mode requires additional dependencies:
```bash
pip install pystray pillow
# Or use the provided script:
# Windows: install-tray.bat
# All platforms: pip install -r requirements-tray.txt
```

The server will start on `http://localhost:8888`

#### 3. Open the Example Page

Open `example.html` in your browser and start printing!

## Usage

### Multiple Printer Support

The server supports connecting to **multiple printers simultaneously**. Each printer is identified by a unique `printer_id`. This is perfect for businesses with:
- **Counter/Receipt Printer** - For customer receipts
- **Kitchen/Order Printer** - For kitchen orders
- **Multiple locations** - Different printers for different areas

### Basic JavaScript Usage

```javascript
// Include the client library
<script src="print-client.js"></script>

// Create a printer instance
const printer = new SimplePrintClient('http://localhost:8888');

// Method 1: Connect by printer name/ID (Recommended)
const printers = await printer.listPrinters();
await printer.connectByName(printers[0].id, 'counter');  // Connect first printer as 'counter'
await printer.connectByName(printers[1].id, 'kitchen'); // Connect second printer as 'kitchen'

// Method 2: Manual connection
await printer.connect({
    printer_id: 'counter',
    name: 'Counter Printer',
    type: 'windows',
    config: { printer_name: 'HP LaserJet Pro' }
});

// Print to specific printer
await printer.printText('counter', 'Hello World!', true); // Print to counter printer
await printer.printText('kitchen', 'Order #123', true);  // Print to kitchen printer

// Print receipt to counter printer
await printer.printReceipt('counter', {
    header: 'RECEIPT',
    storeName: 'My Store',
    storeAddress: '123 Main St',
    items: [
        { name: 'Item 1', quantity: 2, price: 10.99 },
        { name: 'Item 2', quantity: 1, price: 5.50 }
    ],
    subtotal: 27.48,
    tax: 2.20,
    total: 29.68,
    footer: 'Thank you!'
});

// Print to both printers simultaneously
const promises = [
    printer.printText('counter', 'Receipt content', true),
    printer.printText('kitchen', 'Order content', true)
];
await Promise.all(promises);

// Disconnect specific printer
await printer.disconnect('counter');

// Disconnect all printers
await printer.disconnect();
```

### Printer Connection Types

#### USB Printer
```javascript
await printer.connect({
    type: 'usb',
    config: {
        vendor_id: 0x04f9,
        product_id: 0x2060
    }
});
```

#### Serial (COM Port) Printer
```javascript
await printer.connect({
    type: 'serial',
    config: {
        port: 'COM3',
        baudrate: 9600
    }
});
```

#### Network Printer
```javascript
await printer.connect({
    type: 'network',
    config: {
        host: '192.168.1.100',
        port: 9100
    }
});
```

#### File Printer (for testing)
```javascript
await printer.connect({
    type: 'file',
    config: {
        file: 'LPT1'  // Windows parallel port
    }
});
```

## API Documentation

For complete API documentation, see [API.md](API.md).

### Quick Reference

**Server Endpoints:**
- `GET /health` - Check server status
- `GET /printer/list` - List all available printers
- `POST /printer/connect-by-name` - Connect to printer by name/ID (recommended)
- `POST /printer/connect` - Connect using manual configuration
- `POST /printer/disconnect` - Disconnect from printer
- `POST /printer/print` - Send print job

**JavaScript Client Methods:**
- `checkHealth()` - Check server status
- `listPrinters()` - List available printers
- `connectByName(nameOrId, printerId)` - Connect to printer by name/ID (recommended)
- `connect(options)` - Connect using manual configuration
- `printText(printerId, text, cut)` - Print text to specific printer
- `printReceipt(printerId, receipt)` - Print formatted receipt to specific printer
- `listConnectedPrinters()` - List all currently connected printers
- `disconnect(printerId)` - Disconnect specific printer (or all if no ID provided)

## Finding Your Printer's Vendor/Product ID

### Windows
1. Open Device Manager
2. Find your printer under "Printers" or "Universal Serial Bus devices"
3. Right-click → Properties → Details
4. Select "Hardware Ids" from the dropdown
5. Look for `VID_XXXX&PID_XXXX` - these are your vendor and product IDs in hex

### Linux
```bash
lsusb
# Look for your printer and note the ID (e.g., 04f9:2060)
```

### macOS
```bash
system_profiler SPUSBDataType
```

## Troubleshooting

### "Cannot connect to print server"
- Make sure `server.py` is running
- Check that port 8888 is not blocked by firewall
- Verify the server URL in your JavaScript code

### "Failed to connect to printer"
- Verify your printer's vendor/product IDs
- For USB printers, ensure drivers are installed (use Zadig on Windows)
- Check that the printer is powered on and connected
- Try using 'file' type for testing first

### Permission Errors (Linux/macOS)
You may need to add your user to the `lp` group:
```bash
sudo usermod -a -G lp $USER
```

## Differences from QZ Tray

- ✅ No Java required
- ✅ No certificate signing
- ✅ Simpler setup
- ✅ Python-based (easier to modify)
- ⚠️ Requires Python to be installed
- ⚠️ Server must be running locally

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built as an alternative to QZ Tray for users who don't need certificate signing
- Uses [python-escpos](https://github.com/python-escpos/python-escpos) for ESC/POS command support
- Inspired by the need for simpler printer integration in web applications

