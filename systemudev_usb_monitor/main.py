import time

import dbus
import pyudev
import usb


class Udev:
    def __init__(self, devices):
        self.devices = devices

    def __is_usb_device_initialized(udev_object):
        return (
            udev_object.get("ID_MODEL")
            and udev_object.get("ID_MODEL_ID")
            and udev_object.get("ID_VENDOR_ID")
        )

    def handle_service(name, state):
        bus = dbus.SessionBus()

        systemd = bus.get_object(
            "org.freedesktop.systemd1", "/org/freedesktop/systemd1"
        )

        manager = dbus.Interface(systemd, "org.freedesktop.systemd1.Manager")

        service = dbus.Interface(
            bus.get_object(
                "org.freedesktop.systemd1",
                object_path=manager.LoadUnit(f"{name}.service"),
            ),
            "org.freedesktop.DBus.Properties",
        )

        current_state = service.Get("org.freedesktop.systemd1.Unit", "ActiveState")

        if current_state != state:
            if state == "active":
                manager.StartUnit(f"{name}.service", "replace")
            if state == "inactive":
                manager.StopUnit(f"{name}.service", "replace")

    def handle_action(self, udev_object, device):
        if udev_object.action == "bind":
            service_state = "active"

            # wait until the sound system has initialized the device
            if self.__is_usb_device_initialized(udev_object):
                model = bytes(udev_object.get("ID_MODEL_ENC"), "utf-8").decode(
                    "unicode_escape"
                )

                # set a timeout, just in case
                tstart = time.time()

                while time.time() < tstart + 15:
                    if model in open("/proc/asound/cards").read():
                        break

        if udev_object.action == "unbind":
            service_state = "inactive"

        self.handle_service(device["service"], service_state)

    def handle_event(self, udev_object):
        if udev_object.action in ("bind", "unbind"):
            for device in self.devices:
                if udev_object.get("PRODUCT") in f"{device['vid']}/{device['pid']}":
                    self.handle_action(udev_object, device)

    def run(self):
        # check if a device is already connected
        for device in self.devices:
            # TODO: if >1 device matches {V,P}ID (model,vid,pid)
            dev = usb.core.find(
                idVendor=int(device["vid"], 16), idProduct=int(device["pid"], 16)
            )

            if dev is not None:
                self.handle_service(device["service"], "active")

        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)

        # Remove this line to listen for all devices.
        monitor.filter_by(subsystem="usb")

        observer = pyudev.MonitorObserver(
            monitor, callback=self.handle_event, name="usb-monitor-observer"
        )
        observer.daemon = False
        observer.start()
