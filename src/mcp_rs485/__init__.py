__version__ = "0.1.0"
__all__ = ["mcp", "rs485_server"]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import rs485_server

try:
    from .server import rs485_server
except ImportError:
    pass
