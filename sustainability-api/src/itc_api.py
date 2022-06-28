from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from boto3.dynamodb import types as _
from fastapi import FastAPI, HTTPException, status
from mangum import Mangum
from pydantic import BaseModel
import boto3
import environ


env = environ.Env()
env.read_env('env-local')

aws_endpoint_url = env('AWS_ENDPOINT', default=None)

db = boto3.client('dynamodb', endpoint_url=aws_endpoint_url)

response = db.list_tables()

if 'ObjectEvent' not in response['TableNames']:
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
        TableName='ObjectEvent',
        BillingMode='PAY_PER_REQUEST',
        TableClass='STANDARD_INFREQUENT_ACCESS'
    )


app = FastAPI()

class ObjectEventItem(BaseModel):
    id: str
    name: str
    
class ObjectEventQuantityItem(BaseModel):
    productClass: str
    quantity: str
    uom: str
    
class ObjectEventBase(BaseModel):
    itemList: List[ObjectEventItem]
    quantityList: List[ObjectEventQuantityItem]
    eventTime: Optional[datetime]
    actionCode: Optional[str]
    dispositionCode: Optional[str]
    businessStepCode: Optional[str]
    readPointId: Optional[str]
    locationId: Optional[str]
    
class ObjectEvent(ObjectEventBase):
    eventID: UUID
    

@app.get("/")
async def root():
    return {"message": "go to /redoc or /docs for api documentation"}


@app.post("/objectEvents", status_code=status.HTTP_201_CREATED)
async def post_objectEvent(event: ObjectEventBase) -> ObjectEvent:
    event = ObjectEvent(eventID = uuid4(), **dict(event))
    data = event.json().replace('"', "'")
    response = db.execute_statement(
        Statement=f'INSERT INTO ObjectEvent VALUE {data}',
    )

    return event


ddbparser = boto3.dynamodb.types.TypeDeserializer()

def db_to_json(data):
    return {k: ddbparser.deserialize(value=data[k]) for k in data}


@app.get("/objectEvents/{eventID}")
async def get_objectEvent(eventID: UUID) -> ObjectEvent:
    response = db.execute_statement(
        Statement=f"SELECT * FROM ObjectEvent WHERE eventID='{eventID}'",
    )
    if response.get('Items'):
        return db_to_json(response['Items'][0])
    else:
        raise HTTPException(status_code=404, detail="Item not found")
 

@app.get("/objectEvents/")
async def get_objectEvents() -> List[ObjectEvent]:
    response = db.execute_statement(
        Statement=f"SELECT * FROM ObjectEvent",
    )
    return [db_to_json(x) for x in response.get('Items', [])]
 



handler = Mangum(app)  # AWS lambda hadler
