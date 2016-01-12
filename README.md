# Roster: A library for simple service discovery using Dynamodb for Python

Instead of having to manage a separate distributed key store like etcd or ZooKeeper, leverage AWS's own Dynamodb so you don't have to worry about hardware provisioning, setup and configuration, replication, software patching, or cluster scaling.


## Contributing

### Installation

1. Clone the repository

### Running tests

> todo

### Examples

**Server**
    docker run -it -p=3333:3333 -e "DYNAMODB_ENDPOINT=tcp://192.168.99.100:32768" roster-python/example-echo-server
    
    AWS_ACCESS_KEY_ID=`grep aws_access_key_id ~/.boto | awk '{print $3}'`; AWS_SECRET_ACCESS_KEY=`grep aws_secret_access_key ~/.boto | awk '{print $3}'`; docker run -it -p=3333:3333 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY roster-python/example-echo-server

**Client**
    docker run -it -e "DYNAMODB_ENDPOINT=tcp://192.168.99.100:32768" roster-python/example-echo-client

    AWS_ACCESS_KEY_ID=`grep aws_access_key_id ~/.boto | awk '{print $3}'`; AWS_SECRET_ACCESS_KEY=`grep aws_secret_access_key ~/.boto | awk '{print $3}'`; docker run -it -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY roster-python/example-echo-client

> Set the `DYNAMODB_ENDPOINT` to your local dynamodb 
