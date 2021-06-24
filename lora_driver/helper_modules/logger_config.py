import logging

log_format = "[%(asctime)s] <%(levelname)s> %(name)s-"\
             "%(filename)s (%(lineno)d): %(message)s"
logging.basicConfig(level='DEBUG', format=log_format)
