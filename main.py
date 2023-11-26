import csv
import threading
from pythonosc.dispatcher import Dispatcher
import sys
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import time

local_id = 0
local_value = 0
remote_id = 0
remote_value = 0
stored_values = [-2.1] * 256


def sync_to_remote(ip, port):
    ip = "127.0.0.1"
    port = 9000
    client = SimpleUDPClient("127.0.0.1", 9000)
    global stored_values, remote_id, remote_value

    stored_values = read_values(stored_values)
    for x in range(len(stored_values)):
        if x == 0 or stored_values[x] == -2.1:
            pass
        else:
            client.send_message("/avatar/parameters/remote_id", x)
            client.send_message("/avatar/parameters/remote_value", bool(stored_values[x]))
            print("Sent ->", bool(stored_values[x]), "to ID:", x)
            time.sleep(.1)


def id_handler(address: str, *args: float) -> None:
    global local_id
    local_id = args[0]


def value_handler(address: str, *args: float) -> None:
    global local_value
    local_value = args[0]
    update_list(local_id, local_value)
    write_values(stored_values)


def write_values(values):
    with open("saved_params.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for x, value in enumerate(values):
            writer.writerow([x, value])


def read_values(values):
    values = []
    with open("saved_params.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            values.append(float(row[1]))
    return values


def update_list(id, value):
    global stored_values
    if id == 0 or value == 0.5:
        print("none")
        pass
    else:
        stored_values[id] = value
        print(stored_values)


def main():
    # from vrchat
    server_ip = "127.0.0.1"
    server_port = 9001
    # to vrchat
    client_ip = "127.0.0.1"
    client_port = 9000

    read_values(stored_values)

    dispatcher = Dispatcher()
    dispatcher.map("/avatar/parameters/local_id", id_handler)
    dispatcher.map("/avatar/parameters/local_value", value_handler)

    server = ThreadingOSCUDPServer((server_ip, server_port), dispatcher)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"\033[0mListening on \033[37;49;1m{server_ip}:{server_port}\033[0m...")

    active = True

    print(f"\033[0mSending on \033[37;49;1m{client_ip}:{client_port}\033[0m...")
    print("waiting for parameter change...")
    while active:
        sync_to_remote(client_ip, client_port)
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)


