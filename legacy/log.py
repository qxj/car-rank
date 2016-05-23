#!/usr/bin/python
# coding=utf-8


import logging
import logging.handlers
import traceback
import StringIO
import inspect


def init_log(logtofile="test.log", level=logging.DEBUG, logtostderr=False,
             logname=""):
    """
    @logname: log file name
    @level:   logging.DEBUG/INFO/WARN/ERROR/CRITICAL
    @logtostderr: boolean
    """

    logger = logging.getLogger(logname)
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


def error_info():
    """
    自定义错误信息

    :return:
    """
    stack = inspect.stack()
    stack_len = len(stack)
    msgs = []
    if stack_len > 0:
        bottom_stack = stack[stack_len - 1]
        frame, script_path, line, module_name, codes, _ = bottom_stack
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        message = fp.getvalue()
        msgs = ['Scripts:' + script_path, 'Line number:' +
                str(line), 'Module_name:' + module_name]
        msgs.append(message)
    msg = '\n'.join(msgs)
    return msg


if __name__ == "__main__":
    log = init_log(None, logging.INFO, logtostderr=True)
    log.debug("debug")
    log.info("info")
    log.warn("warn")
    log.error("error")
    log.critical("critical")
