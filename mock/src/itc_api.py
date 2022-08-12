from datetime import datetime
from typing import Optional, Union, Literal
from uuid import UUID, uuid4
from enum import Enum

from fastapi import FastAPI, HTTPException, APIRouter, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer

from starlette.status import HTTP_201_CREATED
from mangum import Mangum
from pydantic import BaseModel, Field
import boto3

import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration


sentry_sdk.init(
    dsn="https://dccca35e6ec74a128b3db53c99875b81@o73119.ingest.sentry.io/6642858",
    integrations=[
        StarletteIntegration(),
        FastApiIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)
    
from . import common
from .common import env
from .models import (
    TransactionEvent, TransactionEventBase, ObjectEventBase, ObjectEvent, 
    AggregationEvent, AggregationEventBase, TransformationEvent, TransformationEventBase,
    BizStep
)
from .init_dynamodb import db



security = HTTPBearer()

app = FastAPI(root_path=env('ROOT_PATH', default='/v1'))

def EventRouter(prefix, tag):
    return APIRouter(prefix=prefix, tags=[tag], dependencies=[Depends(security)])

objectEvent = EventRouter("/objectEvents", "ObjectEvent")
transactionEvent = EventRouter("/transactionEvents", "TransactionEvent")
aggregationEvent = EventRouter("/aggregationEvents", "AggregationEvent")
transformationEvent = EventRouter("/transformationEvents", "TransformationEvent")

@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
    <html>
        <script>
            window.onload = function() {{
                const searchParams = new URLSearchParams(window.location.hash.slice(1));
                if (searchParams.get('id_token') != null) {{
                        document.getElementById("msg").innerHTML = 'Your access token: ' 
                        + '<br/>'
                        + searchParams.get('id_token')
                        + '<br/><br/>'
                        + 'Go to <a href="/v1/redoc">redoc</a> or <a href="/v1/docs">docs</a> for api documentation.';
                }}
            }}
        </script>
        <head> <title>Traceability API</title> </head>
        <body>
            <h3>Traceability API</h3>
            <p id="msg" style="word-wrap: break-word;">
                Unauthorized. Go to <a href='{env('LOGIN_URL', default='')}'>Login</a>
                page to obtain a token using your GitHub account.
            </p>
        </body>
    </html>
    """


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
    
    
@app.get("/events/", response_model=ListEventsQueryResponse, dependencies=[Depends(security)])
async def get_events(
            nextPageToken: Optional[str] = Query(None, example=''), 
            eventType: Optional[Literal[
                'ObjectEvent', 'TransactionEvent', 'TransformationEvent', 'AggregationEvent'
            ]] = None,
            businessStepCode: Optional[BizStep] = None, 
            referenceStandard: Optional[str] = Query(None, example=''),
            fromDateTime: Optional[datetime] = Query(None, example='2016-09-07T14:03:59.660Z'),
            toDateTime: Optional[datetime] = Query(None, example='2033-09-07T14:03:59.660Z'),
            rootItemID: Optional[str] = Query(None, example=''), 
            rootProductClassID: Optional[str] = Query(None, example=''),  
            geographicScope: Optional[str] = Query(None, example='6HR8GR9F+9C'), 
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
