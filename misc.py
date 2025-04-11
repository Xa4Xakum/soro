from loguru import logger
import sys


def set_loggers():
    logger.remove()
    logger.add(
        'logs/logs.log',
        format="<green>{time:HH:mm:ss.SSS}</green> - <level>{level: <7}</level> - <level>{message}</level>",
        level='DEBUG',
        backtrace=True,
        diagnose=True,
        rotation='10 MB',
        retention='3 day',
        colorize=True,
        catch=True
    )
    logger.add(
        'errors/errors.log',
        format="<green>{time:HH:mm:ss.SSS}</green> - <level>{level: <7}</level> - <level>{message}</level>",
        level='ERROR',
        backtrace=True,
        diagnose=True,
        rotation='10 MB',
        retention='2 week',
        catch=True,
        colorize=True
    )
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss.SSS}</green> - <level>{level: <7}</level> - <level>{message}</level>",
        level='DEBUG',
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
