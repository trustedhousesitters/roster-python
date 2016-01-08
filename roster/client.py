import time
import sys
import os
import signal
import random
import threading
from urlparse import urlparse
from datetime import datetime, timedelta
from registry import NewRegistry

from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.items import Item
from boto.dynamodb2.exceptions import ItemNotFound

HEARTBEAT_INTERVAL = 1 # 1second
TTL = 5

class Service(object):

    def __init__(self, Name, Endpoint, Expiry=None, stopHeartbeat=False, *args, **kwargs):
        self.Name = Name.get('S') if isinstance(Name, dict) else Name
        self.Endpoint = Endpoint.get('S') if isinstance(Endpoint, dict) else Endpoint
        self.Expiry = int(Expiry.get('N')) if isinstance(Expiry, dict) else Expiry # unix timestamp
        self.stopHeartbeat = int(stopHeartbeat.get('N')) if isinstance(stopHeartbeat, dict) else stopHeartbeat

    # Unregister the service
    def Unregister(self):
        self.stopHeartbeat = True

class BaseConfig(object):

    def __init__(self, registry_name='', *args, **kwargs):
        self.registry_name = registry_name
        self.region = ''

    def GetRegistryName(self):
        """
        Get registry table name
        """
        return self.registry_name or 'roster'

    def GetHashKey(self):
        return self.name

    def GetRangeKey(self):
        return self.endpoint
        
    def GetConnection(self):
        raise NotImplementedError("Subclasses shouls implement this!")

class WebServiceConfig(BaseConfig):
    from boto.dynamodb2.layer1 import DynamoDBConnection

    def SetRegion(self, region):
        self.region = region

    def GetConnection(self):
        # Environment var
        if self.region == '':
            self.region = os.getenv('AWS_REGION', '') 

        # Default
        if self.region == '':
            self.region = "us-west-2"

        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', '')
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', '') 

        return connect_to_region(self.region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

class LocalConfig(BaseConfig):

    def __init__(self, endpoint, *args, **kwargs):
        super(LocalConfig, self).__init__(*args, **kwargs)
        self.endpoint = endpoint

    def GetConnection(self):
        endpoint_data = urlparse(self.endpoint)

        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'foo')
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'bar')

        return DynamoDBConnection(
            host=endpoint_data.hostname,
            port=endpoint_data.port, 
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            is_secure=False
        )

class CleanExit(object):
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is KeyboardInterrupt:
            return True
        return exc_type is None

class Client(object):
    def __init__(self, svc, config, registry):
        self.svc = svc
        self.config = config
        self.registry = registry

    # Register the service in the registry
    def Register(self, name, endpoint):
        # Check whether the registry has been previously created. If not create before registration.
        if not self.registry.Exists():
            table, err = self.registry.Create()
            if err:
                return None, err

        # Create Service
        self.service = Service(Name=name, Endpoint=endpoint)

        # Ensure call heartbeat at least once
        self.heartbeat()

        # Start heartbeat check
        t = threading.Thread(target=heartbeat_check, args=(self,))
        t.daemon = True # causes the thread to terminate when the main process ends.
        t.start()

        return self.service, None

    # Heartbeat function - updates expiry
    def heartbeat(self):
        if self.service.stopHeartbeat:
            return

        # Update service Expiry based on TTL and current time
        self.service.Expiry = int(time.mktime(datetime.now().timetuple())) + TTL

        table = self.registry.Table()

        item_info = {
            'Name': self.service.Name,
            'Endpoint': self.service.Endpoint
        }
        if table.has_item(**item_info):
            item = table.get_item(**item_info)
        else:
            item = Item(table, self.service.__dict__)

        item['Expiry'] = self.service.Expiry
        item.save()

    # Query the registry for named service
    def Discover(self, name):
        now = int(time.mktime(datetime.now().timetuple()))
        items = self.svc.scan(
            self.registry.name,
            filter_expression = 'Expiry > :ExpiryVal AND #N = :NameVal',
            expression_attribute_names = {
                '#N': 'Name'
            },
            expression_attribute_values = {
                ':NameVal': {
                    'S': name
                },
                ':ExpiryVal': {
                    'N': str(now)
                }
            }
        )

        # Randomly select one of the available endpoints (in effect load balancing between available endpoints)
        count = items.get('Count')
        if count == 0:
            return None, Exception('roster: No matching service found')
        else:
            return Service(**items['Items'][random.randint(0, count - 1)]), None

    # Returns the non loopback local IP of the host the client is running on
    def GetLocalIP(self):
        import socket
        try:
            for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
                if not ip.startswith("127."):
                    return ip, ''

        except Exception:
            pass

        return '', Exception("roster: No non loopback local IP address could be found")

# Heartbeat function - updates expiry
def heartbeat_check(client):
    # with CleanExit():
    while True:
        if client.service.stopHeartbeat:
            break

        time.sleep(HEARTBEAT_INTERVAL)
        client.heartbeat()

def NewClient(config):
    svc =  config.GetConnection()
    registry = NewRegistry(svc, config.GetRegistryName())

    return Client(svc=svc, config=config, registry=registry)
