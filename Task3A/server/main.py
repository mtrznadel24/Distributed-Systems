import sys
import Ice
import SmartHome
from devices import FridgeI, PTZCameraI, BlindsWithLamelsI, NightVisionCameraI


class DeviceManagerI(SmartHome.DeviceManager):
    def __init__(self, devices_list):
        self.devices_list = devices_list

    def getAvailableDevices(self, current=None):
        return self.devices_list


def run_server(port):
    with Ice.initialize(sys.argv) as communicator:
        adapter = communicator.createObjectAdapterWithEndpoints("SmartHomeAdapter", f"default -p {port}")

        fridge = FridgeI("Kitchen Fridge")
        camera1 = PTZCameraI("Garage Camera")
        camera2 = PTZCameraI("Backyard Camera")
        camera3 = NightVisionCameraI("Inside Camera")
        blinds = BlindsWithLamelsI("Living room Blinds")

        adapter.add(fridge, Ice.stringToIdentity("Fridge"))
        adapter.add(camera1, Ice.stringToIdentity("Cam1"))
        adapter.add(camera2, Ice.stringToIdentity("Cam2"))
        adapter.add(camera3, Ice.stringToIdentity("Cam3"))
        adapter.add(blinds, Ice.stringToIdentity("Blind"))

        available_devices = ["Fridge", "Cam1", "Cam2", "Cam3", "Blind"]
        manager = DeviceManagerI(available_devices)
        adapter.add(manager, Ice.stringToIdentity("DeviceManager"))

        adapter.activate()
        print(f"Server ICE is working on port {port}. Waiting for connection...")

        communicator.waitForShutdown()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    run_server(port)