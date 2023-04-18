from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch
from uuid import uuid4

from kookaburra.log import log, setup_logging_queue


def test_logger(capsys: Any) -> None:
    log.exception("this is an exception")

    log.info(
        "testing types",
        extra={
            "string": "string",
            "bytes": b"test",
            "set": {"test", "test2"},
            "time": datetime.now(),
            "uuid": uuid4(),
        },
    )

    class MyUnsupportedType:
        def __init__(self, data: str) -> None:
            self.data = data

    log.info("testing types", extra={"random": MyUnsupportedType("test")})
    out, err = capsys.readouterr()
    assert out == ""
    assert "TypeError: Object of type MyUnsupportedType is not JSON serializable" in err


@patch("logging.getLogger")
def test_logger_not_root_handler(mock_logger: Mock) -> None:
    mock_handlers = [Mock()]
    mock_logger.return_value.handlers = mock_handlers

    setup_logging_queue()

    # Check if the original handlers have been removed from the logger
    assert len(mock_logger.return_value.handlers) == 1
