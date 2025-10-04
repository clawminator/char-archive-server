import platform
import subprocess


def ping(host: str):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    https://stackoverflow.com/questions/2953462/pinging-servers-in-python/32684938#32684938
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command, stdout=subprocess.DEVNULL) == 0
