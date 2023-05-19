# ---------------------------------------------------------------------------- #
#                                   logger.py                                  #
# ---------------------------------------------------------------------------- #
import os
import logging
import time


class Logger:
    @staticmethod
    def start_log():
        """
        It creates a log file with a unique name based on the current date and time,
        and then writes a message to the log file
        """
        if not os.path.exists("logs"):
            os.makedirs("logs")
        date_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        log_file_name = f"./logs/{str(date_time)}.log"
        logging.basicConfig(
            filename=log_file_name,
            filemode="w",
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
        )
        logging.info("Log - START")
        pass

    @staticmethod
    def write_info(msg):
        logging.info(msg)
        print("> INFO: ", msg)

    @staticmethod
    def write_debug(msg):
        logging.debug(msg)
        print("> DEBUG: ", msg)

    @staticmethod
    def write_warning(msg):
        logging.warning(msg)
        print("> WARNING: ", msg)

    @staticmethod
    def write_error(msg):
        logging.error(msg)
        print("> ERROR: ", msg)

    @staticmethod
    def write_critical(msg):
        logging.critical(msg)
        print("> CRITICAL: ", msg)

    @staticmethod
    def end_log():
        logging.info("Log - END")
        logging.shutdown()
        pass
