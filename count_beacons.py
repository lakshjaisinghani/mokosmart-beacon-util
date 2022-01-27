from beacon_util import *

async def main():
    all_devices = []
    while True:
        devices = await discover(verbose=False, watch_time=2)

        for device in devices:
            if device not in all_devices:
                all_devices.append(device)

        print("Total number of devices found : " + str(len(all_devices))) 
        

asyncio.run(main())