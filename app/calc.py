def calc(forecast, item):
    temperature = item.temperature
    return temperature / 100 * forecast.volume / 10 * 0.2
