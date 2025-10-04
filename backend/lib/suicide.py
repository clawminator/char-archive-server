import logging
import os
import signal
import time

logger = logging.getLogger('SUICIDE')


def suicide():
    time.sleep(1)
    pid = os.getpid()
    logger.critical(f"\nShutdown took too long, killing PID {pid}\n\n")
    os.kill(pid, signal.SIGTERM)


def watchdog_suicide():
    pid = os.getpid()
    logger.critical(f'EXITING VIA KILLING CURRENT PROCESS: {pid}')
    os.kill(pid, signal.SIGTERM)


def signal_handler(sig, frame):
    watchdog_suicide()


def watchdog_expired(signum, frame):
    logger.critical("Program ran too long, initiating shutdown. If program has not exited in 30 seconds then it will be killed.")
    watchdog_suicide()
