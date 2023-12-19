import logging


def setup_logger(logger_name):
    # Create a logger
    logger = logging.getLogger(logger_name)

    # Set the logging level
    logger.setLevel(logging.DEBUG)

    # Create a file handler and set the formatter
    file_handler = logging.FileHandler("my_assistant_bot_log.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Create a stream handler to print log messages to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
