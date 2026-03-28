import pytest


@pytest.fixture
def sample_port_info() -> dict[str, str]:
    return {
        "port": "/dev/ttyUSB0",
        "description": "USB Serial Converter",
        "hwid": "USB VID:PID=0403:6001",
    }


@pytest.fixture
def sample_connection_status() -> dict[str, int | str | bool]:
    return {
        "connection_id": "conn_abc123",
        "port": "/dev/ttyUSB0",
        "is_open": True,
        "baudrate": 9600,
        "bytes_sent": 1024,
        "bytes_received": 2048,
    }
