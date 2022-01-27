import os.path
import asyncio
import argparse
import uuid
import csv
import copy
import numpy  as np
import pandas as pd

import winrt.windows.devices.bluetooth.advertisement as winBLE
from winrt.windows.storage.streams import DataReader
from winrt.windows.devices.bluetooth import BluetoothLEDevice
from winrt.windows.storage.streams import Buffer
from winrt.windows.storage.streams import DataWriter, DataReader

from device import mokosmart

def create_csv(path: str, filename: str = 'file.csv') -> None:
    """This function create/overwrites a csv with filename at a specified path.

    Args:
        path     (str): The path to directory that the csv file should be located at.

        filename (str): The filename of the particular csv file. This should be in the 
                        format 'your_desired_filename.csv'
    """
    
    header = ['mac_add','address', 'major', 'minor', 'button_status']

    if not os.path.isfile(path + filename):
        with open(path + filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    return path + filename, header

def update_df(df, cols):
    df = df.append(cols, ignore_index=True)
    df = df.drop_duplicates(subset=['mac_add'])
    return df

async def discover():

    devices = []

    def filter_cycled_ibeacon(evt, data, beacon_type='CYCLED iBeacon'):
        beacon_uuid = uuid.UUID(bytes=bytes(data[2:18]))
        if str(beacon_uuid) == '4d0395ff-6470-44ac-9550-a27b3e6306e1':
            beacon_info = {}
            beacon_info['address'] = evt.bluetooth_address
            beacon_info['mac_add'] = _format_bdaddr(beacon_info['address'])
            beacon_info['major']   = int.from_bytes(bytearray(data[18:20]), 'big', signed=False)
            beacon_info['minor']   = int.from_bytes(bytearray(data[20:22]), 'big', signed=False)
            beacon_info['button_status'] = 3

            print(f'\t\tDetected {beacon_type}: {beacon_info["mac_add"]}')
            return beacon_info
        else:
            return None

    def _format_bdaddr(a):
        return ":".join("{:02X}".format(x) for x in a.to_bytes(6, byteorder="big"))

    def on_advert(sender, evt):
        # filter CYCLED iBeacons
        for m_data_buf in evt.advertisement.manufacturer_data:
            if m_data_buf.company_id == 0x004c:
                data_reader = DataReader.from_buffer(m_data_buf.data)
                m_data      = data_reader.read_bytes(m_data_buf.data.length)
                if m_data[0] == 0x02:
                    cycled_beacon = filter_cycled_ibeacon(evt, data=m_data)

                    # append to csv
                    if cycled_beacon:
                        if len(devices) == 0:
                            devices.append(cycled_beacon)
                        else:
                            if cycled_beacon not in devices:
                                devices.append(cycled_beacon)

    watcher = winBLE.BluetoothLEAdvertisementWatcher()
    watcher.add_received(on_advert)

    watcher.start()
    await asyncio.sleep(2)
    watcher.stop()

    return devices

async def set_beacon_button(device , beacon: mokosmart, enable=False):
    address =  device['address']
    data    =  beacon.char_params_data["set_button_power"] + (b'\x01' if enable else b'\x00')
    
    print('\t\tConnecting to ' + device['mac_add'])
    connection = await BluetoothLEDevice.from_bluetooth_address_async(address)
    x          = await  connection.get_gatt_services_async()

    for i in x.services:
        chars = await i.get_characteristics_async()
        for y in chars.characteristics:
            if str(y.uuid) == "e62a0002-1362-4f28-9327-f5b74e970801":

                writer = DataWriter()
                writer.write_bytes(list(data))
                buf = writer.detach_buffer()
                result = await y.write_value_with_result_async(buf)

                check = await y.read_value_async()
                buf_data = DataReader.from_buffer(check.value)
                
                success = buf_data.read_bytes(5)[-1]
                
                # 0 - off
                # 1 - on
                # 2 - protocol error occured
                # 3 - unknown
                if success is not None:
                    print(f'\t\tBeacon with id {device["mac_add"]} has its button been turned ' + ('on!' if enable else 'off!'))
                    return success
                else:
                    return 2

async def set_all_beacon_button(beacon: mokosmart, save_factor:int=10, enable=False):

    # beacon database
    path, header = create_csv('./database/', 'file.csv')
    beacon_db = pd.read_csv(path, header=0)

    # device parameters
    devices = []
    beacon  = beacon

    # Turn em all off
    cnt = 1
    while True:
        # discover new beacons and update dataframe
        devices   = await discover()
        beacon_db = update_df(beacon_db, devices)
        
        # set all beacons with gatt_success False off
        subset_db = beacon_db.copy()[(beacon_db['button_status'] == 2) | \
                                     (beacon_db['button_status'] == 3)]
        subset_db.reset_index(inplace=False)
        subset_db['address'] = subset_db['address'].astype(np.uint64)
        
        # set them off
        for indx, row in subset_db.iterrows():
            try:
                status =  await set_beacon_button(row, beacon, enable=enable)

                if status is not None:
                    subset_db.at[indx, 'button_status'] = status
                else:
                    # just incase we loose connection somehow
                    subset_db.at[indx, 'button_status'] = 3
            except:
                continue

        # update df
        beacon_db = beacon_db.set_index('mac_add')
        subset_db = subset_db.set_index('mac_add')
        beacon_db.update(subset_db)
        beacon_db.reset_index(inplace=True)
        
        # delete subset just in case
        # copies are created
        del subset_db


        # save df to csv every save_factor loops 
        if cnt % save_factor == 0:
            _dtypes = {'mac_add':str,'address':np.uint64, 'major':int, 'minor':int, 'button_status':int}
            beacon_db = beacon_db.astype(_dtypes)

            beacon_db.to_csv(path, header=header, index=False)
        cnt += 1
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Turn the button functionality of the bluetooth beacon on/off.')

    parser.add_argument("--save_factor", help="How often to save data to csv? (Number of discover iterations)",
                        type=int)
    parser.add_argument("--enable_button", help="Turn button functionality on (True) or off (False)?",
                        type=bool)

    args = parser.parse_args()

    mokosmart_beacon = mokosmart()
    asyncio.run(set_all_beacon_button(beacon=mokosmart_beacon,save_factor=args.save_factor, enable=args.enable_button))
