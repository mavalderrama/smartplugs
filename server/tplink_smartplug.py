#
# TP-Link Wi-Fi Smart Plug Protocol Client
# For use with TP-Link HS-100 or HS-110
#
# by Lubomir Stroetmann
# Copyright 2016 softScheck GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import socket
from struct import pack, unpack

VERSION = 0.9

# Predefined Smart Plug Commands
# For a full list of commands, consult tplink_commands.txt
COMMANDS = {
    "info": '{"system":{"get_sysinfo":{}}}',
    "on": '{"system":{"set_relay_state":{"state":1}}}',
    "off": '{"system":{"set_relay_state":{"state":0}}}',
    "ledoff": '{"system":{"set_led_off":{"off":1}}}',
    "ledon": '{"system":{"set_led_off":{"off":0}}}',
    "cloudinfo": '{"cnCloud":{"get_info":{}}}',
    "wlanscan": '{"netif":{"get_scaninfo":{"refresh":0}}}',
    "time": '{"time":{"get_time":{}}}',
    "schedule": '{"schedule":{"get_rules":{}}}',
    "countdown": '{"count_down":{"get_rules":{}}}',
    "antitheft": '{"anti_theft":{"get_rules":{}}}',
    "reboot": '{"system":{"reboot":{"delay":1}}}',
    "reset": '{"system":{"reset":{"delay":{}}}}}',
    "energy": '{"emeter":{"get_realtime":{}}}',
    # HS220
    "bright": '{"smartlife.iot.dimmer": {"set_brightness": {"brightness": %d}}}',
}


class Commands:
    def __init__(self):
        self.command = None

    def set_command(
        self,
        type: str = "system",
        command: str = "get_sysinfo",
        sub_command: str = "state",
        state: int = 0,
    ):
        """
        Set a command to a Kasa Device
        :param type: [system, cnCloud, netif, time, schedule, count_down, anti_theft, emeter, smartlife.iot.dimmer]
        :param command: list of commands
        :return:
        COMMANDS = {
            "info": '{"system":{"get_sysinfo":{}}}',
            "on": '{"system":{"set_relay_state":{"state":1}}}',
            "off": '{"system":{"set_relay_state":{"state":0}}}',
            "ledoff": '{"system":{"set_led_off":{"off":1}}}',
            "ledon": '{"system":{"set_led_off":{"off":0}}}',
            "cloudinfo": '{"cnCloud":{"get_info":{}}}',
            "wlanscan": '{"netif":{"get_scaninfo":{"refresh":0}}}',
            "time": '{"time":{"get_time":{}}}',
            "schedule": '{"schedule":{"get_rules":{}}}',
            "countdown": '{"count_down":{"get_rules":{}}}',
            "antitheft": '{"anti_theft":{"get_rules":{}}}',
            "reboot": '{"system":{"reboot":{"delay":1}}}',
            "reset": '{"system":{"reset":{"delay":{}}}}}',
            "energy": '{"emeter":{"get_realtime":{}}}',
            # HS220
            "bright": '{"smartlife.iot.dimmer": {"set_brightness": {"brightness": %d}}}',
        }
        """
        if command not in ["set_relay_state", "set_led_off", "get_scaninfo"]:
            self.command = {type: {command: {}}}
        elif command in ["reset", "get_scaninfo"]:
            self.command = {type: {command: {sub_command: {}}}}
        else:
            self.command = {type: {command: {sub_command: state}}}

    def get_command(self):
        return json.dumps(self.command)


class CommFailure(Exception):
    pass


class Kasa:
    def __init__(self, hostname: str):
        try:
            self.ip = self.__valid_hostname(hostname)
            self.commands = Commands()
        except Exception as error:
            raise AssertionError(
                "Device hostname {}: was not available in the network => {}".format(
                    hostname, error
                )
            )

    # Encryption and Decryption of TP-Link Smart Home Protocol
    # XOR Autokey Cipher with starting key = 171
    @staticmethod
    def __encrypt(string):
        key = 171
        result = []
        chars = isinstance(string[0], str)
        if chars:
            string = map(ord, string)
        for plain in string:
            key ^= plain
            result.append(key)
        return b"".join(map(chr, result)) if chars else bytes(result)

    @staticmethod
    def __decrypt(string):
        key = 171
        result = []
        chars = isinstance(string[0], str)
        if chars:
            string = map(ord, string)
        for cipher in string:
            result.append(key ^ cipher)
            key = cipher
        return b"".join(map(chr, result)) if chars else bytes(result)

    @staticmethod
    def __valid_hostname(hostname):
        try:
            ip = socket.gethostbyname(hostname)
            return ip
        except socket.error as error:
            raise Exception("Socket Error => {}".format(error))
        except Exception as error:
            raise Exception("General exception => {}".format(error))

    # Send command and receive reply
    def __command(self, ip, command, port=9999):
        dec = isinstance(command, str)
        sock_tcp = None
        if dec:
            command = command.encode()
        try:
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.connect((ip, port))
            sock_tcp.send(pack(">I", len(command)) + self.__encrypt(command))
            data = sock_tcp.recv(2048)
            dlen = 4 + unpack(">I", data[:4])[0]
            while len(data) < dlen:
                data += sock_tcp.recv(2048)
            sock_tcp.close()
        except socket.error:
            raise CommFailure("Could not connect to host %s:%d" % (ip, port))
        finally:
            sock_tcp.close()
        res = self.__decrypt(data[4:])
        return res.decode() if dec else res

    def send(
        self,
        command_type: str = "system",
        command: str = "get_sysinfo",
        sub_command: str = "",
        state: int = 1,
        json_request: str = None,
    ):
        """
        send command to Kasa device
        :param command_type:
        :param command:
        :param sub_command:
        :param state:
        :return:
        """
        reply = ""
        try:
            if not json_request:
                self.commands.set_command(
                    type=command_type,
                    command=command,
                    sub_command=sub_command,
                    state=state,
                )
                reply = self.__command(self.ip, self.commands.get_command())
            else:
                reply = self.__command(self.ip, json_request)
            if len(reply) <= 0:
                raise Exception()
        except CommFailure as error:
            raise Exception("Communication error at ")
        finally:
            return reply if reply else None
