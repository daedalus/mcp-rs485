from mcp_rs485.server import rs485_server


def main() -> int:
    rs485_server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
