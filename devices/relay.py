import json
from abc import ABC

from server.tplink_smartplug import Kasa
from .device import Device


class Relay(Device):
    def __init__(self, hostname: str, name: str = "switch"):
        super().__init__(name, hostname)
        self.device = Kasa(hostname=hostname)
        self.relay_state = self.get_status()["system"]["get_sysinfo"]["relay_state"]
        self.led_state = self.device.send()

    def toggle(self, retry: int = 0):
        retries = retry
        try:
            if self.relay_state:
                response = json.loads(
                    self.device.send(
                        command_type="system",
                        command="set_relay_state",
                        sub_command="state",
                        state=0,
                    )
                )
            else:
                response = json.loads(
                    self.device.send(
                        command_type="system",
                        command="set_relay_state",
                        sub_command="state",
                        state=1,
                    )
                )
            if not response["system"]["get_sysinfo"]["err_code"]:
                # if err_code == 0, updates the realay_state
                self.relay_state = self.get_status()["system"]["get_sysinfo"][
                    "relay_state"
                ]
            else:
                if retries < 3:
                    self.toggle(retries + 1)
                else:
                    raise Exception("Getting error as a response from the device")
        except Exception as error:
            raise Exception("Exception at Relay.toggle => {}".format(error))

    def turn_on(self, retry: int = 0):
        retries = retry
        try:
            if not self.relay_state:
                response = json.loads(
                    self.device.send(
                        command_type="system",
                        command="set_relay_state",
                        sub_command="state",
                        state=1,
                    )
                )
                if not response["system"]["set_relay_state"]["err_code"]:
                    # if err_code == 0, updates the realay_state
                    self.relay_state = self.get_status()["system"]["get_sysinfo"][
                        "relay_state"
                    ]
                else:
                    if retries < 3:
                        self.turn_on(retries + 1)
                    else:
                        raise Exception("Getting error as a response from the device")
        except Exception as error:
            raise Exception("Exception at Relay.turn_on => {}".format(error))

    def turn_off(self, retry: int = 0):
        retries = retry
        try:
            if self.relay_state:
                response = json.loads(
                    self.device.send(
                        command_type="system",
                        command="set_relay_state",
                        sub_command="state",
                        state=0,
                    )
                )
                if not response["system"]["set_relay_state"]["err_code"]:
                    # if err_code == 0, updates the realay_state
                    self.relay_state = self.get_status()["system"]["get_sysinfo"][
                        "relay_state"
                    ]
                else:
                    if retries < 3:
                        self.turn_on(retries + 1)
                    else:
                        raise Exception("Getting error as a response from the device")
        except Exception as error:
            raise Exception("Exception at Relay.turn_on => {}".format(error))

    def get_status(self, retry: int = 0) -> dict:
        retries = retry
        try:
            response = json.loads(self.device.send())
            if not response:
                if retries < 3:
                    self.get_status(retries + 1)
                else:
                    raise Exception("Getting error as a response from the device")
            return response
        except Exception as error:
            raise Exception("Comms error at Relay.get_status => {}".format(error))

    def led_off(self, retry: int = 0) -> dict:
        retries = retry
        try:
            response = json.loads(
                self.device.send(
                    command_type="system",
                    command="set_led_off",
                    sub_command="off",
                    state=1,
                )
            )
            if not response:
                if retries < 3:
                    self.led_off(retries + 1)
                else:
                    raise Exception("Getting error as a response from the device")
            return response
        except Exception as error:
            raise Exception("Comms error at Relay.led_off => {}".format(error))

    def led_on(self, retry: int = 0):
        retries = retry
        try:
            response = json.loads(
                self.device.send(
                    command_type="system",
                    command="set_led_off",
                    sub_command="off",
                    state=0,
                )
            )
            if not response:
                if retries < 3:
                    self.led_off(retries + 1)
                else:
                    raise Exception("Getting error as a response from the device")
            return response
        except Exception as error:
            raise Exception("Comms error at Relay.led_off => {}".format(error))

    def schedule(self, **kwargs):
        # TODO program this with sqlite and threads
        pass

    def reboot(self, time_delay):
        return self.device.send(
            command_type="system",
            command="reset",
            sub_command="delay",
            state=time_delay,
        )

    def reset_factory_default(self):
        return self.device.send(
            command_type="system", command="reset", sub_command="delay"
        )

    def set_status(self, **kwargs):
        pass
