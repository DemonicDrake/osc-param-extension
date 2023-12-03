#!/bin/env python

"""
OSC - PARAMETER EXTENSION
Branch: Fox
Version: 0.1

With inspiration from SC Parameter Sync System by: Fuuujin
Gumroad: https://fuuujin.gumroad.com/l/OSCParameterSync

Program written by: Drake "The Nardo"
GitHub: https://github.com/DemonicDrake/osc-param-extension
Bluesky: @demonicdrake.bsky.social

Fox branch modifications by: Toddstone "The Foxo"
Bluesky: @toddstone.bsky.social
"""

import csv
import os
import threading
from pythonosc.dispatcher import Dispatcher
import sys
from os import system, name, path
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from datetime import datetime
import time

# GLOBAL Parameter to toggle logging output
LOGGING = True


class OSC:
    def __init__(self):
        self.STORED_VALUES = [-6.9] * 257
        self.FILE = File('temp_config.csv',
                         'C:/Users/Matt/PycharmProjects/OSC-AVATAR PARAMETER EXPANDER/AviConfigs/')
        self.CLIENT_IP = "127.0.0.1"  # to vrhat
        self.CLIENT_PORT = 9000  # to vrhat
        self.PARAM_ID = 0
        self.PARAM_VALUE = 0

    def sync_to_remote(self):
        client = SimpleUDPClient(self.CLIENT_IP, self.CLIENT_PORT)
        c = 0
        for x in range(len(self.STORED_VALUES)):
            if x != 0 and self.STORED_VALUES[x] != -6.9:
                c += 1
                client.send_message("/avatar/parameters/remote_id", x)
                client.send_message("/avatar/parameters/remote_value", float(self.STORED_VALUES[x]))
                if LOGGING: print(
                    f"\033[30;43;6;1mDEBUG:\033[0mI just pushed out {x},{self.STORED_VALUES[x]} to the client!")
                time.sleep(0.0039)
        print(f" @ {datetime.now()}  ::  \033[32;49m%d Parameter%s Synced\033[0m"
              % (c, (c != 1 and 's' or 'Ø' and 's')))

    def avatar_handler(self, _address, *args: str):
        self.FILE.write_values(self.STORED_VALUES)
        self.FILE = File(f'{str(args[0])}_config.csv',
                         'C:/Users/Matt/PycharmProjects/OSC-AVATAR PARAMETER EXPANDER/AviConfigs/')
        if LOGGING: print("I got myself an AVATAR_ID!")
        self.STORED_VALUES = self.FILE.read_values()

    # PROBLEM:
    # When the avatar animator sends out ID = 0, denoting the client side has finished modifying the
    # associated parameter value it causes the update push to send the new parameter value with ID 0.
    def id_handler(self, _address, *args):
        if LOGGING: print(f"\033[30;43;6;1mDEBUG:\033[0mReceived id: {args[0]}")
        if args[0] == 0:
            self.FILE.write_values(self.STORED_VALUES)
            return
        self.STORED_VALUES[args[0]] = self.PARAM_VALUE

    def value_handler(self, _address, *args):
        if LOGGING: print(f"\033[30;43;6;1mDEBUG:\033[0mReceived data: {args[0]}")
        self.PARAM_VALUE = args[0]


