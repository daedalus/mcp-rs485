# SPEC.md — rs485-mcp

## Purpose

An MCP server that exposes RS485 bus connectivity, enabling AI assistants and applications to read from and write to RS485 serial devices. RS485 is a differential serial communication standard commonly used in industrial automation, HVAC systems, and sensor networks.

## Scope

### In Scope
- Serial port discovery and listing
- RS485 device connection management
- Reading data from RS485 bus
- Writing data to RS485 bus
- Bus configuration (baudrate, parity, stop bits, data bits)
- Connection status monitoring
- Graceful connection teardown

### Not In Scope
- Protocol-specific implementations (Modbus, Bacnet, etc.)
- Multi-drop arbitration logic (handled by hardware)
- RS232 or other serial standards
- USB-to-Serial adapter management (beyond basic serial port access)
- Network-based serial communication

## Public API / Interface

### MCP Tools

#### `list_ports()`
- **Description**: Lists all available serial ports on the system.
- **Returns**: List of dictionaries with port name, description, and hardware info.
- **Example**: `[{"port": "/dev/ttyUSB0", "description": "USB Serial", "hwid": "USB VID:PID=...}]`

#### `connect_rs485(port: str, baudrate: int = 9600, parity: str = "N", stopbits: int = 1, bytesize: int = 8, timeout: float = 1.0)`
- **Description**: Opens a connection to an RS485 device.
- **Args**:
  - `port`: Serial port path (e.g., "/dev/ttyUSB0" or "COM3")
  - `baudrate`: Communication speed (default: 9600)
  - `parity`: Parity setting - "N" (none), "E" (even), "O" (odd) (default: "N")
  - `stopbits`: Number of stop bits (default: 1)
  - `bytesize`: Data bits per frame (default: 8)
  - `timeout`: Read timeout in seconds (default: 1.0)
- **Returns**: Connection ID string for subsequent operations.
- **Raises**: Error message if connection fails.

#### `disconnect_rs485(connection_id: str)`
- **Description**: Closes an RS485 connection.
- **Args**: `connection_id`: Connection ID from connect_rs485.
- **Returns**: Success confirmation string.

#### `read_rs485(connection_id: str, length: int = 1024)`
- **Description**: Reads data from an open RS485 connection.
- **Args**:
  - `connection_id`: Connection ID from connect_rs485.
  - `length`: Maximum bytes to read (default: 1024).
- **Returns**: Hex string of received data.
- **Raises**: Error if connection not found.

#### `write_rs485(connection_id: str, data: str)`
- **Description**: Writes data to an RS485 connection.
- **Args**:
  - `connection_id`: Connection ID from connect_rs485.
  - `data`: Hex string of data to send (e.g., "01 03 00 00 00 0A").
- **Returns**: Number of bytes written.

#### `get_connection_status(connection_id: str)`
- **Description**: Gets the status of an RS485 connection.
- **Args**: `connection_id`: Connection ID from connect_rs485.
- **Returns**: Dictionary with connection state and statistics.

### MCP Resources

#### `resource://rs485/connections`
- **Description**: Returns JSON list of all active connections.

## Data Formats

### Serial Port List Response
```json
[
  {
    "port": "/dev/ttyUSB0",
    "description": "USB Serial Converter",
    "hwid": "USB VID:PID=0403:6001"
  }
]
```

### Connection Status Response
```json
{
  "connection_id": "conn_abc123",
  "port": "/dev/ttyUSB0",
  "is_open": true,
  "baudrate": 9600,
  "bytes_sent": 1024,
  "bytes_received": 2048
}
```

## Edge Cases

1. **Port not found**: Return clear error when attempting to connect to non-existent port.
2. **Port already in use**: Detect and report when port is busy.
3. **Permission denied**: Report when lacking permissions to access serial port.
4. **Read timeout**: Handle timeouts gracefully, returning empty data or timeout error.
5. **Invalid hex data**: Validate and reject malformed hex strings.
6. **Connection not found**: Return error for operations on non-existent connections.
7. **Write to closed connection**: Detect and report write attempts on closed connections.
8. **Rapid connect/disconnect**: Handle concurrent connection attempts safely.
9. **Empty read**: Return empty string for zero bytes available.
10. **Special characters**: Handle binary data including null bytes and high ASCII.

## Performance & Constraints

- Read operations timeout after configured duration (default 1s)
- Maximum read buffer: 65536 bytes
- Maximum write buffer: 65536 bytes
- Connection IDs: UUID4-based, unique per session
- No persistent connections across server restarts
