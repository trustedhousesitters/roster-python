import socket
import os
import sys
from urlparse import urlparse

import roster

def connect(client, service_name='echo'):
    service, err = client.Discover(service_name)
    if err:
        print >>sys.stderr, str(err)
        exit(1)

    endpoint_data = urlparse(service.Endpoint)
    print >>sys.stdout, 'connecting to %s port %s' % (endpoint_data.hostname, endpoint_data.port)

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.bind((endpoint_data.hostname, endpoint_data.port))
    return conn

def main():
    client = roster.Client.new()

    while True:
        try:
            message = raw_input("Enter your message: ")
            conn = connect(client)

            # Send data
            print >>sys.stdout, 'sending "%s"' % message
            conn.sendall(message)

            # Look for the response
            amount_received = 0
            amount_expected = len(message)
            
            while amount_received < amount_expected:
                data = conn.recv(1024)
                amount_received += len(data)
                print >>sys.stdout, 'received "%s"' % data
                 
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print >>sys.stderr, 'Error: "%s"' % str(e)
        finally:
            print >>sys.stdout, 'closing socket'
            conn.close()

if __name__ == '__main__':
    main()
