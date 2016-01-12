import os
import sys
import time
import socket
import signal
import threading
from datetime import datetime, timedelta

import roster

CONN_PORT = 3333

def client_thread(connection, client_address):
    try:
        print >>sys.stderr, 'connection from', client_address

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024)
            print >>sys.stderr, 'received "%s"' % data
            if data:
                print >>sys.stderr, 'sending data back to the client'
                connection.sendall(data)
            else:
                print >>sys.stderr, 'no more data from', client_address
                break

    finally:
        # Clean up the connection
        connection.close()

def main():
    client = roster.Client.new()

    CONN_HOST, err = client.get_local_ip()
    if err is None:
        print >>sys.stderr, err
        return None

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.bind((CONN_HOST, CONN_PORT))

    endpoint_repr = 'tcp://{0}:{1}'.format(CONN_HOST, CONN_PORT)

    service, err = client.Register('echo', endpoint_repr)
    if err:
        print >>sys.stderr, str(err)
        exit(1)

    # Listen for incoming connections
    conn.listen(10)
    connections = []

    try:
        while True:
            connection, client_address = conn.accept()
            connections.append(connection)
            t = threading.Thread(target=client_thread, args=(connection, client_address,))
            t.daemon = True # causes the thread to terminate when the main process ends.
            t.start()
    except KeyboardInterrupt:
        service.Unregister()
        time.sleep(5)
    except Exception as e:
        print >>sys.stderr, 'Error: "%s"' % str(e)
    finally:
        for connection in connections:
            connection.close()

def signal_handler(signal, frame):
    time.sleep(5)
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
