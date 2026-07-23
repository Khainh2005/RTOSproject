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
        
        # Send to LCD
        if len(lcd_queue) < MAX_ITEMS:
            lcd_queue.append(data)
            lcd_sem.release()

        # Heater decision
        if len(heater_queue) < MAX_ITEMS:
            heater_queue.append(data)
            heater_sem.release()
            
        await asleep_ms(5000)

async def task_decision():
    while True:
        await sensor_ready_sem.acquire()
        
        data = sensor_queue.pop(0)

        temp = data["temp"]
        humi = data["humi"]
        
        heater_task_on = False
        humi_task_on = False

        # Cooler decision
        if temp > 28:
            cooler_sem.release()
            heater_task_on = True

        # Humidifier decision
        if humi < 40:
            humidifier_sem.release()
            humi_task_on = True
            
        if heater_task_on:
            await cooler_finished_sem.acquire()
        if humi_task_on:
            await humidifier_finished_sem.acquire()

async def task_cooler():
    while True:
        await cooler_sem.acquire()
        
        rgb_led_D5.show(0, hex_to_rgb('#00ff00')) #(Green)
        await asleep_ms(5000)
        rgb_led_D5.show(0, hex_to_rgb('#000000'))
        cooler_finished_sem.release()


async def task_heater():
    while True:
        await heater_sem.acquire()

        temp = heater_queue.pop(0)["temp"]
        if 20 <= temp <= 25:
            rgb_led_D3.show(0, hex_to_rgb('#00ff00'))
        elif 15 <= temp <= 30:
            rgb_led_D3.show(0, hex_to_rgb('#ffff00'))
        else:
            rgb_led_D3.show(0, hex_to_rgb('#ff0000'))

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
