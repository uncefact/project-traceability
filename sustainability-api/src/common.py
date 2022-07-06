import boto3
from boto3.dynamodb import types as _

ddbparser = boto3.dynamodb.types.TypeDeserializer()

def db_to_json(data):
    return {k: ddbparser.deserialize(value=data[k]) for k in data}
 
