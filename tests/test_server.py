from unittest.mock import MagicMock, patch

import pytest

from mcp_rs485.server import (
    PARITY_MAP,
    RS485Connection,
    connect_rs485,
    connections,
    disconnect_rs485,
    get_connection_status,
    list_ports,
    read_rs485,
    write_rs485,
)


@pytest.fixture(autouse=True)
def clear_connections() -> None:
    connections.clear()
    yield
    connections.clear()


@pytest.fixture
def mock_serial() -> tuple[MagicMock, MagicMock]:
        with patch("mcp_rs485.server.Serial") as mock:
        serial_instance = MagicMock()
        serial_instance.is_open = True
        mock.return_value = serial_instance
        yield mock, serial_instance


class TestListPorts:
    def test_list_ports_returns_list(self) -> None:
            with patch("mcp_rs485.server.comports") as mock_comports:
            mock_port = MagicMock()
            mock_port.device = "/dev/ttyUSB0"
            mock_port.description = "USB Serial"
            mock_port.hwid = "USB VID:PID=1234:5678"
            mock_comports.return_value = [mock_port]

            result = list_ports()

            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["port"] == "/dev/ttyUSB0"
            assert result[0]["description"] == "USB Serial"


class TestConnectRS485:
    def test_connect_rs485_success(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, _ = mock_serial
        conn_id = connect_rs485("/dev/ttyUSB0", baudrate=9600)

        assert conn_id.startswith("conn_")
        assert conn_id in connections
        mock.assert_called_once()

    def test_connect_rs485_custom_params(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, _ = mock_serial
        connect_rs485(
            port="/dev/ttyUSB1",
            baudrate=19200,
            parity="E",
            stopbits=2,
            bytesize=7,
            timeout=2.0,
        )

        mock.assert_called_once()
        call_kwargs = mock.call_args.kwargs
        assert call_kwargs["baudrate"] == 19200
        assert call_kwargs["parity"] == "even"
        assert call_kwargs["stopbits"] == 2
        assert call_kwargs["bytesize"] == 7
        assert call_kwargs["timeout"] == 2.0

    def test_connect_rs485_invalid_parity(self) -> None:
        with pytest.raises(ValueError, match="Invalid parity"):
            connect_rs485("/dev/ttyUSB0", parity="X")

    def test_connect_rs485_permission_denied(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, _ = mock_serial
        mock.side_effect = PermissionError("Access denied")

        with pytest.raises(PermissionError, match="Permission denied"):
            connect_rs485("/dev/ttyUSB0")

    def test_connect_rs485_port_not_found(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, _ = mock_serial
        mock.side_effect = FileNotFoundError("Port not found")

        with pytest.raises(FileNotFoundError, match="Port not found"):
            connect_rs485("/dev/ttyUSB0")


class TestDisconnectRS485:
    def test_disconnect_rs485_success(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        conn_id = connect_rs485("/dev/ttyUSB0")
        serial_instance.is_open = True

        result = disconnect_rs485(conn_id)

        assert "Disconnected" in result
        assert conn_id not in connections
        serial_instance.close.assert_called_once()

    def test_disconnect_rs485_not_found(self) -> None:
        with pytest.raises(ValueError, match="Connection not found"):
            disconnect_rs485("invalid_id")


class TestReadRS485:
    def test_read_rs485_success(self, mock_serial: tuple[MagicMock, MagicMock]) -> None:
        mock, serial_instance = mock_serial
        serial_instance.read.return_value = b"\x01\x03\x00\x00"
        conn_id = connect_rs485("/dev/ttyUSB0")

        result = read_rs485(conn_id, length=1024)

        assert result == "01030000"
        serial_instance.read.assert_called_once()

    def test_read_rs485_connection_not_found(self) -> None:
        with pytest.raises(ValueError, match="Connection not found"):
            read_rs485("invalid_id")

    def test_read_rs485_connection_closed(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        serial_instance.is_open = False
        conn_id = connect_rs485("/dev/ttyUSB0")

        with pytest.raises(OSError, match="not open"):
            read_rs485(conn_id)

    def test_read_rs485_invalid_length_zero(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        conn_id = connect_rs485("/dev/ttyUSB0")

        with pytest.raises(ValueError, match="Length must be between"):
            read_rs485(conn_id, length=0)

    def test_read_rs485_invalid_length_exceeds_max(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        conn_id = connect_rs485("/dev/ttyUSB0")

        with pytest.raises(ValueError, match="Length must be between"):
            read_rs485(conn_id, length=70000)


class TestWriteRS485:
    def test_write_rs485_success(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        serial_instance.write.return_value = 4
        conn_id = connect_rs485("/dev/ttyUSB0")

        result = write_rs485(conn_id, "01 03 00 00")

        assert result == 4
        serial_instance.write.assert_called_once_with(b"\x01\x03\x00\x00")

    def test_write_rs485_no_spaces(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        serial_instance.write.return_value = 2
        conn_id = connect_rs485("/dev/ttyUSB0")

        result = write_rs485(conn_id, "0103")

        assert result == 2

    def test_write_rs485_connection_not_found(self) -> None:
        with pytest.raises(ValueError, match="Connection not found"):
            write_rs485("invalid_id", "0103")

    def test_write_rs485_connection_closed(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        serial_instance.is_open = False
        conn_id = connect_rs485("/dev/ttyUSB0")

        with pytest.raises(OSError, match="not open"):
            write_rs485(conn_id, "0103")

    def test_write_rs485_empty_data(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        conn_id = connect_rs485("/dev/ttyUSB0")

        with pytest.raises(ValueError, match="No valid hex data"):
            write_rs485(conn_id, "   ")

    def test_write_rs485_invalid_hex_odd_length(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        conn_id = connect_rs485("/dev/ttyUSB0")

        with pytest.raises(ValueError, match="Hex data must have even length"):
            write_rs485(conn_id, "123")

    def test_write_rs485_invalid_hex_characters(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        conn_id = connect_rs485("/dev/ttyUSB0")

        with pytest.raises(ValueError, match="Invalid hex data"):
            write_rs485(conn_id, "GGGG")


class TestGetConnectionStatus:
    def test_get_connection_status_success(
        self, mock_serial: tuple[MagicMock, MagicMock]
    ) -> None:
        mock, serial_instance = mock_serial
        conn_id = connect_rs485("/dev/ttyUSB0", baudrate=19200)

        result = get_connection_status(conn_id)

        assert result["connection_id"] == conn_id
        assert result["port"] == "/dev/ttyUSB0"
        assert result["is_open"] is True
        assert result["baudrate"] == 19200
        assert result["bytes_sent"] == 0
        assert result["bytes_received"] == 0

    def test_get_connection_status_not_found(self) -> None:
        with pytest.raises(ValueError, match="Connection not found"):
            get_connection_status("invalid_id")


class TestRS485Connection:
    def test_connection_creates_uuid(self) -> None:
        conn = RS485Connection(
            port="/dev/ttyUSB0",
            baudrate=9600,
            parity="N",
            stopbits=1,
            bytesize=8,
            timeout=1.0,
        )
        assert conn.connection_id.startswith("conn_")
        assert len(conn.connection_id) == 17


class TestParityMap:
    def test_parity_map_values(self) -> None:
        assert PARITY_MAP["N"] == "none"
        assert PARITY_MAP["E"] == "even"
        assert PARITY_MAP["O"] == "odd"
