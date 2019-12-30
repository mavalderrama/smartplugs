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
    "reset": '{"system":{"reset":{"delay":1}}}',
    "energy": '{"emeter":{"get_realtime":{}}}',
    # HS220
    "bright": '{"smartlife.iot.dimmer": {"set_brightness": {"brightness": %d}}}',
}


# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
def encrypt(string):
    key = 171
    result = []
    chars = isinstance(string[0], str)
    if chars:
        string = map(ord, string)
    for plain in string:
        key ^= plain
        result.append(key)
    return b"".join(map(chr, result)) if chars else bytes(result)


def decrypt(string):
    key = 171
    result = []
    chars = isinstance(string[0], str)
    if chars:
        string = map(ord, string)
    for cipher in string:
        result.append(key ^ cipher)
        key = cipher
    return b"".join(map(chr, result)) if chars else bytes(result)


class CommFailure(Exception):
    pass


# Send command and receive reply
def comm(ip, command, port=9999):
    dec = isinstance(command, str)
    if dec:
        command = command.encode()
    try:
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.connect((ip, port))
        sock_tcp.send(pack(">I", len(command)) + encrypt(command))
        data = sock_tcp.recv(2048)
        dlen = 4 + unpack(">I", data[:4])[0]
        while len(data) < dlen:
            data += sock_tcp.recv(2048)
        sock_tcp.close()
    except socket.error:
        raise CommFailure("Could not connect to host %s:%d" % (ip, port))
    finally:
        sock_tcp.close()
    res = decrypt(data[4:])
    return res.decode() if dec else res


class KASA(object):
    def __init__(self, name, hostname):
        try:
            self.name = name
            self.hostname = self.valid_hostname(hostname)
        except Exception as ex:
            print("error", ex)

    @staticmethod
    def valid_hostname(hostname):
        try:
            socket.gethostbyname(hostname)
        except socket.error:
            print("Invalid hostname")
        return hostname

    def send(self, command):
        reply = ""
        try:
            reply = comm(self.hostname, COMMANDS[command])
            error_code = len(reply) <= 0
        except CommFailure as e:
            error_code = 2
            print("<<%s>>" % (str(e),))
            print("Error code: ", error_code)
        finally:
            print("%-16s %s" % ("Sent(%d):" % (len(command),), command))
            # print("%-16s %s" % ("Received(%d):" % (len(reply),), reply))
            return reply
