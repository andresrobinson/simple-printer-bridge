/**
 * Simple Print Client Library
 * A lightweight alternative to QZ Tray for thermal printers
 * 
 * Usage:
 *   const printer = new SimplePrintClient('http://localhost:8888');
 *   await printer.connect({ type: 'usb', config: { vendor_id: 0x04f9, product_id: 0x2060 } });
 *   await printer.print({ type: 'text', data: 'Hello World', cut: true });
 */

class SimplePrintClient {
    constructor(serverUrl = 'http://localhost:8888') {
        this.serverUrl = serverUrl;
        this.connectedPrinters = {}; // Map of printer_id -> printer info
    }

    /**
     * Check if server is available
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.serverUrl}/health`);
            const data = await response.json();
            return data;
        } catch (error) {
            throw new Error(`Cannot connect to print server: ${error.message}`);
        }
    }

    /**
     * Connect to a printer
     * @param {Object} options - Connection options
     * @param {string} options.printer_id - Unique ID for this printer (optional, auto-generated if not provided)
     * @param {string} options.name - Display name for the printer (optional)
     * @param {string} options.type - Printer type: 'usb', 'serial', 'network', 'file', 'windows'
     * @param {Object} options.config - Printer configuration
     * @returns {Promise<Object>} Response with printer_id and printer_name
     * @example
     * await printer.connect({ 
     *   printer_id: 'counter',
     *   name: 'Counter Printer',
     *   type: 'windows', 
     *   config: { printer_name: 'HP LaserJet' } 
     * });
     */
    async connect(options = {}) {
        try {
            const response = await fetch(`${this.serverUrl}/printer/connect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(options)
            });

            const data = await response.json();
            
            if (data.success) {
                const printerId = data.printer_id || options.printer_id;
                this.connectedPrinters[printerId] = {
                    id: printerId,
                    name: data.printer_name || options.name || printerId,
                    type: options.type
                };
                return data;
            } else {
                throw new Error(data.message || 'Failed to connect');
            }
        } catch (error) {
            throw error;
        }
    }

    /**
     * Connect to a printer by name or ID from the printer list
     * @param {string|number} nameOrId - Printer name or ID from the list
     * @param {string} [printerId] - Optional custom ID for this printer connection (defaults to printer name)
     * @returns {Promise<Object>} Response with printer_id and printer_name
     * @example
     * // Connect using printer ID from list
     * await printer.connectByName(0, 'counter');
     * 
     * @example
     * // Connect using printer name
     * await printer.connectByName('HP LaserJet', 'receipt-printer');
     */
    async connectByName(nameOrId, printerId = null) {
        try {
            const isId = typeof nameOrId === 'number' || /^\d+$/.test(nameOrId);
            const payload = isId ? { id: parseInt(nameOrId) } : { name: nameOrId };
            
            if (printerId) {
                payload.printer_id = printerId;
            }
            
            const response = await fetch(`${this.serverUrl}/printer/connect-by-name`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            
            if (data.success) {
                const connectedId = data.printer_id;
                this.connectedPrinters[connectedId] = {
                    id: connectedId,
                    name: data.printer_name || nameOrId,
                    type: data.connection_type
                };
                return data;
            } else {
                throw new Error(data.message || 'Failed to connect');
            }
        } catch (error) {
            throw error;
        }
    }

    /**
     * Disconnect from a specific printer or all printers
     * @param {string} [printerId] - Optional printer ID to disconnect. If omitted, disconnects all printers.
     * @returns {Promise<Object>} Response with success status
     * @example
     * // Disconnect specific printer
     * await printer.disconnect('counter');
     * 
     * @example
     * // Disconnect all printers
     * await printer.disconnect();
     */
    async disconnect(printerId = null) {
        try {
            const payload = printerId ? { printer_id: printerId } : {};
            
            const response = await fetch(`${this.serverUrl}/printer/disconnect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            
            if (printerId) {
                delete this.connectedPrinters[printerId];
            } else {
                this.connectedPrinters = {};
            }
            
            return data;
        } catch (error) {
            throw error;
        }
    }

    /**
     * Print data to a specific printer
     * @param {string} printerId - ID of the printer to use (required)
     * @param {Object} options - Print options
     * @param {string} options.type - Print type: 'text', 'raw', 'escpos'
     * @param {string|Array} options.data - Data to print
     * @param {boolean} options.cut - Auto-cut paper after printing
     * @param {Array} options.commands - ESC/POS commands (for type: 'escpos')
     * @returns {Promise<Object>} Response with success status
     * @example
     * await printer.print('counter', {
     *   type: 'text',
     *   data: 'Hello World',
     *   cut: true
     * });
     */
    async print(printerId, options = {}) {
        if (!printerId) {
            throw new Error('printerId is required. Specify which printer to use.');
        }
        
        if (!this.connectedPrinters[printerId]) {
            throw new Error(`Printer "${printerId}" not connected. Call connect() or connectByName() first.`);
        }

        try {
            const payload = {
                printer_id: printerId,
                ...options
            };
            
            const response = await fetch(`${this.serverUrl}/printer/print`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            
            if (data.success) {
                return data;
            } else {
                throw new Error(data.message || 'Print failed');
            }
        } catch (error) {
            throw error;
        }
    }

    /**
     * Print text (convenience method)
     * 
     * Sends plain text to the printer. Multi-line text is supported.
     * 
     * @param {string} printerId - ID of the printer to use
     * @param {string} text - Text to print (can include newlines)
     * @param {boolean} cut - Auto-cut paper after printing (default: false)
     * @returns {Promise<Object>} Response object with success status
     * @throws {Error} If printer is not connected or print fails
     * 
     * @example
     * await printer.printText('counter', 'Hello World\nLine 2', true);
     */
    async printText(printerId, text, cut = false) {
        return this.print(printerId, {
            type: 'text',
            data: text,
            cut: cut
        });
    }

    /**
     * Print raw ESC/POS commands
     * 
     * Sends raw ESC/POS command bytes directly to the printer.
     * Useful for advanced formatting or custom commands.
     * 
     * @param {string} printerId - ID of the printer to use
     * @param {string|Array} rawData - Raw hex string (e.g., "1B 40") or byte array
     * @param {boolean} cut - Auto-cut paper after printing (default: false)
     * @returns {Promise<Object>} Response object with success status
     * @throws {Error} If printer is not connected or print fails
     * 
     * @example
     * // Print ESC @ (reset) command
     * await printer.printRaw('counter', '1B 40');
     * 
     * @example
     * // Print from byte array
     * await printer.printRaw('counter', [0x1B, 0x40]);
     */
    async printRaw(printerId, rawData, cut = false) {
        return this.print(printerId, {
            type: 'raw',
            data: rawData,
            cut: cut
        });
    }

    /**
     * List all available printers (system-installed + USB)
     * 
     * Retrieves a list of all printers available on the system.
     * Includes both system-installed printers and direct USB printers.
     * 
     * @returns {Promise<Array>} Array of printer objects, each containing:
     *   - id (number): Unique identifier for connecting
     *   - name (string): Printer name
     *   - port (string): Connection port
     *   - driver (string): Driver name (Windows)
     *   - type (string): Connection type (usb, serial, network, unknown)
     *   - status (string): Printer status (ready, error, unknown)
     *   - system_printer (boolean): True for system printers, false for USB
     * 
     * @throws {Error} If server is unreachable
     * 
     * @example
     * const printers = await printer.listPrinters();
     * console.log(`Found ${printers.length} printers`);
     * printers.forEach(p => console.log(p.name));
     */
    async listPrinters() {
        try {
            const response = await fetch(`${this.serverUrl}/printer/list`);
            const data = await response.json();
            return data.printers || [];
        } catch (error) {
            throw error;
        }
    }

    /**
     * Print a formatted receipt (convenience method)
     * 
     * Formats and prints a complete receipt with header, items, totals, and footer.
     * Automatically handles alignment, formatting, and paper cutting.
     * 
     * @param {string} printerId - ID of the printer to use
     * @param {Object} receipt - Receipt data object
     * @param {string} [receipt.header] - Receipt header text (e.g., "RECEIPT")
     * @param {string} [receipt.storeName] - Store name
     * @param {string} [receipt.storeAddress] - Store address
     * @param {Array<Object>} [receipt.items] - Array of item objects, each with:
     *   - name (string): Item name
     *   - quantity (number): Item quantity
     *   - price (number): Item price
     * @param {number} [receipt.subtotal] - Subtotal amount
     * @param {number} [receipt.tax] - Tax amount
     * @param {number} [receipt.total] - Total amount
     * @param {string} [receipt.footer] - Footer message
     * @returns {Promise<Object>} Response object with success status
     * @throws {Error} If printer is not connected or print fails
     * 
     * @example
     * await printer.printReceipt('counter', {
     *   header: 'RECEIPT',
     *   storeName: 'My Store',
     *   storeAddress: '123 Main St',
     *   items: [
     *     { name: 'Item 1', quantity: 2, price: 10.99 },
     *     { name: 'Item 2', quantity: 1, price: 5.50 }
     *   ],
     *   subtotal: 27.48,
     *   tax: 2.20,
     *   total: 29.68,
     *   footer: 'Thank you!'
     * });
     */
    async printReceipt(printerId, receipt) {
        const commands = [];

        // Header
        if (receipt.header) {
            commands.push({ action: 'set', attribute: 'align', value: 'center' });
            commands.push({ action: 'set', attribute: 'text_size', value: 'b' });
            commands.push({ action: 'text', data: receipt.header });
            commands.push({ action: 'text', data: '\n' });
        }

        // Store info
        if (receipt.storeName) {
            commands.push({ action: 'set', attribute: 'align', value: 'center' });
            commands.push({ action: 'text', data: receipt.storeName + '\n' });
        }

        if (receipt.storeAddress) {
            commands.push({ action: 'set', attribute: 'align', value: 'center' });
            commands.push({ action: 'text', data: receipt.storeAddress + '\n' });
        }

        // Divider
        commands.push({ action: 'text', data: '--------------------------------\n' });

        // Items
        if (receipt.items && receipt.items.length > 0) {
            commands.push({ action: 'set', attribute: 'align', value: 'left' });
            commands.push({ action: 'set', attribute: 'text_size', value: 'normal' });
            
            receipt.items.forEach(item => {
                const name = item.name || '';
                const qty = item.quantity || 1;
                const price = item.price || 0;
                const total = qty * price;
                
                const line = `${name} x${qty} = $${total.toFixed(2)}\n`;
                commands.push({ action: 'text', data: line });
            });
        }

        // Divider
        commands.push({ action: 'text', data: '--------------------------------\n' });

        // Totals
        if (receipt.subtotal !== undefined) {
            commands.push({ action: 'text', data: `Subtotal: $${receipt.subtotal.toFixed(2)}\n` });
        }
        if (receipt.tax !== undefined) {
            commands.push({ action: 'text', data: `Tax: $${receipt.tax.toFixed(2)}\n` });
        }
        if (receipt.total !== undefined) {
            commands.push({ action: 'set', attribute: 'text_size', value: 'b' });
            commands.push({ action: 'text', data: `TOTAL: $${receipt.total.toFixed(2)}\n` });
        }

        // Footer
        if (receipt.footer) {
            commands.push({ action: 'set', attribute: 'align', value: 'center' });
            commands.push({ action: 'set', attribute: 'text_size', value: 'normal' });
            commands.push({ action: 'text', data: '\n' + receipt.footer + '\n' });
        }

        // Cut
        commands.push({ action: 'cut' });

        return this.print(printerId, {
            type: 'escpos',
            commands: commands
        });
    }
    
    /**
     * List all currently connected printers
     * 
     * @returns {Promise<Array>} Array of connected printer objects
     * @example
     * const connected = await printer.listConnectedPrinters();
     * console.log(`Connected: ${connected.length} printers`);
     */
    async listConnectedPrinters() {
        try {
            const response = await fetch(`${this.serverUrl}/printer/list-connected`);
            const data = await response.json();
            
            // Update local cache
            if (data.printers) {
                data.printers.forEach(p => {
                    this.connectedPrinters[p.printer_id] = {
                        id: p.printer_id,
                        name: p.name,
                        type: p.type
                    };
                });
            }
            
            return data.printers || [];
        } catch (error) {
            throw error;
        }
    }
    
    /**
     * Get list of connected printer IDs
     * 
     * @returns {Array<string>} Array of printer IDs
     * @example
     * const ids = printer.getConnectedPrinterIds();
     * console.log('Connected printers:', ids);
     */
    getConnectedPrinterIds() {
        return Object.keys(this.connectedPrinters);
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimplePrintClient;
}

