
class mokosmart:
    def __init__(self) -> None:
        """ This is a class that defines all service and characteristic
            UUID's for a particular beacon.
        """
        
        self.name = "CYCLED iBeacon"
        
        # 180A: Device Information Service 
        self.CHAR_MODEL_NUMBER      = "00002A24-0000-1000-8000-00805F9B34FB"
        self.CHAR_SERIAL_NUMBER     = "00002A25-0000-1000-8000-00805F9B34FB"
        self.CHAR_MANUFACTURER_NAME = "00002A29-0000-1000-8000-00805F9B34FB"
        self.CHAR_FIRMWARE_REVISION = "00002A26-0000-1000-8000-00805F9B34FB"
        self.CHAR_HARDWARE_REVISION = "00002A27-0000-1000-8000-00805F9B34FB"
        self.CHAR_SOFTWARE_REVISION = "00002A28-0000-1000-8000-00805F9B34FB"

        # E62A0001: Mokosmart Unknown Param Service
        self.CHAR_LOCKED_NOTIFY     = "E62A0003-1362-4F28-9327-F5B74E970801"
        self.CHAR_THREE_AXIS_NOTIFY = "E62A0008-1362-4F28-9327-F5B74E970801"
        self.CHAR_TH_NOTIFY         = "E62A0009-1362-4F28-9327-F5B74E970801"
        self.CHAR_STORE_NOTIFY      = "E62A000A-1362-4F28-9327-F5B74E970801"
        self.CHAR_PARAMS            = "E62A0002-1362-4F28-9327-F5B74E970801"
        self.CHAR_DEVICE_TYPE       = "E62A0004-1362-4F28-9327-F5B74E970801"
        self.CHAR_SLOT_TYPE         = "E62A0005-1362-4F28-9327-F5B74E970801"
        self.CHAR_BATTERY           = "E62A0006-1362-4F28-9327-F5B74E970801"
        self.CHAR_DISCONNECT        = "E62A0007-1362-4F28-9327-F5B74E970801"
        
        # A3C87500 : Eddystone Configuration Service
        self.CHAR_ADV_SLOT          = "A3C87502-8ED3-4BDF-8A39-A01BEBEDE295"
        self.CHAR_ADV_INTERVAL      = "A3C87503-8ED3-4BDF-8A39-A01BEBEDE295"
        self.CHAR_RADIO_TX_POWER    = "A3C87504-8ED3-4BDF-8A39-A01BEBEDE295"
        self.CHAR_ADV_TX_POWER      = "A3C87505-8ED3-4BDF-8A39-A01BEBEDE295"
        self.CHAR_LOCK_STATE        = "A3C87506-8ED3-4BDF-8A39-A01BEBEDE295"
        self.CHAR_UNLOCK            = "A3C87507-8ED3-4BDF-8A39-A01BEBEDE295"
        self.CHAR_ADV_SLOT_DATA     = "A3C8750A-8ED3-4BDF-8A39-A01BEBEDE295"
        self.CHAR_RESET_DEVICE      = "A3C8750B-8ED3-4BDF-8A39-A01BEBEDE295"
        self.CHAR_CONNECTABLE       = "A3C8750C-8ED3-4BDF-8A39-A01BEBEDE295"

        # remember to add b'01' -> on or b'00' for off to each characteristic action
        # Add more from : https://github.com/BeaconX-Pro/Android-Nordic-SDK/blob/cc1759b356994a5426abc558242b6d006976022b/mokosupport/src/main/java/com/moko/support/nordic/task/ParamsTask.java#L49
        self.char_params_data = {"set_button_power": b'\xEA\x38\x00\x01'}
