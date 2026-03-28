import uuid
from dataclasses import dataclass, field
from typing import Any

import fastmcp
from serial import Serial
from serial.tools.list_ports import comports

rs485_server = fastmcp.FastMCP("mcp-rs485")

PARITY_MAP = {"N": "none", "E": "even", "O": "odd"}


@dataclass
class RS485Connection:
    port: str
    baudrate: int
    parity: str
    stopbits: int
    bytesize: int
    timeout: float
    connection_id: str = field(default_factory=lambda: f"conn_{uuid.uuid4().hex[:12]}")
    serial: Serial | None = field(default=None, repr=False)
    bytes_sent: int = 0
    bytes_received: int = 0


connections: dict[str, RS485Connection] = {}


@rs485_server.tool()
def list_ports() -> list[dict[str, Any]]:
    ports = comports()
    return [
        {
            "port": port.device,
            "description": port.description or "Unknown",
            "hwid": port.hwid,
        }
        for port in ports
    ]


@rs485_server.tool()
def connect_rs485(
    port: str,
    baudrate: int = 9600,
    parity: str = "N",
    stopbits: int = 1,
    bytesize: int = 8,
    timeout: float = 1.0,
) -> str:
    parity_upper = parity.upper()
    if parity_upper not in PARITY_MAP:
        raise ValueError(f"Invalid parity: {parity}. Must be N, E, or O.")

    try:
        serial_conn = Serial(
            port=port,
            baudrate=baudrate,
            parity=PARITY_MAP[parity_upper],
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=timeout,
        )
    except PermissionError as e:
        raise PermissionError(f"Permission denied accessing {port}: {e}") from e
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Port not found: {port}: {e}") from e
    except OSError as e:
        raise OSError(f"Failed to open port {port}: {e}") from e

    conn = RS485Connection(
        port=port,
        baudrate=baudrate,
        parity=parity_upper,
        stopbits=stopbits,
        bytesize=bytesize,
        timeout=timeout,
        serial=serial_conn,
    )
    connections[conn.connection_id] = conn
    return conn.connection_id


@rs485_server.tool()
def disconnect_rs485(connection_id: str) -> str:
    if connection_id not in connections:
        raise ValueError(f"Connection not found: {connection_id}")

    conn = connections[connection_id]
    if conn.serial and conn.serial.is_open:
        conn.serial.close()
    del connections[connection_id]
    return f"Disconnected {connection_id}"


@rs485_server.tool()
def read_rs485(connection_id: str, length: int = 1024) -> str:
    if connection_id not in connections:
        raise ValueError(f"Connection not found: {connection_id}")

    conn = connections[connection_id]
    if not conn.serial or not conn.serial.is_open:
        raise OSError(f"Connection {connection_id} is not open")

    if length <= 0 or length > 65536:
        raise ValueError("Length must be between 1 and 65536")

    data = conn.serial.read(min(length, 65536))
    conn.bytes_received += len(data)
    return data.hex()


@rs485_server.tool()
def write_rs485(connection_id: str, data: str) -> int:
    if connection_id not in connections:
        raise ValueError(f"Connection not found: {connection_id}")

    conn = connections[connection_id]
    if not conn.serial or not conn.serial.is_open:
        raise OSError(f"Connection {connection_id} is not open")

    cleaned = data.replace(" ", "").replace("\n", "").replace("\r", "")
    if not cleaned:
        raise ValueError("No valid hex data provided")

    if len(cleaned) % 2 != 0:
        raise ValueError(f"Hex data must have even length, got {len(cleaned)}")

    try:
        byte_data = bytes.fromhex(cleaned)
    except ValueError as e:
        raise ValueError(f"Invalid hex data: {e}") from e

    if len(byte_data) > 65536:
        raise ValueError("Data exceeds maximum size of 65536 bytes")

    written = conn.serial.write(byte_data)
    if written is None:
        written = 0
    conn.bytes_sent += written
    return written


@rs485_server.tool()
def get_connection_status(connection_id: str) -> dict[str, Any]:
    if connection_id not in connections:
        raise ValueError(f"Connection not found: {connection_id}")

    conn = connections[connection_id]
    is_open = conn.serial is not None and conn.serial.is_open

    return {
        "connection_id": connection_id,
        "port": conn.port,
        "is_open": is_open,
        "baudrate": conn.baudrate,
        "bytes_sent": conn.bytes_sent,
        "bytes_received": conn.bytes_received,
    }


@rs485_server.resource("resource://rs485/connections")
def get_connections_resource() -> str:
    import json

    result = []
    for conn_id, conn in connections.items():
        is_open = conn.serial is not None and conn.serial.is_open
        result.append(
            {
                "connection_id": conn_id,
                "port": conn.port,
                "is_open": is_open,
                "baudrate": conn.baudrate,
            }
        )
    return json.dumps(result)
