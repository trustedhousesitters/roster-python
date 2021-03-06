import time
from boto.dynamodb2.fields import HashKey, RangeKey, GlobalAllIndex
from boto.dynamodb2 import table as dynamodb_table

class Registry(object):

    def __init__(self, svc, name):
        self.svc = svc
        self.name = name

    # Does the registry exist
    def Exists(self):
        try:
            self.svc.describe_table(self.name)
            return True
        except Exception:
            pass

        return False

    def get_table_info(self):
        return {
            'table_name': self.name, 
            'schema': [
                HashKey('Name'),
                RangeKey('Endpoint'),
            ], 
            'throughput': {
                'read': 1,
                'write': 1,
            },
            'global_indexes': [
                GlobalAllIndex('EverythingIndex', parts=[
                    HashKey('Name'),
                    RangeKey('Endpoint')
                ])
            ],
            'connection': self.svc
        }

    # Create table with 2 attributes (Name and Expiry)
    def Table(self):
        return dynamodb_table.Table(**self.get_table_info())

    def IsActive(self):
        try:
            desc = self.svc.describe_table(self.name)
            status = desc.get('Table', {}).get('TableStatus')
            return status == 'ACTIVE', None
        except Exception as e:
            return False, str(e)

        return False, Exception('roster: Unknown error while creating the table')

    # Create table with 2 attributes (Name and Expiry)
    def Create(self):
        try:
            table = dynamodb_table.Table.create(**self.get_table_info())

            # Table was created, but it's asynchronous...so block whilst it finishes being created
            err = None
            for _ in xrange(5):
                active, err = self.IsActive()
                if active:
                    return table, None

                time.sleep(1)

            return None, err or Exception('roster: Registry table has taken longer than expected to reach ACTIVE state')

        except Exception as e:
            return None, e

    # Delete the registry
    def Delete(self):
        self.GetTable().delete()

def NewRegistry(svc, name):
    return Registry(svc, name)
