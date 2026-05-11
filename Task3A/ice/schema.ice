
module SmartHome {

    exception DeviceBrokenException { string deviceId; };
    exception OpenedDoorException {string deviceId; };
    exception OutOfBoundsException {string deviceId; };
    exception OutofTiltException {string deviceId; };

    interface Device {
        string getName();
        string getStatus();
    };

    struct FridgeState {
        float currentTemp;
        float targetTemp;
    };

    struct CameraPosition {
        int x;
        int y;
        int zoom;
    };

    struct BlindState {
        int positionPercent;
        int lamelsAngle;
    };

    sequence<byte> ImageBytes;
    sequence<string> DeviceList;

    interface Fridge extends Device {
        void setTargetTemperature(float temp) throws DeviceBrokenException;
        FridgeState getState() throws OpenedDoorException;
    };

    interface Camera extends Device{
        ImageBytes takeScreenShot() throws DeviceBrokenException;
    };

    interface PTZCamera extends Camera {
        void setPosition(CameraPosition pos) throws OutOfBoundsException;
        CameraPosition getPosition();
    };

    interface NightVisionCamera extends Camera {
        void setNightVisionMode(bool isOn);
        bool getNightVisionMode();
    };

    interface Blinds extends Device{
        void setPosition(int percent) throws OutOfBoundsException;
        BlindState getState();
    };

    interface BlindsWithLamels extends Blinds {
        int setTilt(int angle) throws OutofTiltException;
    };

    interface DeviceManager {
        DeviceList getAvailableDevices();
    };

};