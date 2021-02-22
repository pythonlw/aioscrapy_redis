# -*- coding: utf-8 -*- 
# Time:2020/4/3
import logging
from datetime import datetime

def log_count(spider):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logfile = './{}.log'.format(spider.name)
    fh = logging.FileHandler(logfile, mode='a')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


# if __name__ == '__main__':
#     spider=Spider_cls()
#     logger=log_count(spider)
#     logger.info('info message'+str(datetime.now()))

