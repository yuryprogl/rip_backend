import random

def calc(item):
    return item["volume"] * item["temperature"] * random.uniform(0.1, 0.5)