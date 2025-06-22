from random import random
from time import sleep

def wait():
    """Function to wait for a random period between 1 and 5 seconds."""

    period = random() * 4 + 1
    sleep(period)
