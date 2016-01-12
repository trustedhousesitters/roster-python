import socket
import os
import sys
import time
import errno
from urlparse import urlparse

import roster

MAX_RECONNECT_TRY = 10

def connect(client, service_name='echo'):
    service, err = client.Discover(service_name)
    if err:
        print >>sys.stderr, str(err)

    endpoint_data = urlparse(service.Endpoint)
    print >>sys.stdout, 'connecting to %s port %s' % (endpoint_data.hostname, endpoint_data.port)

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((endpoint_data.hostname, endpoint_data.port))
    return conn, endpoint_data

def main():
    client = roster.Client.new()

    conn = None
    endpoint_data = None
    message_count = 1
    reconnect_try = 0

    try:
        while True:
            try:
                if not conn:
                    print >>sys.stdout, 'Connecting... %d' % reconnect_try 
                    conn, endpoint_data = connect(client)
                    reconnect_try += 1
                    if reconnect_try == MAX_RECONNECT_TRY:
                        raise KeyboardInterrupt()

                # message = raw_input("Enter your message: ")
                message = 'My message %d' % message_count
                message_count+= 1
                
                # Send data
                print >>sys.stdout, 'sending "%s" to "%s:%d"' % (message, endpoint_data.hostname, endpoint_data.port)
                conn.sendall(message)

                # Look for the response
                amount_received = 0
                amount_expected = len(message)
                
                while amount_received < amount_expected:
                    data = conn.recv(1024)
                    amount_received += len(data)
                    if amount_received > 0:
                        print >>sys.stdout, 'received "%s"' % data

                    reconnect_try = 0
            except socket.error, e:
                # try to reconnect
                # print >>sys.stderr, 'Socket Error: "%s, %d"' % (str(e), e.errno)
                try: 
                    conn.close()
                except Exception:
                    pass
                finally:
                    conn = None

            except IOError, e:
                if e.errno == errno.EPIPE:
                    print >>sys.stderr, 'EPIPE IOError : "%s"' % str(e)
                else:
                    print >>sys.stderr, 'IOError : "%s"' % str(e)
            except Exception as e:
                print >>sys.stderr, 'Error: "%s"' % str(e)

            # sleep for a second
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        if conn:
            print >>sys.stdout, 'closing socket'
            conn.close()
        exit(1)

if __name__ == '__main__':
    main()
