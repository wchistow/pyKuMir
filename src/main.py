import logging

from interface import run

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(module)s.%(funcName)s:%(lineno)s:%(message)s',
                    level=logging.INFO)

run()
