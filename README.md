# mcp-rs485

> MCP server that exposes RS485 bus connectivity for reading and writing serial data.

[![PyPI](https://img.shields.io/pypi/v/mcp-rs485.svg)](https://pypi.org/project/mcp-rs485/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-rs485.svg)](https://pypi.org/project/mcp-rs485/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Install

```bash
pip install mcp-rs485
```

## Usage

This MCP server exposes RS485 serial bus connectivity through the Model Context Protocol. It allows AI assistants to interact with RS485 devices.

### Tools

- `list_ports`: Lists all available serial ports on the system
- `connect_rs485`: Opens a connection to an RS485 device
- `disconnect_rs485`: Closes an RS485 connection
- `read_rs485`: Reads data from an open RS485 connection
- `write_rs485`: Writes data to an RS485 connection
- `get_connection_status`: Gets the status of an RS485 connection

### Example

```python
from mcp_rs485.server import connect_rs485, write_rs485, read_rs485

# Connect to a device
conn_id = connect_rs485("/dev/ttyUSB0", baudrate=9600)

# Write data (Modbus RTU example)
write_rs485(conn_id, "01 03 00 00 00 0A")

# Read response
response = read_rs485(conn_id)

# Cleanup
disconnect_rs485(conn_id)
```

## Development

```bash
git clone https://github.com/daedalus/mcp-rs485.git
cd mcp-rs485
pip install -e ".[test]"

# run tests
pytest

# format
ruff format src/ tests/

# lint
ruff check src/ tests/

# type check
mypy src/
```

## API

### list_ports()

Lists all available serial ports.

**Returns:** List of port dictionaries with `port`, `description`, and `hwid`.

### connect_rs485(port, baudrate=9600, parity="N", stopbits=1, bytesize=8, timeout=1.0)

Opens a connection to an RS485 device.

**Parameters:**
- `port`: Serial port path (e.g., "/dev/ttyUSB0")
- `baudrate`: Communication speed (default: 9600)
- `parity`: "N" (none), "E" (even), "O" (odd)
- `stopbits`: Number of stop bits
- `bytesize`: Data bits per frame
- `timeout`: Read timeout in seconds

**Returns:** Connection ID string.

### read_rs485(connection_id, length=1024)

Reads data from an open RS485 connection.

**Parameters:**
- `connection_id`: Connection ID from connect_rs485
- `length`: Maximum bytes to read

**Returns:** Hex string of received data.

### write_rs485(connection_id, data)

Writes data to an RS485 connection.

**Parameters:**
- `connection_id`: Connection ID from connect_rs485
- `data`: Hex string (e.g., "01 03 00 00 00 0A")

**Returns:** Number of bytes written.

### get_connection_status(connection_id)

Gets connection status and statistics.

**Returns:** Dictionary with connection state and statistics.
