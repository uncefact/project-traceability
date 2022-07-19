from datetime import datetime
from typing import Optional, Union, Literal
from uuid import UUID, uuid4
from enum import Enum

from fastapi import FastAPI, HTTPException, APIRouter, Query

from starlette.status import HTTP_201_CREATED
from mangum import Mangum
from pydantic import BaseModel, Field
import boto3

from . import common
from .common import env
from .models import (
    TransactionEvent, TransactionEventBase, ObjectEventBase, ObjectEvent, 
    AggregationEvent, AggregationEventBase, TransformationEvent, TransformationEventBase 
)
from .init_dynamodb import db

app = FastAPI()


objectEvent = APIRouter(prefix="/objectEvents", tags=["ObjectEvent"])
transactionEvent = APIRouter(prefix="/transactionEvents", tags=["TransactionEvent"])
aggregationEvent = APIRouter(prefix="/aggregationEvents", tags=["AggregationEvent"])
transformationEvent = APIRouter(prefix="/transformationEvents", tags=["TransformationEvent"])

@app.get("/")
async def root():
    return {"message": "go to /redoc or /docs for api documentation"}


@objectEvent.post("/", status_code=HTTP_201_CREATED, response_model=ObjectEvent)
async def post_objectEvent(event: ObjectEventBase):
    return store_event(event, ObjectEvent)
    
@transactionEvent.post("/", status_code=HTTP_201_CREATED, response_model=TransactionEvent)
async def post_transactionEvent(event: TransactionEventBase):
    return store_event(event, TransactionEvent)
    
@aggregationEvent.post("/", status_code=HTTP_201_CREATED, response_model=AggregationEvent)
async def post_aggregationEvent(event: AggregationEventBase):
    return store_event(event, AggregationEvent)
    
@transformationEvent.post("/", status_code=HTTP_201_CREATED, response_model=TransformationEvent)
async def post_transformationEvent(event: TransformationEventBase):
    return store_event(event, TransformationEvent)
    
def store_event(event, EventClass):
    event = EventClass(eventID = uuid4(), **dict(event))
    data = event.json().replace('"', "'")
    response = db.execute_statement(Statement=f'INSERT INTO Event VALUE {data}')
    return event


@objectEvent.get("/{eventID}", response_model=ObjectEvent)
async def get_objectEvent(eventID: UUID):
    return get_event(eventID)

@transactionEvent.get("/{eventID}", response_model=TransactionEvent)
async def get_transactionEvent(eventID: UUID):
    return get_event(eventID)

@aggregationEvent.get("/{eventID}", response_model=AggregationEvent)
async def get_aggregationEvent(eventID: UUID):
    return get_event(eventID)

@transformationEvent.get("/{eventID}", response_model=TransformationEvent)
async def get_transformationEvent(eventID: UUID):
    return get_event(eventID)


def get_event(eventID: UUID):
    response = db.execute_statement(
        Statement=f"SELECT * FROM Event WHERE eventID='{eventID}'",
    )
    if response.get('Items'):
        return common.db_to_json(response['Items'][0])
    else:
        raise HTTPException(status_code=404, detail="Item not found")
 

class ListEventsQueryResponse(BaseModel):
    items: list[Union[
        ObjectEvent, TransactionEvent, TransformationEvent, AggregationEvent
    ]]
    hasMorePages: bool
    nextPageToken: Optional[str]
    
    
@app.get("/events/", response_model=ListEventsQueryResponse)
async def get_events(
            nextPageToken: Optional[str] = Query(None, example=''), 
            eventType: Optional[Literal[
                'ObjectEvent', 'TransactionEvent', 'TransformationEvent', 'AggregationEvent'
            ]] = None,
            businessStepCode: Optional[str] = None, 
            referenceStandard: Optional[str] = None, 
            fromDateTime: Optional[datetime] = None, 
            toDateTime: Optional[datetime] = None, 
            rootItemID: Optional[str] = None, 
            rootProductClassID: Optional[str] = None, 
            geographicScope: Optional[str] = None, 
        ):
    query = "SELECT * FROM Event"
    if eventType:
       query += f" AND eventType='{eventType}'"
    if businessStepCode:
       query += f" AND businessStepCode='{businessStepCode}'"
    if referenceStandard:
       query += f" AND certification.referenceStandard='{referenceStandard}'"
    if rootItemID:
       query += (f" AND (itemList[0].id = '{rootItemID}' "
                         f"OR inputItemList[0].id = '{rootItemID}' "
                         f"OR parentItem.id = '{rootItemID}')")
    if fromDateTime:
       query += f" AND eventTime >= '{fromDateTime}'"
    if toDateTime:
       query += f" AND eventTime < '{toDateTime}'"
    if geographicScope:
       query += f" AND begins_with(\"locationId\", '{geographicScope}')"
       
    query = query.replace('AND', 'WHERE', 1)
    response = db.execute_statement(
        Statement=query,
        **{'NextToken': nextPageToken} if nextPageToken else {}
    )
    items = [common.db_to_json(x) for x in response.get('Items', [])]
    
    if 'LastEvaluatedKey' in response:
        return {'items': items, 'hasMorePages': True, 'nextPageToken': response['NextToken']}
    
    return {'items': items, 'hasMorePages': False}
 


app.include_router(objectEvent)
app.include_router(transactionEvent)
app.include_router(aggregationEvent)
app.include_router(transformationEvent)



handler = Mangum(app)  # AWS lambda hadler
