import logging

from abinbev_test.utils.logger import get_logger


def test_get_logger_returns_logger():
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)


def test_get_logger_level_is_info():
    logger = get_logger("test_logger_level")
    assert logger.level == logging.INFO


def test_get_logger_has_handler():
    logger = get_logger("test_logger_handler")
    assert len(logger.handlers) > 0


def test_get_logger_no_duplicate_handlers():
    logger1 = get_logger("test_logger_dedup")
    handler_count = len(logger1.handlers)

    logger2 = get_logger("test_logger_dedup")
    assert len(logger2.handlers) == handler_count


def test_get_logger_name():
    logger = get_logger("my_engine")
    assert logger.name == "my_engine"
