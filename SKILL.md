# MCP RS485

MCP server exposing RS485 bus connectivity.

## When to use this skill

Use this skill when you need to:
- Communicate with RS485 devices
- Read/write serial data on RS485 bus
- Connect to industrial equipment

## Tools

- `list_ports` - List available serial ports
- `connect_rs485` - Open RS485 connection
- `disconnect_rs485` - Close connection
- `read_rs485` - Read data
- `write_rs485` - Write data
- `get_connection_status` - Get connection status

## Install

```bash
pip install mcp-rs485
```