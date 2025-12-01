#!/usr/bin/env python3
"""
Simple Print Server for Thermal Printers
A lightweight alternative to QZ Tray without certificate requirements
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import json
import platform
import subprocess
import re
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from browser

# Try to import escpos library, fallback to raw printing if not available
try:
    from escpos.printer import Usb, Serial, Network, File
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False
    print("Warning: python-escpos not installed. Using raw printing mode.")

# Global printer instances - dictionary to support multiple printers
# Key: printer_id (string), Value: dict with 'instance', 'type', 'config', 'name'
printers = {}  # {printer_id: {'instance': printer_obj, 'type': str, 'config': dict, 'name': str}}
printer_list_cache = []  # Cache of available printers


def get_printer(printer_type, config):
    """
    Initialize and return a printer instance based on type and configuration.
    
    Args:
        printer_type (str): Type of printer connection. Options:
            - 'usb': Direct USB connection (requires vendor_id and product_id)
            - 'serial': Serial/COM port connection (requires port and baudrate)
            - 'network': Network printer (requires host and port)
            - 'file': File output or Windows parallel port (requires file path)
            - 'windows': Windows system printer by name (requires printer_name)
        config (dict): Configuration dictionary with connection-specific parameters:
            - For 'usb': {'vendor_id': int, 'product_id': int, 'in_ep': int, 'out_ep': int}
            - For 'serial': {'port': str, 'baudrate': int}
            - For 'network': {'host': str, 'port': int}
            - For 'file': {'file': str}
            - For 'windows': {'printer_name': str}
    
    Returns:
        object: Printer instance (WindowsPrinter, Usb, Serial, Network, File, or MockPrinter)
        None: If printer initialization fails
    
    Example:
        >>> printer = get_printer('windows', {'printer_name': 'My Printer'})
        >>> printer = get_printer('usb', {'vendor_id': 0x04f9, 'product_id': 0x2060})
    """
    
    if ESCPOS_AVAILABLE:
        try:
            if printer_type == 'usb':
                # USB printer: vendor_id, product_id
                printer = Usb(config.get('vendor_id', 0x04f9), 
                             config.get('product_id', 0x2060),
                             in_ep=config.get('in_ep', 0x81),
                             out_ep=config.get('out_ep', 0x03))
            elif printer_type == 'serial':
                # Serial printer: port, baudrate
                printer = Serial(config.get('port', 'COM3'),
                                baudrate=config.get('baudrate', 9600))
            elif printer_type == 'network':
                # Network printer: host, port
                printer = Network(config.get('host', '192.168.1.100'),
                                 port=config.get('port', 9100))
            elif printer_type == 'file':
                # File printer (for testing or raw output)
                printer = File(config.get('file', 'LPT1'))
            elif printer_type == 'windows':
                # Windows system printer by name
                try:
                    import win32print
                    printer_name = config.get('printer_name')
                    if printer_name:
                        # Use custom Windows printer handler
                        printer = WindowsPrinter(printer_name)
                    else:
                        return None
                except ImportError:
                    # Fallback: try to use File type, but warn user
                    print("Warning: pywin32 not available. Windows printer may not work correctly.")
                    printer = File(config.get('printer_name', 'LPT1'))
            else:
                return None
            
            return printer
        except Exception as e:
            print(f"Error initializing printer: {e}")
            return None
    else:
        # Fallback: return a mock printer object
        return MockPrinter()


class MockPrinter:
    """
    Mock printer class for testing when python-escpos is not available.
    
    This class simulates printer operations by printing to console instead of
    sending data to an actual printer. Useful for development and testing.
    
    Methods:
        text(text): Print text to console
        cut(): Simulate paper cut
        close(): No-op cleanup method
    """
    def text(self, text):
        """Print text to console (mock operation)"""
        print(f"[PRINT] {text}")
    
    def cut(self):
        """Simulate paper cut (mock operation)"""
        print("[PRINT] Paper cut")
    
    def close(self):
        """Close printer connection (no-op for mock)"""
        pass


class WindowsPrinter:
    """
    Windows system printer handler using win32print API.
    
    This class handles printing to Windows system printers by name. It buffers
    all print data and sends it in a single print job to avoid creating multiple
    print jobs for multi-line content.
    
    Attributes:
        printer_name (str): Name of the Windows printer
        buffer (bytearray): Internal buffer to collect print data before sending
    
    Methods:
        text(text): Add text to print buffer
        _raw(data): Add raw bytes/ESC-POS commands to buffer
        cut(): Add paper cut command to buffer
        set(**kwargs): Add formatting commands to buffer
        flush(): Send all buffered data to printer in one print job
        close(): Cleanup (no-op, handles are closed after each flush)
    
    Example:
        >>> printer = WindowsPrinter("HP LaserJet")
        >>> printer.text("Hello")
        >>> printer.text("World")
        >>> printer.cut()
        >>> printer.flush()  # Sends everything in one print job
    """
    def __init__(self, printer_name):
        """
        Initialize Windows printer handler.
        
        Args:
            printer_name (str): Name of the Windows printer as it appears in
                               Windows Printers & Scanners settings
        """
        self.printer_name = printer_name
        self.buffer = bytearray()  # Buffer to collect all data before printing
    
    def _add_to_buffer(self, data):
        """Add data to buffer"""
        if isinstance(data, str):
            data = data.encode('utf-8', errors='ignore')
        elif not isinstance(data, bytes):
            data = bytes(data)
        self.buffer.extend(data)
    
    def _flush(self):
        """Send buffered data to printer in one print job"""
        if not self.buffer:
            return
        
        try:
            import win32print
            # Open printer handle for this operation
            handle = win32print.OpenPrinter(self.printer_name)
            try:
                # Send all buffered data in one print job
                win32print.StartDocPrinter(handle, 1, (self.printer_name, None, "RAW"))
                try:
                    win32print.StartPagePrinter(handle)
                    try:
                        win32print.WritePrinter(handle, bytes(self.buffer))
                    finally:
                        win32print.EndPagePrinter(handle)
                finally:
                    win32print.EndDocPrinter(handle)
            finally:
                win32print.ClosePrinter(handle)
            # Clear buffer after successful print
            self.buffer = bytearray()
        except Exception as e:
            self.buffer = bytearray()  # Clear buffer on error
            raise Exception(f"Print error: {e}")
    
    def text(self, text):
        """Add text to buffer (doesn't print immediately)"""
        self._add_to_buffer(text)
    
    def _raw(self, data):
        """Add raw data to buffer (doesn't print immediately)"""
        self._add_to_buffer(data)
    
    def cut(self):
        """Add cut command to buffer"""
        # ESC/POS cut command: ESC i (0x1B 0x69)
        cut_command = bytes([0x1B, 0x69])
        self._add_to_buffer(cut_command)
    
    def flush(self):
        """Flush buffer and send all buffered data to printer"""
        self._flush()
    
    def set(self, **kwargs):
        """Set printer options (for compatibility) - adds to buffer"""
        # ESC/POS commands based on kwargs
        commands = []
        
        if 'align' in kwargs:
            align = kwargs['align']
            if align == 'center':
                commands.append(bytes([0x1B, 0x61, 0x01]))  # ESC a 1
            elif align == 'right':
                commands.append(bytes([0x1B, 0x61, 0x02]))  # ESC a 2
            else:  # left
                commands.append(bytes([0x1B, 0x61, 0x00]))  # ESC a 0
        
        if 'text_type' in kwargs or 'font' in kwargs:
            # Font size commands
            text_type = kwargs.get('text_type', kwargs.get('font', 'normal'))
            if text_type == 'b' or text_type == 'bold':
                commands.append(bytes([0x1B, 0x45, 0x01]))  # ESC E 1 (bold on)
            else:
                commands.append(bytes([0x1B, 0x45, 0x00]))  # ESC E 0 (bold off)
        
        for cmd in commands:
            self._add_to_buffer(cmd)  # Add to buffer instead of printing immediately
    
    def close(self):
        """Close printer connection (no-op, handles are closed after each operation)"""
        pass


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint to verify server status.
    
    Returns:
        JSON response with:
            - status (str): 'ok' if server is running
            - espos_available (bool): Whether python-escpos library is installed
            - printers_connected (int): Number of printers currently connected
            - printer_ids (list): List of connected printer IDs
    
    Example Response:
        {
            "status": "ok",
            "espos_available": true,
            "printers_connected": 2,
            "printer_ids": ["counter", "kitchen"]
        }
    """
    try:
        return jsonify({
            'status': 'ok',
            'espos_available': ESCPOS_AVAILABLE,
            'printers_connected': len(printers),
            'printer_ids': list(printers.keys())
        })
    except Exception as e:
        if logger:
            logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/printer/connect', methods=['POST'])
def connect_printer():
    """
    Connect to a printer using manual configuration.
    
    Request Body (JSON):
        {
            "printer_id": "counter",  // Unique ID for this printer (optional, auto-generated if not provided)
            "name": "Counter Printer",  // Display name (optional)
            "type": "usb|serial|network|file|windows",
            "config": {
                // Configuration depends on type:
                // USB: {"vendor_id": int, "product_id": int, "in_ep": int, "out_ep": int}
                // Serial: {"port": str, "baudrate": int}
                // Network: {"host": str, "port": int}
                // File: {"file": str}
                // Windows: {"printer_name": str}
            }
        }
    
    Returns:
        JSON response with success status, message, and printer_id
    
    Example Request:
        POST /printer/connect
        {
            "printer_id": "counter",
            "name": "Counter Receipt Printer",
            "type": "windows",
            "config": {"printer_name": "HP LaserJet"}
        }
    
    Example Response:
        {
            "success": true,
            "message": "Connected to windows printer",
            "printer_id": "counter"
        }
    """
    global printers
    
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body must be JSON'
            }), 400
        
        printer_id = data.get('printer_id') or data.get('name', 'printer_' + str(len(printers)))
        printer_name = data.get('name', printer_id)
        printer_type = data.get('type', 'usb')
        printer_config = data.get('config', {})
        
        # If printer_id already exists, disconnect it first (auto-reconnect)
        if printer_id in printers:
            if logger:
                logger.info(f"Printer '{printer_id}' already connected. Disconnecting and reconnecting...")
            printer_info = printers[printer_id]
            try:
                if hasattr(printer_info['instance'], 'close'):
                    printer_info['instance'].close()
            except:
                pass  # Ignore errors when closing
            del printers[printer_id]
        
        printer_instance = get_printer(printer_type, printer_config)
        
        if printer_instance:
            printers[printer_id] = {
                'instance': printer_instance,
                'type': printer_type,
                'config': printer_config,
                'name': printer_name
            }
            
            if logger:
                logger.info(f"Printer connected: id={printer_id}, name={printer_name}, type={printer_type}")
            
            return jsonify({
                'success': True,
                'message': f'Connected to {printer_name}',
                'printer_id': printer_id,
                'printer_name': printer_name
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to printer'
            }), 400
            
    except Exception as e:
        if logger:
            logger.error(f"Connection error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/printer/disconnect', methods=['POST'])
def disconnect_printer():
    """
    Disconnect from a specific printer or all printers.
    
    Request Body (JSON):
        {
            "printer_id": "counter"  // Optional: specific printer ID. If omitted, disconnects all.
        }
    
    Returns:
        JSON response with success status and message
    
    Example Request:
        POST /printer/disconnect
        {
            "printer_id": "counter"
        }
    
    Example Response:
        {
            "success": true,
            "message": "Printer 'counter' disconnected"
        }
    """
    global printers
    
    try:
        data = request.json or {}
        printer_id = data.get('printer_id')
        
        if printer_id:
            # Disconnect specific printer
            if printer_id in printers:
                printer_info = printers[printer_id]
                if hasattr(printer_info['instance'], 'close'):
                    printer_info['instance'].close()
                del printers[printer_id]
                
                if logger:
                    logger.info(f"Printer disconnected: id={printer_id}")
                
                return jsonify({
                    'success': True,
                    'message': f'Printer "{printer_id}" disconnected'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Printer "{printer_id}" not found'
                }), 404
        else:
            # Disconnect all printers
            disconnected_count = 0
            for pid, printer_info in list(printers.items()):
                if hasattr(printer_info['instance'], 'close'):
                    printer_info['instance'].close()
                disconnected_count += 1
            
            printers.clear()
            
            if logger:
                logger.info(f"All printers disconnected: {disconnected_count} printers")
            
            return jsonify({
                'success': True,
                'message': f'All printers disconnected ({disconnected_count} printers)'
            })
            
    except Exception as e:
        if logger:
            logger.error(f"Disconnect error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/printer/print', methods=['POST'])
def print_data():
    """
    Send print job to the connected printer.
    
    Request Body (JSON):
        {
            "type": "text|raw|escpos",
            "data": "string or array",  // For 'text' or 'raw' type
            "commands": [...],      // For 'escpos' type
            "cut": boolean           // Auto-cut paper after printing
        }
    
    Print Types:
        - 'text': Simple text printing (data should be a string)
        - 'raw': Raw ESC/POS commands (data can be hex string or byte array)
        - 'escpos': Structured ESC/POS commands (commands array with actions)
    
    ESC/POS Commands Format:
        [
            {"action": "text", "data": "Hello"},
            {"action": "set", "attribute": "align", "value": "center"},
            {"action": "cut"}
        ]
    
    Returns:
        JSON response with success status and message
    
    Example Request:
        POST /printer/print
        {
            "type": "text",
            "data": "Hello World",
            "cut": true
        }
    
    Example Response:
        {
            "success": true,
            "message": "Print job sent successfully"
        }
    """
    global printers
    
    # Try to get logger, fallback to print if not available
    try:
        log = logging.getLogger(__name__)
    except:
        log = None
    
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body must be JSON'
            }), 400
        
        printer_id = data.get('printer_id')
        
        if not printer_id:
            return jsonify({
                'success': False,
                'message': 'printer_id is required. Specify which printer to use.'
            }), 400
        
        if printer_id not in printers:
            return jsonify({
                'success': False,
                'message': f'Printer "{printer_id}" not connected. Connect it first using /printer/connect or /printer/connect-by-name.'
            }), 404
        
        printer_info = printers[printer_id]
        printer_instance = printer_info['instance']
        print_type = data.get('type', 'text')  # text, raw, escpos
        
        if log:
            log.info(f"Print job received: printer_id={printer_id}, type={print_type}, cut={data.get('cut', False)}")
        
        if print_type == 'text':
            # Simple text printing
            text = data.get('data', '')
            printer_instance.text(text)
            # Don't flush yet if cut is requested - wait until after cut
            if not data.get('cut', False):
                # Flush buffer if using WindowsPrinter
                if hasattr(printer_instance, 'flush'):
                    printer_instance.flush()
            
        elif print_type == 'raw':
            # Raw ESC/POS commands (hex string or byte array)
            raw_data = data.get('data', '')
            if isinstance(raw_data, str):
                # Convert hex string to bytes
                if raw_data.startswith('0x') or ' ' in raw_data:
                    # Hex string format
                    bytes_data = bytes.fromhex(raw_data.replace('0x', '').replace(' ', ''))
                else:
                    # Assume it's already a hex string
                    bytes_data = bytes.fromhex(raw_data)
            else:
                bytes_data = bytes(raw_data)
            
            # Use _raw method if available (WindowsPrinter or escpos)
            if hasattr(printer_instance, '_raw'):
                printer_instance._raw(bytes_data)
                # Don't flush yet if cut is requested - wait until after cut
                if not data.get('cut', False):
                    # Flush buffer if using WindowsPrinter
                    if hasattr(printer_instance, 'flush'):
                        printer_instance.flush()
            elif hasattr(printer_instance, 'raw'):
                printer_instance.raw(bytes_data)
            else:
                # Fallback: encode as text
                try:
                    printer_instance.text(bytes_data.decode('latin1', errors='ignore'))
                    if not data.get('cut', False):
                        if hasattr(printer_instance, 'flush'):
                            printer_instance.flush()
                except:
                    printer_instance.text(str(bytes_data))
                    if not data.get('cut', False):
                        if hasattr(printer_instance, 'flush'):
                            printer_instance.flush()
            
        elif print_type == 'escpos':
            # ESC/POS commands using the library
            commands = data.get('commands', [])
            for cmd in commands:
                if cmd['action'] == 'text':
                    printer_instance.text(cmd.get('data', ''))
                elif cmd['action'] == 'cut':
                    printer_instance.cut()
                elif cmd['action'] == 'set':
                    attr = cmd.get('attribute')
                    value = cmd.get('value')
                    if attr == 'align':
                        printer_instance.set(align=value)
                    elif attr == 'font':
                        printer_instance.set(font=value)
                    elif attr == 'text_size':
                        printer_instance.set(text_type=value)
                    # Add more attributes as needed
            
            # Flush buffer if using WindowsPrinter (send all commands in one job)
            if hasattr(printer_instance, 'flush'):
                printer_instance.flush()
        
        # Auto-cut if requested
        if data.get('cut', False):
            printer_instance.cut()
        
        # Flush buffer once at the end (sends all data including cut in one job)
        if hasattr(printer_instance, 'flush'):
            printer_instance.flush()
        
        if log:
            log.info(f"Print job sent successfully to printer '{printer_id}'")
        
        return jsonify({
            'success': True,
            'message': f'Print job sent successfully to {printer_info["name"]}'
        })
        
    except Exception as e:
        if log:
            log.error(f"Print error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Print error: {str(e)}'
        }), 500


def get_windows_printers():
    """Get list of installed printers on Windows"""
    printers = []
    
    # Try using win32print (best method)
    try:
        import win32print
        import win32api
        
        printer_list = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        )
        
        for printer_info in printer_list:
            printer_name = printer_info[2]
            
            # Get printer details
            try:
                printer_handle = win32print.OpenPrinter(printer_name)
                printer_defaults = {"DesiredAccess": win32print.PRINTER_ACCESS_USE}
                printer_details = win32print.GetPrinter(printer_handle, 2)
                win32print.ClosePrinter(printer_handle)
                
                port_name = printer_details.get('pPortName', 'Unknown')
                driver_name = printer_details.get('pDriverName', 'Unknown')
                status = printer_details.get('Status', 0)
                
                # Determine connection type
                connection_type = 'unknown'
                if port_name.startswith('USB'):
                    connection_type = 'usb'
                elif port_name.startswith('COM') or port_name.startswith('LPT'):
                    connection_type = 'serial'
                elif ':' in port_name or port_name.startswith('\\\\'):
                    connection_type = 'network'
                
                # Check if printer is ready
                is_ready = status == 0
                
                printers.append({
                    'name': printer_name,
                    'port': port_name,
                    'driver': driver_name,
                    'type': connection_type,
                    'status': 'ready' if is_ready else 'error',
                    'system_printer': True
                })
            except Exception as e:
                # If we can't get details, still add the printer with basic info
                printers.append({
                    'name': printer_name,
                    'port': 'Unknown',
                    'driver': 'Unknown',
                    'type': 'unknown',
                    'status': 'unknown',
                    'system_printer': True,
                    'error': str(e)
                })
        
        return printers
        
    except ImportError:
        # Fallback to PowerShell/WMIC if win32print not available
        try:
            # Try PowerShell command
            ps_command = "Get-Printer | Select-Object Name, PortName, DriverName, PrinterStatus | ConvertTo-Json"
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                import json as json_lib
                try:
                    ps_printers = json_lib.loads(result.stdout)
                    if not isinstance(ps_printers, list):
                        ps_printers = [ps_printers]
                    
                    for p in ps_printers:
                        port = p.get('PortName', 'Unknown')
                        connection_type = 'unknown'
                        if port.startswith('USB'):
                            connection_type = 'usb'
                        elif port.startswith('COM') or port.startswith('LPT'):
                            connection_type = 'serial'
                        elif ':' in port or port.startswith('\\\\'):
                            connection_type = 'network'
                        
                        printers.append({
                            'name': p.get('Name', 'Unknown'),
                            'port': port,
                            'driver': p.get('DriverName', 'Unknown'),
                            'type': connection_type,
                            'status': 'ready' if p.get('PrinterStatus', 0) == 0 else 'error',
                            'system_printer': True
                        })
                    return printers
                except:
                    pass
        except:
            pass
        
        # Last resort: try WMIC
        try:
            result = subprocess.run(
                ['wmic', 'printer', 'get', 'name,portname,drivername', '/format:csv'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 4:
                            name = parts[-3].strip()
                            port = parts[-2].strip()
                            driver = parts[-1].strip()
                            
                            if name and name != 'Name':
                                connection_type = 'unknown'
                                if port.startswith('USB'):
                                    connection_type = 'usb'
                                elif port.startswith('COM') or port.startswith('LPT'):
                                    connection_type = 'serial'
                                elif ':' in port or port.startswith('\\\\'):
                                    connection_type = 'network'
                                
                                printers.append({
                                    'name': name,
                                    'port': port,
                                    'driver': driver,
                                    'type': connection_type,
                                    'status': 'ready',
                                    'system_printer': True
                                })
        except:
            pass
    
    return printers


def get_linux_printers():
    """Get list of installed printers on Linux"""
    printers = []
    
    try:
        # Use lpstat command
        result = subprocess.run(
            ['lpstat', '-p', '-d'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            current_printer = None
            for line in result.stdout.split('\n'):
                if line.startswith('printer '):
                    # Extract printer name
                    match = re.match(r'printer (\S+)', line)
                    if match:
                        current_printer = match.group(1)
                        printers.append({
                            'name': current_printer,
                            'port': 'Unknown',
                            'driver': 'Unknown',
                            'type': 'unknown',
                            'status': 'ready',
                            'system_printer': True
                        })
    except:
        pass
    
    return printers


def get_macos_printers():
    """
    Get list of installed printers on macOS system.
    
    Uses lpstat command to query print system.
    
    Returns:
        list: List of printer dictionaries with basic information
    
    Example:
        >>> printers = get_macos_printers()
    """
    printers = []
    
    try:
        # Use lpstat command (same as Linux)
        result = subprocess.run(
            ['lpstat', '-p'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'printer ' in line:
                    match = re.search(r'printer (\S+)', line)
                    if match:
                        printer_name = match.group(1)
                        printers.append({
                            'name': printer_name,
                            'port': 'Unknown',
                            'driver': 'Unknown',
                            'type': 'unknown',
                            'status': 'ready',
                            'system_printer': True
                        })
    except:
        pass
    
    return printers


def get_usb_printers():
    """
    Get list of USB printers available for direct USB connection.
    
    Scans USB devices and identifies potential printers by checking device
    names for 'print' or 'printer' keywords.
    
    Returns:
        list: List of USB printer dictionaries, each containing:
            - name (str): Device name
            - vendor_id (str): USB vendor ID in hex
            - product_id (str): USB product ID in hex
            - vendor_name (str): Vendor name
            - product_name (str): Product name
            - type (str): Always 'usb'
            - status (str): Device status
            - system_printer (bool): False for direct USB printers
            - config (dict): Configuration with vendor_id and product_id
    
    Note:
        Requires pyusb library. Returns empty list if not available.
    """
    usb_printers = []
    
    if ESCPOS_AVAILABLE:
        try:
            import usb.core
            import usb.util
            
            # Find all USB devices
            devices = usb.core.find(find_all=True)
            for device in devices:
                try:
                    vendor_name = 'Unknown'
                    product_name = 'Unknown'
                    
                    if device.iManufacturer:
                        try:
                            vendor_name = usb.util.get_string(device, device.iManufacturer)
                        except:
                            pass
                    
                    if device.iProduct:
                        try:
                            product_name = usb.util.get_string(device, device.iProduct)
                        except:
                            pass
                    
                    # Only include devices that might be printers
                    # (This is a heuristic - you might want to refine this)
                    if 'print' in product_name.lower() or 'printer' in product_name.lower() or \
                       'print' in vendor_name.lower() or 'printer' in vendor_name.lower():
                        usb_printers.append({
                            'name': f'{vendor_name} {product_name}',
                            'vendor_id': hex(device.idVendor),
                            'product_id': hex(device.idProduct),
                            'vendor_name': vendor_name,
                            'product_name': product_name,
                            'type': 'usb',
                            'status': 'ready',
                            'system_printer': False,
                            'config': {
                                'vendor_id': device.idVendor,
                                'product_id': device.idProduct
                            }
                        })
                except:
                    pass
        except ImportError:
            pass
        except Exception as e:
            print(f"Error listing USB printers: {e}")
    
    return usb_printers


@app.route('/printer/list', methods=['GET'])
def list_printers():
    """List all available printers (system printers + USB printers)"""
    global printer_list_cache
    all_printers = []
    
    # Get system-installed printers based on OS
    system_printers = []
    if platform.system() == 'Windows':
        system_printers = get_windows_printers()
    elif platform.system() == 'Linux':
        system_printers = get_linux_printers()
    elif platform.system() == 'Darwin':  # macOS
        system_printers = get_macos_printers()
    
    all_printers.extend(system_printers)
    
    # Also get direct USB printers (for raw USB connection)
    usb_printers = get_usb_printers()
    all_printers.extend(usb_printers)
    
    # Add ID to each printer for easy reference
    for idx, printer in enumerate(all_printers):
        printer['id'] = idx
        if 'name' not in printer:
            printer['name'] = f'Printer {idx}'
    
    # Cache the printer list
    printer_list_cache = all_printers
    
    return jsonify({
        'printers': all_printers,
        'count': len(all_printers),
        'system': platform.system(),
        'note': 'System printers can be used via their port. USB printers can be connected directly.'
    })


@app.route('/printer/connect-by-name', methods=['POST'])
def connect_printer_by_name():
    """
    Connect to a printer by name or ID from the printer list.
    
    This is the recommended method for connecting to printers. It automatically
    determines the connection type and configuration based on the printer's
    information from the system.
    
    Request Body (JSON):
        {
            "name": "Printer Name",  // OR
            "id": 0                 // Printer ID from /printer/list
        }
    
    Returns:
        JSON response with success status, message, and connection details
    
    Example Request:
        POST /printer/connect-by-name
        {
            "id": 0
        }
    
    Example Response:
        {
            "success": true,
            "message": "Connected to printer: HP LaserJet Pro",
            "printer_name": "HP LaserJet Pro",
            "connection_type": "windows"
        }
    
    Note:
        The connection type is automatically determined:
        - USB port → 'windows' type (Windows) or 'usb' type (direct)
        - COM/LPT port → 'serial' type
        - Network port → 'network' type
        - Unknown → 'windows' type (Windows) or 'file' type (other)
    """
    global printers, printer_list_cache
    
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body must be JSON'
            }), 400
        
        printer_name = data.get('name')
        printer_id = data.get('id')
        
        # Refresh printer list if cache is empty
        if not printer_list_cache:
            # Trigger list refresh
            list_printers()
        
        # Find the printer by name or ID
        selected_printer = None
        if printer_id is not None:
            # Find by ID
            for p in printer_list_cache:
                if p.get('id') == printer_id:
                    selected_printer = p
                    break
        elif printer_name:
            # Find by name
            for p in printer_list_cache:
                if p.get('name') == printer_name:
                    selected_printer = p
                    break
        
        if not selected_printer:
            return jsonify({
                'success': False,
                'message': f'Printer not found: {printer_name or printer_id}'
            }), 404
        
        # Determine connection type and config from printer info
        connection_type = None
        connection_config = {}
        
        # Check if it's a USB printer with direct config
        if selected_printer.get('config'):
            connection_type = 'usb'
            connection_config = selected_printer['config']
        elif selected_printer.get('port'):
            port = selected_printer['port']
            # Determine type from port
            if port.startswith('COM') or port.startswith('LPT'):
                connection_type = 'serial'
                connection_config = {
                    'port': port,
                    'baudrate': 9600  # Default baudrate
                }
            elif ':' in port or port.startswith('\\\\'):
                # Network printer
                connection_type = 'network'
                if ':' in port:
                    parts = port.split(':')
                    connection_config = {
                        'host': parts[0],
                        'port': int(parts[1]) if len(parts) > 1 else 9100
                    }
                else:
                    connection_config = {
                        'host': port.replace('\\\\', ''),
                        'port': 9100
                    }
            elif port.startswith('USB'):
                # USB port on Windows - use Windows printing API
                if platform.system() == 'Windows':
                    connection_type = 'windows'
                    connection_config = {
                        'printer_name': selected_printer['name']
                    }
                else:
                    connection_type = 'file'
                    connection_config = {
                        'file': selected_printer['name']
                    }
            else:
                # Fallback: use Windows API if on Windows
                if platform.system() == 'Windows':
                    connection_type = 'windows'
                    connection_config = {
                        'printer_name': selected_printer['name']
                    }
                else:
                    connection_type = 'file'
                    connection_config = {
                        'file': selected_printer['name']
                    }
        else:
            # Fallback: try using Windows API if on Windows, otherwise file
            if platform.system() == 'Windows':
                connection_type = 'windows'
                connection_config = {
                    'printer_name': selected_printer['name']
                }
            else:
                connection_type = 'file'
                connection_config = {
                    'file': selected_printer['name']
                }
        
        # Get printer_id from request or use printer name
        printer_id = data.get('printer_id') or selected_printer.get('name', 'printer_' + str(len(printers)))
        printer_name = selected_printer.get('name', 'Unknown')
        
        # If printer_id already exists, disconnect it first (auto-reconnect)
        if printer_id in printers:
            if logger:
                logger.info(f"Printer '{printer_id}' already connected. Disconnecting and reconnecting...")
            printer_info = printers[printer_id]
            try:
                if hasattr(printer_info['instance'], 'close'):
                    printer_info['instance'].close()
            except:
                pass  # Ignore errors when closing
            del printers[printer_id]
        
        # Connect using determined type and config
        printer_instance = get_printer(connection_type, connection_config)
        
        if printer_instance:
            printers[printer_id] = {
                'instance': printer_instance,
                'type': connection_type,
                'config': connection_config,
                'name': printer_name
            }
            
            if logger:
                logger.info(f"Printer connected by name: id={printer_id}, name={printer_name}, type={connection_type}")
            
            return jsonify({
                'success': True,
                'message': f'Connected to printer: {printer_name}',
                'printer_id': printer_id,
                'printer_name': printer_name,
                'connection_type': connection_type
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to connect to printer: {printer_name}'
            }), 400
            
    except Exception as e:
        if logger:
            logger.error(f"Connect by name error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/printer/list-connected', methods=['GET'])
def list_connected_printers():
    """
    List all currently connected printers.
    
    Returns:
        JSON response with list of connected printers
    
    Example Response:
        {
            "printers": [
                {
                    "printer_id": "counter",
                    "name": "Counter Receipt Printer",
                    "type": "windows",
                    "status": "connected"
                },
                {
                    "printer_id": "kitchen",
                    "name": "Kitchen Order Printer",
                    "type": "windows",
                    "status": "connected"
                }
            ],
            "count": 2
        }
    """
    try:
        connected = []
        for printer_id, printer_info in printers.items():
            connected.append({
                'printer_id': printer_id,
                'name': printer_info['name'],
                'type': printer_info['type'],
                'status': 'connected'
            })
        
        return jsonify({
            'printers': connected,
            'count': len(connected)
        })
    except Exception as e:
        if logger:
            logger.error(f"List connected printers error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    if logger:
        logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error) if logger else 'An error occurred'
    }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': 'The requested endpoint was not found'
    }), 404


if __name__ == '__main__':
    print("=" * 60)
    print("Simple Print Server - Thermal Printer Bridge")
    print("=" * 60)
    print(f"ESC/POS Library Available: {ESCPOS_AVAILABLE}")
    print("Server starting on http://localhost:8888")
    print("=" * 60)
    
    # Run the server
    app.run(host='127.0.0.1', port=8888, debug=False)

