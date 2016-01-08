import socket
import os
import sys
import urlparse

import roster

def main():
    # Check to see if running Dynamodb Locally or in AWS
    dle = os.getenv('DYNAMODB_LOCAL_ENDPOINT', '') 
    if dle != '':
        client = roster.NewClient(roster.LocalConfig(endpoint=dle))
    else:
        client = roster.NewClient(roster.WebServiceConfig())

    service, err = client.Discover('echo')
    if err:
        print >>sys.stderr, str(err)
        exit(1)

    endpoint_data = urlparse(service)

    # Create a TCP/IP socket
    endpoint = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    print >>sys.stdiyt, 'connecting to %s port %s' % server_address
    endpoint.connect((endpoint_data.hostname, endpoint_data.port))

    while True:
        message = raw_input("Enter your message: ")

        try:
            # Send data
            print >>sys.stdout, 'sending "%s"' % message
            endpoint.sendall(message)

            # Look for the response
            amount_received = 0
            amount_expected = len(message)
            
            while amount_received < amount_expected:
                data = endpoint.recv(16)
                amount_received += len(data)
                print >>sys.stdout, 'received "%s"' % data

        finally:
            print >>sys.stdout, 'closing socket'
            endpoint.close()

if __name__ == '__main__':
    main()
