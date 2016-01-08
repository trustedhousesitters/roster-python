import os
import socket
import sys

import roster

CONN_PORT = 3333

def main():
    # Check to see if running Dynamodb Locally or in AWS
    dle = os.getenv('DYNAMODB_LOCAL_ENDPOINT', '') 
    if dle != '':
        client = roster.NewClient(roster.LocalConfig(endpoint=dle))
    else:
        client = roster.NewClient(roster.WebServiceConfig())

    CONN_HOST, err = client.GetLocalIP()
    if err is None:
        print >>sys.stderr, err
        exit(1)

    endpoint = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    endpoint.bind((CONN_HOST, CONN_PORT))
    endpoint_str = 'tcp://{0}:{1}'.format(CONN_HOST, CONN_PORT)

    service, err = client.Register('roster', endpoint_str)
    if err:
        print >>sys.stderr, str(err)
        exit(1)

    # Listen for incoming connections
    endpoint.listen(1)

    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = endpoint.accept()

        try:
            print >>sys.stderr, 'connection from', client_address

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
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

if __name__ == '__main__':
    main()