class File:
    def __init__(self, file_name: str, file_dir: str):
        self.FILE_NAME = file_name
        self.FILE_DIR = file_dir
        self.FILE_PATH = os.path.join(self.FILE_DIR, self.FILE_NAME)

        if path.isdir(self.FILE_DIR) is not True:
            if LOGGING: print(f"\033[30;43;6;1mDEBUG:\033[0mI'm about to make a dir!\n{self.FILE_DIR}")
            os.makedirs(self.FILE_DIR)
            self.write_values([-6.9] * 257)
            print(f"\033[30;43;6;1mNOTICE:\033[0m Directory \033[37;40m\'{self.FILE_DIR}\'\033[0m "
                  + "was \033[31;49mnot found\033[0m, so it was created along with configuration file(s)...")
            return
        elif path.isfile(self.FILE_PATH) is not True:
            if LOGGING: print(f"\033[30;43;6;1mDEBUG:\033[0mI'm about to make a file!\n{self.FILE_PATH}")
            self.write_values([-6.9] * 257)
            print(f"\033[30;43;6;1mNOTICE:\033[0m Configuration file \033[37;40m\'{self.FILE_NAME}\'\033[0m "
                  + "was \033[31;49mnot found\033[0m, so it was created...")
            return
        if LOGGING: print(f"\033[30;43;6;1mDEBUG:\033[0mI think this document exists! {self.FILE_PATH}")

    def read_values(self) -> list:
        stored_values = []
        if LOGGING: print("\033[30;43;6;1mDEBUG:\033[0mI'm going to read the CSV now!")
        with open(self.FILE_PATH, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                stored_values.append(float(row[1]))
        return stored_values

    def write_values(self, stored_values: list):
        if LOGGING: print(f"\033[30;43;6;1mDEBUG:\033[0mI'm about to updated the CSV")
        with open(self.FILE_PATH, 'w', newline='') as file:
            writer = csv.writer(file)
            for i, value in enumerate(stored_values):
                writer.writerow([i, value])


def main():
    server_ip = "127.0.0.1"  # from vrchat
    server_port = 9001  # from vrchat
    osc = OSC()

    dispatcher: Dispatcher = Dispatcher()
    dispatcher.map("/avatar/change", osc.avatar_handler)
    dispatcher.map("/avatar/parameters/local_id", osc.id_handler)
    dispatcher.map("/avatar/parameters/local_value", osc.value_handler)

    server = ThreadingOSCUDPServer((server_ip, server_port), dispatcher)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    print(f"\033[0mSending to \033[37;49;1m{osc.CLIENT_IP}:{osc.CLIENT_PORT}\033[0m...\n"
          + f"\033[0mListening on \033[37;49;1m{server_ip}:{server_port}\033[0m...\n\n")

    while True:
        osc.sync_to_remote()
        time.sleep(1)


if __name__ == '__main__':
    if name == 'nt':
        system('cls')
    else:
        system('clear')
    print(
        "                        \033[35;40;1m██████████  ████████\033[0m\n                      \033[35;40;1m██▒▒▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒██████\033[0m\n                        \033[35;40;1m██▒▒▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒████\033[0m\n                    \033[35;40;1m██    ██▒▒▒▒██████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒███\033[0m\n                  \033[35;40;1m████    ██████▒▒██▒▒▒▒████▒▒▒▒██▒▒▒▒▒▒▒▒████\033[0m\n                \033[35;40;1m██▒▒██████▒▒▒▒▒▒██▒▒▒▒██▒▒▒▒██▒▒▒▒██▒▒▒▒██▒▒▒▒██\033[0m\n      \033[35;40;1m██      ████▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒██▒▒▒▒██▒▒▒▒██▒▒▒▒██\033[0m\n      \033[35;40;1m██████  ████▒▒██▒▒▒▒▒▒████▒▒▒▒▒▒▒▒▒▒▒▒▒▒████▒▒████▒▒▒▒██▒▒▒▒██\033[0m\n      \033[35;40;1m██▒▒████▒▒██▒▒██▒▒████▒▒██▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒████▒▒██▒▒████▒▒██\033[0m\n      \033[35;40;1m██▒▒▒▒██▒▒██▒▒▒▒██▒▒▒▒██▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒██▒▒██  ██▒▒██\033[0m\n        \033[35;40;1m██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██████▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒██▒▒▒▒████  ██▒▒██\033[0m\n          \033[35;40;1m██▒▒▒▒▒▒▒▒▓▓▒▒▒▒▒▒██████▒▒▒▒▒▒██▒▒▒▒▒▒████████▒▒▒▒▒▒██  ██▒▒██\033[0m\n          \033[35;40;1m██▒▒▒▒▒▒▒▒░░▓▓▒▒████▒▒▒▒██▒▒██▒▒▒▒████▒▒▒▒▒▒▒▒██▒▒▒▒██  ██▒▒██\033[0m\n  \033[35;40;1m██████████▒▒▒▒▒▒▒▒░░░░▒▒████▒▒▒▒██▒▒██▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒██  ████\033[0m\n    \033[35;40;1m██████████▒▒▒▒▒▒▒▒░░▒▒██  ██▒▒▒▒██████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒██  ████                ██████████████\033[0m\n            \033[35;40;1m██████▒▒▒▒▒▒▒▒██  ██▒▒▒▒██▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒██    ██          ████████▒▒▒▒▒▒▒▒▒▒▒▒██\033[0m\n          \033[35;40;1m████    ██▒▒▒▒▒▒██  ██▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██              ████▒▒▒▒▒▒▒▒██████████▒▒██\033[0m\n          \033[35;40;1m██      ████▒▒▒▒██  ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██          ██████▒▒▒▒▒▒████        ████▒▒██\033[0m\n                \033[35;40;1m██▒▒▒▒████  ██▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒██        ████▒▒▒▒▒▒▒▒██              ██████\033[0m\n              \033[35;40;1m██▒▒▒▒▒▒▒▒██  ██▒▒▒▒██▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒██    ████▒▒▒▒▒▒▒▒██                ██████\033[0m\n            \033[35;40;1m██▒▒▒▒▒▒▒▒██    ██▒▒▒▒▒▒████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒▒▒██████▒▒▒▒▒▒▒▒██                    ████\033[0m\n          \033[35;40;1m██▒▒▒▒▒▒▒▒██    ██▒▒▒▒▒▒▒▒██      ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██\033[0m\n        \033[35;40;1m██▒▒▒▒▒▒▒▒██      ██▒▒▒▒▒▒██        ████▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██\033[0m\n      \033[35;40;1m██▒▒▒▒▒▒▒▒██      ██▒▒▒▒▒▒▒▒██  ██████▒▒▒▒██▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██\033[0m\n        \033[35;40;1m████████        ██▒▒▒▒▒▒██  ██▒▒▒▒▒▒▒▒▒▒▒▒████████  ████▒▒▒▒▒▒██████\033[0m\n                          \033[35;40;1m██████      ████████████              ██████\033[0m\n\n  \033[37;49;1mProgram Written by:\033[0m \033[35;40;1mDrake \"The Nardo\"\033[0m\n      \033[34;49mBluesky:\033[0m \033[34;40;4;1mhttps://bsky.app/profile/demonicdrake.bsky.social\033[0m\n")
    try:
        main()
    except KeyboardInterrupt:
        print("User Terminated...")
        sys.exit(0)
