import SmartHome

class FridgeI(SmartHome.Fridge):
    def __init__(self, name):
        self.name = name
        self.temp = 5.0
        self.target_temp = 5.0

    def getName(self, current=None):
        return self.name

    def getStatus(self, current=None):
        return f"Fridge is running. Current temp: {self.temp}C. Target temp: {self.target_temp}C"

    def setTargetTemperature(self, temp, current=None):
        if temp < -20.0:
            raise SmartHome.DeviceBrokenException(self.name)
        self.target_temp = temp

    def getState(self, current=None):
        return SmartHome.FridgeState(self.temp, self.target_temp)

class PTZCameraI(SmartHome.PTZCamera):
    def __init__(self, name):
        self.name = name
        self.pos = SmartHome.CameraPosition(0, 0, 1)

    def getName(self, current=None):
        return self.name

    def getStatus(self, current=None):
        return f"PTZ Camera online. Position: ({self.pos.x}, {self.pos.y}), Zoom: {self.pos.zoom}"

    def takeScreenShot(self, current=None):
        return [255, 216, 255, 224]

    def setPosition(self, pos, current=None):
        if pos.x < -180 or pos.x > 180:
            raise SmartHome.OutOfBoundsException(self.name)
        self.pos = pos

    def getPosition(self, current=None):
        return self.pos

class NightVisionCameraI(SmartHome.NightVisionCamera):
    def __init__(self, name):
        self.name = name
        self.night_vision = False

    def getName(self, current=None):
        return self.name

    def getStatus(self, current=None):
        state_str = "ON" if self.night_vision else "OFF"
        return f"Night Vision Camera online. Night mode is {state_str}"

    def takeScreenShot(self, current=None):
        return [255, 216, 255, 224]

    def setNightVisionMode(self, isOn, current=None):
        self.night_vision = isOn

    def getNightVisionMode(self, current=None):
        return self.night_vision

class BlindsWithLamelsI(SmartHome.BlindsWithLamels):
    def __init__(self, name):
        self.name = name
        self.pos_percent = 0
        self.angle = 0

    def getName(self, current=None):
        return self.name

    def getStatus(self, current=None):
        return "Blinds raised" if self.pos_percent == 0 else "Blinds lowered"

    def setPosition(self, percent, current=None):
        if percent < 0 or percent > 100:
            raise SmartHome.OutOfBoundsException(self.name)
        self.pos_percent = percent

    def getState(self, current=None):
        return SmartHome.BlindState(self.pos_percent, self.angle)

    def setTilt(self, angle, current=None):
        if angle < -90 or angle > 90:
            raise SmartHome.OutofTiltException(self.name)
        self.angle = angle
        return self.angle