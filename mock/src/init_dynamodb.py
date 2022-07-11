import boto3

from .common import env


aws_endpoint_url = env('AWS_ENDPOINT', default=None)

db = boto3.client('dynamodb', verify=False, endpoint_url=aws_endpoint_url)

response = db.list_tables()

if 'Event' not in response['TableNames']:
    response = db.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'eventID',
                'AttributeType': 'S'
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'eventID',
                'KeyType': 'HASH'
            },
        ],
        TableName='Event',
        BillingMode='PAY_PER_REQUEST',
        TableClass='STANDARD_INFREQUENT_ACCESS'
    )

 
