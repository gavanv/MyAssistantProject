import logging


def setup_logger(logger_name):
    # Create a logger
    logger = logging.getLogger(logger_name)

    # Set the logging level
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create a file handler and set the formatter
    file_handler = logging.FileHandler("logs_my_assistant_bot.log")
    file_handler.setFormatter(formatter)

    # Create a stream handler to print log messages to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
