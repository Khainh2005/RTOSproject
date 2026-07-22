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
    while True:

        data = {
            "temp": await dht20.atemperature(),
            "humi": await dht20.ahumidity()
        }

        add_latest(sensor_queue, sensor_ready_sem, data)
        
        #
        # Send to LCD
        #
        if len(lcd_queue) < MAX_ITEMS:
            lcd_queue.append(data)
            lcd_sem.release()

        #
        # Heater decision
        #
        
        if len(heater_queue) < MAX_ITEMS:
            heater_queue.append(data)
            heater_sem.release()
            
        await asleep_ms(5000)

async def task_decision():
    pass

async def task_cooler():
    pass

async def task_heater():
    pass

async def task_humidifier():

    while True:

        await humidifier_sem.acquire()

        rgb_led_D7.show(0, hex_to_rgb('#00ff00')) #(Green)
        await asleep_ms(5000)
        
        rgb_led_D7.show(0, hex_to_rgb('#ffff00')) # Yellow
        await asleep_ms(3000)
        
        rgb_led_D7.show(0, hex_to_rgb('#ff0000')) # Red
        await asleep_ms(2000)

        rgb_led_D7.show(0, hex_to_rgb('#000000'))
        humidifier_finished_sem.release()

async def task_LCD():
    while True:

        await lcd_sem.acquire()

        data = lcd_queue.pop(0)

        lcd1602.clear()

        lcd1602.show("TEMP:",0,0)
        lcd1602.show(str(data["temp"]),0,9)
        lcd1602.show(str('*C'), 0, 13)

        lcd1602.show("HUMI:",1,0)
        lcd1602.show(str(data["humi"]),1,9)
        lcd1602.show(str('%'), 1, 13)


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
