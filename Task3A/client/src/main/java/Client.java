import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.Util;
import com.zeroc.Ice.ObjectPrx;
import SmartHome.*;

import java.util.Scanner;

public class Client {
    public static void main(String[] args) {
        try (Communicator communicator = Util.initialize(args)) {
            Scanner scanner = new Scanner(System.in);

            System.out.print("Enter Server Port: ");
            String port = scanner.nextLine();

            ObjectPrx baseProxy = communicator.stringToProxy("DeviceManager:default -p " + port);
            DeviceManagerPrx manager = DeviceManagerPrx.checkedCast(baseProxy);

            if (manager == null) {
                System.out.println("Could not communicate with DeviceManager.");
                return;
            }

            while (true) {
                String[] devices = manager.getAvailableDevices();
                System.out.println("\n=== Available Devices ===");
                for (int i = 0; i < devices.length; i++) {
                    System.out.println((i + 1) + ". " + devices[i]);
                }
                System.out.println("0. Exit");

                System.out.print("Choose Device: ");
                int choice = scanner.nextInt();
                scanner.nextLine();

                if (choice == 0) {
                    System.out.println("Exiting...");
                    break;
                }

                if (choice < 1 || choice > devices.length) {
                    System.out.println("Invalid choice.");
                    continue;
                }

                String selectedIdentity = devices[choice - 1];
                ObjectPrx deviceProxy = communicator.stringToProxy(selectedIdentity + ":default -p " + port);

                if (FridgePrx.checkedCast(deviceProxy) != null) {
                    FridgePrx fridge = FridgePrx.checkedCast(deviceProxy);
                    while (true) {
                        System.out.println("\n[" + fridge.getName() + " Menu]");
                        System.out.println("1. Get Status");
                        System.out.println("2. Set Target Temperature");
                        System.out.println("0. Back");
                        System.out.print("Select action: ");

                        int action = scanner.nextInt(); scanner.nextLine();
                        if (action == 0) break;

                        if (action == 1) {
                            System.out.println(">> " + fridge.getStatus());
                        } else if (action == 2) {
                            try {
                                System.out.print("Enter new target temperature: ");
                                float temp = scanner.nextFloat(); scanner.nextLine();
                                fridge.setTargetTemperature(temp);
                                System.out.println(">> SUCCESS! " + fridge.getStatus());
                            } catch (DeviceBrokenException e) {
                                System.err.println(">> ERROR: Device broken - " + e.deviceId);
                            }
                        }
                    }
                }
                else if (PTZCameraPrx.checkedCast(deviceProxy) != null) {
                    PTZCameraPrx camera = PTZCameraPrx.checkedCast(deviceProxy);
                    while (true) {
                        System.out.println("\n[" + camera.getName() + " Menu]");
                        System.out.println("1. Get Status");
                        System.out.println("2. Set Position & Zoom");
                        System.out.println("3. Take Screenshot");
                        System.out.println("0. Back");
                        System.out.print("Select action: ");

                        int action = scanner.nextInt(); scanner.nextLine();
                        if (action == 0) break;

                        if (action == 1) {
                            System.out.println(">> " + camera.getStatus());
                        } else if (action == 2) {
                            try {
                                System.out.print("Enter X: "); int x = scanner.nextInt();
                                System.out.print("Enter Y: "); int y = scanner.nextInt();
                                System.out.print("Enter Zoom: "); int zoom = scanner.nextInt();
                                scanner.nextLine();
                                camera.setPosition(new CameraPosition(x, y, zoom));
                                System.out.println(">> SUCCESS! " + camera.getStatus());
                            } catch (OutOfBoundsException e) {
                                System.err.println(">> ERROR: Out of bounds - " + e.deviceId);
                            }
                        } else if (action == 3) {
                            try {
                                byte[] img = camera.takeScreenShot();
                                System.out.println(">> Screenshot taken! Size: " + img.length + " bytes.");
                            } catch (DeviceBrokenException e) {
                                System.err.println(">> ERROR: Camera broken - " + e.deviceId);
                            }
                        }
                    }
                }
                else if (NightVisionCameraPrx.checkedCast(deviceProxy) != null) {
                    NightVisionCameraPrx camera = NightVisionCameraPrx.checkedCast(deviceProxy);
                    while (true) {
                        System.out.println("\n[" + camera.getName() + " Menu]");
                        System.out.println("1. Get Status");
                        System.out.println("2. Toggle Night Vision");
                        System.out.println("3. Take Screenshot");
                        System.out.println("0. Back");
                        System.out.print("Select action: ");

                        int action = scanner.nextInt(); scanner.nextLine();
                        if (action == 0) break;

                        if (action == 1) {
                            System.out.println(">> " + camera.getStatus());
                        } else if (action == 2) {
                            System.out.print("Turn ON? (true/false): ");
                            boolean isOn = scanner.nextBoolean(); scanner.nextLine();
                            camera.setNightVisionMode(isOn);
                            System.out.println(">> SUCCESS! " + camera.getStatus());
                        } else if (action == 3) {
                            try {
                                byte[] img = camera.takeScreenShot();
                                System.out.println(">> Screenshot taken! Size: " + img.length + " bytes.");
                            } catch (DeviceBrokenException e) {
                                System.err.println(">> ERROR: Camera broken.");
                            }
                        }
                    }
                }
                else if (BlindsWithLamelsPrx.checkedCast(deviceProxy) != null) {
                    BlindsWithLamelsPrx blinds = BlindsWithLamelsPrx.checkedCast(deviceProxy);
                    while (true) {
                        System.out.println("\n[" + blinds.getName() + " Menu]");
                        System.out.println("1. Get Status");
                        System.out.println("2. Set Position & Tilt");
                        System.out.println("0. Back");
                        System.out.print("Select action: ");

                        int action = scanner.nextInt(); scanner.nextLine();
                        if (action == 0) break;

                        if (action == 1) {
                            BlindState state = blinds.getState();
                            System.out.println(">> " + blinds.getStatus() + ". Pos: " + state.positionPercent + "%, Angle: " + state.lamelsAngle);
                        } else if (action == 2) {
                            try {
                                System.out.print("Enter position (0-100%): "); int pos = scanner.nextInt();
                                System.out.print("Enter tilt (-90 to 90): "); int tilt = scanner.nextInt();
                                scanner.nextLine();

                                blinds.setPosition(pos);
                                blinds.setTilt(tilt);
                                BlindState state = blinds.getState();
                                System.out.println(">> SUCCESS! Pos: " + state.positionPercent + "%, Angle: " + state.lamelsAngle);
                            } catch (OutOfBoundsException | OutofTiltException e) {
                                System.err.println(">> ERROR: Values out of bounds!");
                            }
                        }
                    }
                } else {
                    System.out.println("Unknown device type.");
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}