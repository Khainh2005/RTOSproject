from yolo_uno import *
from pins import *
from lcd1602 import *
from dht20 import *
import asyncio

led_D13 = Pins(D13_PIN)
rgb_led_D3 = RGBLed(D3_PIN, 4)
rgb_led_D5 = RGBLed(D5_PIN, 4)
rgb_led_D7 = RGBLed(D7_PIN, 4)

lcd1602 = LCD1602()
dht20 = DHT20()

sensor_queue = []
sensor_ready_sem = asyncio.Semaphore(0)

lcd_queue = []
lcd_sem = asyncio.Semaphore(0)

heater_queue = []
heater_sem = asyncio.Semaphore(0)

cooler_sem = asyncio.Semaphore(0)
humidifier_sem = asyncio.Semaphore(0)

cooler_finished_sem = asyncio.Semaphore(0)
humidifier_finished_sem = asyncio.Semaphore(0)

MAX_ITEMS = 2

async def task_monitoring():
    pass

async def task_decision():
    pass

async def task_cooler():
    pass

async def task_heater():
    pass

async def task_humidifier():
    pass

async def task_LCD():
    pass

def add_latest(queue, sem, data):
    if len(queue) < MAX_ITEMS:
        queue.append(data)
        sem.release()
    else:
        queue.pop(0)
        queue.append(data)

async def setup():
    create_task(task_monitoring())
    create_task(task_decision())
    create_task(task_cooler())
    create_task(task_heater())
    create_task(task_humidifier())
    create_task(task_LCD())

async def main():
    await setup()
    while True:
        await asleep_ms(100)

run_loop(main())
