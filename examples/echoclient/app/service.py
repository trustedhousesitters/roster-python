import socket
import os
import sys
import time
import errno
from urlparse import urlparse

import roster

def main():
    client = roster.Client.new()

    conn = None
    endpoint_data = None
    message_count = 1

    while True:
        try:
            service, err = client.Discover('echo')
            if err:
                print >>sys.stderr, str(err)

            endpoint_data = urlparse(service.Endpoint)
            print >>sys.stdout, 'connecting to %s port %s' % (endpoint_data.hostname, endpoint_data.port)

            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.settimeout(5)
            conn.connect((endpoint_data.hostname, endpoint_data.port))

            # message = raw_input("Enter your message: ")
            message = 'My message %d' % message_count
            message_count += 1
            
            # Send data
            print >>sys.stdout, 'sending "%s" to "%s:%d"' % (message, endpoint_data.hostname, endpoint_data.port)
            
            # conn.setblocking(0)
            # status = conn.sendall(message)
            # conn.setblocking(1)

            buffer = message
            while buffer:
                bytes = conn.send(buffer)
                buffer = buffer[bytes:]

            # Look for the response
            amount_received = 0
            amount_expected = len(message)
            
            data = ''
            while amount_received < amount_expected:
                data += conn.recv(1024)
                amount_received += len(data)
                if amount_received > 0:
                    print >>sys.stdout, 'received "%s"' % data

        except socket.error, e:
            print >>sys.stderr, 'Socket Error: "%s, %d"' % (str(e), e.errno)
        except IOError, e:
            if e.errno == errno.EPIPE:
                print >>sys.stderr, 'EPIPE IOError : "%s"' % str(e)
            else:
                print >>sys.stderr, 'IOError : "%s"' % str(e)
        except KeyboardInterrupt:
            print >>sys.stderr, 'Exiting...'
            if conn:
                print >>sys.stdout, 'closing connection'
                conn.close()
            exit(1)
        except Exception as e:
            print >>sys.stderr, 'Error: "%s"' % str(e)
        finally:
            if conn:
                print >>sys.stdout, 'closing connection'
                conn.close()

        time.sleep(3)

if __name__ == '__main__':
    main()
