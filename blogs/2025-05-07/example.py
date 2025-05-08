import logging
import time

logger = logging.getLogger(__name__)


def main():
    logger.info("Hello from the logger")
    while True:
        time.sleep(100)


if __name__ == '__main__':
    # Use a log config file when really doing this.
    logging.basicConfig(level=logging.INFO)
    main()
