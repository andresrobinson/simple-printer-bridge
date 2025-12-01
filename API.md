# API Documentation

Complete API reference for Simple Print Server.

> 📖 **Other Documentation:**
> - [README.md](README.md) - Installation, usage, and quick start guide
> - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
> - [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute to this project

## Table of Contents

- [Server API Endpoints](#server-api-endpoints)
- [JavaScript Client Library](#javascript-client-library)
- [Python Server Functions](#python-server-functions)

---

## Server API Endpoints

All endpoints are available at `http://localhost:8888` by default.

### GET /health

Check server status and availability.

**Response:**
```json
{
  "status": "ok",
  "espos_available": true,
  "printers_connected": 2,
  "printer_ids": ["counter", "kitchen"]
}
```

**Response Fields:**
- `status` (string): Server status ("ok" or "error")
- `espos_available` (boolean): Whether python-escpos library is installed
- `printers_connected` (number): Number of currently connected printers
- `printer_ids` (array): List of connected printer IDs

---

### GET /printer/list

List all available printers (system-installed + USB).

**Response:**
```json
{
  "printers": [
    {
      "id": 0,
      "name": "HP LaserJet Pro",
      "port": "USB001",
      "driver": "HP Universal Print Driver",
      "type": "usb",
      "status": "ready",
      "system_printer": true
    }
  ],
  "count": 1,
  "system": "Windows",
  "note": "System printers can be used via their port..."
}
```

**Printer Object Fields:**
- `id` (number): Unique identifier for connecting
- `name` (string): Printer name
- `port` (string): Connection port
- `driver` (string): Driver name (Windows only)
- `type` (string): Connection type (usb, serial, network, unknown)
- `status` (string): Printer status (ready, error, unknown)
- `system_printer` (boolean): True for system printers, false for USB

---

### POST /printer/connect-by-name

**Recommended method** - Connect to a printer by name or ID.

**Request Body:**
```json
{
  "id": 0,
  "printer_id": "counter"
}
```
OR
```json
{
  "name": "HP LaserJet Pro",
  "printer_id": "counter"
}
```

**Parameters:**
- `id` (number, optional): Printer ID from the list
- `name` (string, optional): Printer name
- `printer_id` (string, optional): Custom ID for this printer connection (defaults to printer name)

**Response:**
```json
{
  "success": true,
  "message": "Connected to printer: HP LaserJet Pro",
  "printer_id": "counter",
  "printer_name": "HP LaserJet Pro",
  "connection_type": "windows"
}
```

**Note:** Connection type is automatically determined based on printer port. You can connect to multiple printers simultaneously by using different `printer_id` values.

---

### POST /printer/connect

Connect to a printer using manual configuration.

**Request Body:**
```json
{
  "printer_id": "counter",
  "name": "Counter Printer",
  "type": "windows",
  "config": {
    "printer_name": "HP LaserJet Pro"
  }
}
```

**Parameters:**
- `printer_id` (string, optional): Unique ID for this printer connection (auto-generated if not provided)
- `name` (string, optional): Display name for the printer
- `type` (string, required): Printer type (usb, serial, network, file, windows)
- `config` (object, required): Configuration object specific to printer type

**Connection Types:**
- `usb`: Direct USB connection
  ```json
  {
    "type": "usb",
    "config": {
      "vendor_id": 1273,
      "product_id": 8288,
      "in_ep": 129,
      "out_ep": 3
    }
  }
  ```

- `serial`: Serial/COM port
  ```json
  {
    "type": "serial",
    "config": {
      "port": "COM3",
      "baudrate": 9600
    }
  }
  ```

- `network`: Network printer
  ```json
  {
    "type": "network",
    "config": {
      "host": "192.168.1.100",
      "port": 9100
    }
  }
  ```

- `windows`: Windows system printer (recommended for Windows)
  ```json
  {
    "type": "windows",
    "config": {
      "printer_name": "Printer Name"
    }
  }
  ```

**Response:**
```json
{
  "success": true,
  "message": "Connected to Counter Printer",
  "printer_id": "counter",
  "printer_name": "Counter Printer"
}
```

---

### POST /printer/disconnect

Disconnect from a specific printer or all printers.

**Request Body (optional):**
```json
{
  "printer_id": "counter"
}
```

**Parameters:**
- `printer_id` (string, optional): ID of printer to disconnect. If omitted, disconnects all printers.

**Response (specific printer):**
```json
{
  "success": true,
  "message": "Printer \"counter\" disconnected"
}
```

**Response (all printers):**
```json
{
  "success": true,
  "message": "All printers disconnected (2 printers)"
}
```

---

### POST /printer/print

Send print job to a specific printer.

**Request Body (Text Printing):**
```json
{
  "printer_id": "counter",
  "type": "text",
  "data": "Hello World\nLine 2",
  "cut": true
}
```

**Parameters:**
- `printer_id` (string, **required**): ID of the printer to use
- `type` (string, required): Print type ("text", "raw", or "escpos")
- `data` (string|array, required for "text" and "raw"): Data to print
- `commands` (array, required for "escpos"): ESC/POS command array
- `cut` (boolean, optional): Auto-cut paper after printing (default: false)

**Request Body (Raw ESC/POS):**
```json
{
  "printer_id": "counter",
  "type": "raw",
  "data": "1B 40",
  "cut": false
}
```

**Request Body (Structured ESC/POS):**
```json
{
  "printer_id": "counter",
  "type": "escpos",
  "commands": [
    {"action": "set", "attribute": "align", "value": "center"},
    {"action": "text", "data": "Hello"},
    {"action": "cut"}
  ]
}
```

**ESC/POS Commands:**
- `text`: Print text
  ```json
  {"action": "text", "data": "Hello World"}
  ```

- `cut`: Cut paper
  ```json
  {"action": "cut"}
  ```

- `set`: Set formatting
  ```json
  {"action": "set", "attribute": "align", "value": "center"}
  {"action": "set", "attribute": "text_size", "value": "b"}
  {"action": "set", "attribute": "font", "value": "a"}
  ```

**Response:**
```json
{
  "success": true,
  "message": "Print job sent successfully to Counter Printer"
}
```

**Error Responses:**
- `400 Bad Request`: Missing `printer_id` or invalid request
- `404 Not Found`: Printer with specified `printer_id` is not connected

---

### GET /printer/list-connected

List all currently connected printers.

**Response:**
```json
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
```

---

## JavaScript Client Library

### SimplePrintClient Class

#### Constructor

```javascript
const printer = new SimplePrintClient(serverUrl);
```

**Parameters:**
- `serverUrl` (string, optional): Print server URL (default: `'http://localhost:8888'`)

---

#### checkHealth()

Check if print server is available.

```javascript
const health = await printer.checkHealth();
// Returns: { status: 'ok', espos_available: true, printer_connected: false }
```

---

#### listPrinters()

List all available printers.

```javascript
const printers = await printer.listPrinters();
// Returns: Array of printer objects
```

---

#### connectByName(nameOrId, printerId)

Connect to a printer by name or ID (recommended).

```javascript
// By ID with custom printer_id
await printer.connectByName(0, 'counter');

// By name with custom printer_id
await printer.connectByName("HP LaserJet Pro", 'kitchen');

// Without custom printer_id (uses printer name as ID)
await printer.connectByName(0);
```

**Parameters:**
- `nameOrId` (string|number): Printer name or ID from the list
- `printerId` (string, optional): Custom ID for this printer connection (defaults to printer name)

**Returns:** Promise resolving to connection response with `printer_id` and `printer_name`

---

#### connect(options)

Connect to a printer using manual configuration.

```javascript
await printer.connect({
  printer_id: 'counter',
  name: 'Counter Printer',
  type: 'windows',
  config: { printer_name: 'HP LaserJet Pro' }
});
```

**Parameters:**
- `options.printer_id` (string, optional): Unique ID for this printer (auto-generated if not provided)
- `options.name` (string, optional): Display name for the printer
- `options.type` (string, required): Printer type
- `options.config` (object, required): Configuration object

```javascript
await printer.connect({
  type: 'windows',
  config: { printer_name: 'HP LaserJet Pro' }
});
```

**Parameters:**
- `options` (object): Connection options
  - `type` (string): Printer type
  - `config` (object): Configuration object

---

#### disconnect(printerId)

Disconnect from a specific printer or all printers.

```javascript
// Disconnect specific printer
await printer.disconnect('counter');

// Disconnect all printers
await printer.disconnect();
```

**Parameters:**
- `printerId` (string, optional): ID of printer to disconnect. If omitted, disconnects all printers.

---

#### print(printerId, options)

Send print job to a specific printer.

```javascript
await printer.print('counter', {
  type: 'text',
  data: 'Hello World',
  cut: true
});
```

**Parameters:**
- `printerId` (string, **required**): ID of the printer to use
- `options` (object): Print options
  - `type` (string, required): 'text', 'raw', or 'escpos'
  - `data` (string|array, required for 'text' and 'raw'): Data to print
  - `cut` (boolean, optional): Auto-cut after printing (default: false)
  - `commands` (array, required for 'escpos'): ESC/POS command array

**Throws:** Error if printer is not connected

---

#### printText(printerId, text, cut)

Print text to a specific printer (convenience method).

```javascript
await printer.printText('counter', 'Hello World\nLine 2', true);
```

**Parameters:**
- `printerId` (string, **required**): ID of the printer to use
- `text` (string, required): Text to print (can include newlines)
- `cut` (boolean, optional): Auto-cut after printing (default: false)

---

#### printRaw(printerId, rawData, cut)

Print raw ESC/POS commands to a specific printer (convenience method).

```javascript
await printer.printRaw('counter', '1B 40', true);  // Hex string
await printer.printRaw('counter', [0x1B, 0x40], true);  // Byte array
```

**Parameters:**
- `printerId` (string, **required**): ID of the printer to use
- `rawData` (string|array, required): Raw hex string or byte array
- `cut` (boolean, optional): Auto-cut after printing (default: false)

---

#### printReceipt(printerId, receipt)

Print a formatted receipt to a specific printer (convenience method).

```javascript
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
```

**Parameters:**
- `printerId` (string, **required**): ID of the printer to use
- `receipt` (object, required): Receipt data
  - `header` (string, optional): Receipt header
  - `storeName` (string, optional): Store name
  - `storeAddress` (string, optional): Store address
  - `items` (array, optional): Array of items with `name`, `quantity`, `price`
  - `subtotal` (number, optional): Subtotal amount
  - `tax` (number, optional): Tax amount
  - `total` (number, optional): Total amount
  - `footer` (string, optional): Footer message

---

#### listConnectedPrinters()

List all currently connected printers.

```javascript
const connected = await printer.listConnectedPrinters();
// Returns: Array of connected printer objects
```

**Returns:** Promise resolving to array of connected printer objects with `printer_id`, `name`, `type`, and `status`

---

#### getConnectedPrinterIds()

Get list of connected printer IDs (synchronous).

```javascript
const ids = printer.getConnectedPrinterIds();
// Returns: ['counter', 'kitchen']
```

**Returns:** Array of printer ID strings

---

## Python Server Functions

### get_printer(printer_type, config)

Initialize and return a printer instance.

**Parameters:**
- `printer_type` (str): Type of printer connection
- `config` (dict): Configuration dictionary

**Returns:**
- Printer instance or None

---

### WindowsPrinter Class

Windows system printer handler using win32print API.

**Methods:**
- `text(text)`: Add text to print buffer
- `_raw(data)`: Add raw bytes to buffer
- `cut()`: Add paper cut command to buffer
- `set(**kwargs)`: Add formatting commands to buffer
- `flush()`: Send all buffered data to printer in one print job
- `close()`: Cleanup (no-op)

---

### get_windows_printers()

Get list of installed printers on Windows.

**Returns:**
- List of printer dictionaries

---

### get_linux_printers()

Get list of installed printers on Linux.

**Returns:**
- List of printer dictionaries

---

### get_macos_printers()

Get list of installed printers on macOS.

**Returns:**
- List of printer dictionaries

---

### get_usb_printers()

Get list of USB printers for direct connection.

**Returns:**
- List of USB printer dictionaries

---

## Complete Example

```javascript
// Initialize client
const printer = new SimplePrintClient('http://localhost:8888');

// Check server health
const health = await printer.checkHealth();
console.log('Server status:', health);

// List available printers
const printers = await printer.listPrinters();
console.log(`Found ${printers.length} printers`);

// Connect to first printer
await printer.connectByName(0);

// Print text
await printer.printText('Hello World!', true);

// Print receipt
await printer.printReceipt({
  header: 'RECEIPT',
  storeName: 'My Store',
  items: [
    { name: 'Item 1', quantity: 2, price: 10.99 }
  ],
  total: 21.98,
  footer: 'Thank you!'
});

// Disconnect
await printer.disconnect();
```

---

## Error Handling

All methods throw errors that should be caught:

```javascript
try {
  await printer.connectByName(0);
  await printer.printText('Hello');
} catch (error) {
  console.error('Error:', error.message);
}
```

Common errors:
- `Cannot connect to print server`: Server is not running
- `Printer not connected`: No printer is connected
- `Failed to connect`: Printer connection failed
- `Print error: ...`: Printing failed

---

## Related Documentation

- [README.md](README.md) - Installation, usage, and quick start guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute to this project

