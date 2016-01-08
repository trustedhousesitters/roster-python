import sys
import time
import unittest
import roster
from boto.dynamodb2 import table as dynamodb_table

CONN_PORT = 3337

class TestClient(unittest.TestCase):

    def setUp(self):
        self.service_endpoint = 'tcp://192.168.99.100:32768'
        self.service_name = 'roster_client_test'
        self.client = roster.NewClient(roster.LocalConfig(endpoint=self.service_endpoint, 
                                                          registry_name=self.service_name))

    def test_register(self):

        CONN_HOST, err = self.client.GetLocalIP()
        if err is None:
            print >>sys.stderr, err
            exit(1)

        endpoint_str = 'tcp://{0}:{1}'.format(CONN_HOST, CONN_PORT)

        service, err = self.client.Register('test-service', endpoint_str)
        if err:
            print >>sys.stderr, str(err)
            exit(1)

        service.Unregister()

    def test_discovery(self):

        CONN_HOST, err = self.client.GetLocalIP()
        if err is None:
            print >>sys.stderr, err
            exit(1)

        endpoint_str = 'tcp://{0}:{1}'.format(CONN_HOST, CONN_PORT)

        service, err = self.client.Register('test-service', endpoint_str)
        if err:
            print >>sys.stderr, str(err)
            exit(1)
        self.assertIsNone(err)

        service, err = self.client.Discover('test-service')
        self.assertIsNone(err)
        self.assertEqual(service.Endpoint, endpoint_str)

        service.Unregister()

    def test_unregister(self):

        CONN_PORT = 3337
        CONN_HOST, err = self.client.GetLocalIP()
        if err is None:
            print >>sys.stderr, err
            exit(1)

        endpoint_str = 'tcp://{0}:{1}'.format(CONN_HOST, CONN_PORT)

        service, err = self.client.Register('test-service', endpoint_str)
        self.assertIsNone(err)

        service.Unregister()

        # TTL set to 5 seconds, so wait 6 seconds to see if expired
        time.sleep(6)

        service, err = self.client.Discover('test-service-non-existing')
        self.assertIsNone(service)
