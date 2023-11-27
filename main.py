# import csv
# import sys
# import threading
# import time
#
# from pythonosc.dispatcher import Dispatcher
# from pythonosc.osc_server import ThreadingOSCUDPServer
# from pythonosc.udp_client import SimpleUDPClient
#
# local_id = 0
# local_value = 0
# remote_id = 0
# remote_value = 0
# stored_values = [-2.1] * 256
#
#
# def sync_to_remote(ip, port):
#     ip = "127.0.0.1"
#     port = 9000
#     client = SimpleUDPClient("127.0.0.1", 9000)
#     global stored_values, remote_id, remote_value
#
#     stored_values = read_values(stored_values)
#     for x in range(len(stored_values)):
#         if x == 0 or stored_values[x] == -2.1:
#             pass
#         else:
#             client.send_message("/avatar/parameters/remote_id", x)
#             client.send_message("/avatar/parameters/remote_value", bool(stored_values[x]))
#             print("Sent ->", bool(stored_values[x]), "to ID:", x)
#             time.sleep(.1)
#
#
# def id_handler(address: str, *args: float) -> None:
#     global local_id
#     local_id = args[0]
#
#
# def value_handler(address: str, *args: float) -> None:
#     global local_value
#     local_value = args[0]
#     update_list(local_id, local_value)
#     write_values(stored_values)
#
#
# def write_values(values):
#     with open("saved_params.csv", 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         for x, value in enumerate(values):
#             writer.writerow([x, value])
#
#
# def read_values(values):
#     values = []
#     with open("saved_params.csv", 'r') as csvfile:
#         reader = csv.reader(csvfile)
#         for row in reader:
#             values.append(float(row[1]))
#     return values
#
#
# def update_list(id, value):
#     global stored_values
#     if id == 0 or value == 0.5:
#         print("none")
#         pass
#     else:
#         stored_values[id] = value
#
#
# def main():
#     # from vrchat
#     server_ip = "127.0.0.1"
#     server_port = 9001
#     # to vrchat
#     client_ip = "127.0.0.1"
#     client_port = 9000
#
#     read_values(stored_values)
#
#     dispatcher = Dispatcher()
#     dispatcher.map("/avatar/parameters/local_id", id_handler)
#     dispatcher.map("/avatar/parameters/local_value", value_handler)
#     dispatcher.map("avatar/change")
#
#     server = ThreadingOSCUDPServer((server_ip, server_port), dispatcher)
#     thread = threading.Thread(target=server.serve_forever)
#     thread.daemon = True
#     thread.start()
#     print(f"\033[0mListening on \033[37;49;1m{server_ip}:{server_port}\033[0m...")
#
#     active = True
#
#     print(f"\033[0mSending on \033[37;49;1m{client_ip}:{client_port}\033[0m...")
#     print("waiting for parameter change...")
#     while active:
#         sync_to_remote(client_ip, client_port)
#         time.sleep(1)  # delay between sync passes
#
#
# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("Interrupted")
#         sys.exit(0)

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import threading
import logging
import time
import csv
import sys

class PauseFlag:
    def __init__(self):
        self.paused = False


pause_flag = PauseFlag()


class VRChatSyncSender:
    def __init__(self, client_ip, client_port):
        self.client_ip = client_ip
        self.client_port = client_port


class VRChatSyncReceiver:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

        self.stored_values = []

        dispatcher = Dispatcher()
        dispatcher.map("/avatar/parameters/local_id", self.id_handler)
        dispatcher.map("/avatar/parameters/local_value_bool", self.bool_handler)
        dispatcher.map("/avatar/parameters/local_value_float", self.float_handler)
        dispatcher.map("/avatar/change", self.avatar_change)
        # dispatcher.map("/avatar/change", temp)

        self.server = ThreadingOSCUDPServer((server_ip, server_port), dispatcher)

    def id_handler(self, address, *value):
        local_id = value[0]
        if local_id != 0:
            print(local_id)

    def bool_handler(self, address, *value):
        if value[0] != -2:
            print(bool(value[0]))################################
            # if value[0] == 1:
            #     print("True")
            # else:
            #     print("False")

    def float_handler(self, address, *value):
        if value[0] != -2:
            print(value[0], type(value[0]), "\n")

    def avatar_change(self, address, *value):
        print(value[0])
        pause_flag.paused = True

    def run(self, asynchronous: bool = False):
        try:
            if asynchronous:
                threading.Thread(target=self._run, daemon=True).start()
            else:
                self._run()
        except KeyboardInterrupt:
            pass

    def _run(self):
        self.server.serve_forever()


class CSVHandling:
    def __init__(self):
        pass


def main():
    logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

    server_ip = "127.0.0.1"
    server_port = 9001
    client_ip = "127.0.0.1"
    client_port = 9000

    sender = VRChatSyncSender(
        client_ip,
        client_port
    )
    receiver = VRChatSyncReceiver(
        server_ip,
        server_port
    )

    #sender.run(asynchronous=True)
    receiver.run(asynchronous=True)

    #Hold
    try:
        while 1:
            time.sleep(1e6)
    except KeyboardInterrupt:
        print("end")


if __name__ == "__main__":
    main()
# add csv init
# add csv write(w/ data types)
# add csv read(casting to data types)
# add sender (send to bool/float/int depending on type)
