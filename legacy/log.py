#!/usr/bin/python
# coding=utf-8


import logging
import logging.handlers


def init_log(logtofile="test.log", level=logging.DEBUG, logtostderr=False):
    """
    @logname: log file name
    @level:   logging.DEBUG/INFO/WARN/ERROR/CRITICAL
    @logtostderr: boolean
    """

    logger = logging.getLogger("legacy")
    logger.setLevel(level)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(filename)s:%(lineno)d:%(funcName)s] %(levelname)s: %(message)s')
    if logtofile:
        fh = logging.handlers.RotatingFileHandler(
            logtofile, maxBytes=5 * 1024 * 1024, backupCount=5)
        fh.setFormatter(formatter)
        fh.setLevel(level)
        logger.addHandler(fh)
    if logtostderr:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    log = init_log(None, logging.INFO, logtostderr=True)
    log.debug("debug")
    log.info("info")
    log.warn("warn")
    log.error("error")
    log.critical("critical")
