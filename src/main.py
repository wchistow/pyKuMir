import logging

from interface import run
from metadata import VERSION

logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(module)s.%(funcName)s:%(lineno)s:%(message)s',
    level=logging.INFO,
)

if __name__ == '__main__':
    run(VERSION)
