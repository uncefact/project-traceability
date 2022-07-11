from datetime import datetime
from typing import Optional, Union, Literal
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel


class Party(BaseModel):
    partyID: str
    name: str
    
    
class EventItem(BaseModel):
    id: str
    name: str
    
class QuantityListItem(BaseModel):
    productClass: str
    quantity: str
    uom: str
    
    
class Certification(BaseModel):
    certificateID: str
    referenceStandard: str
    evidenceURL: Optional[str]
    criteriaList: Optional[list[str]]
    assessmentLevel: Optional[str]
    responsibleAgency: Optional[Party]
    
class BaseEvent(BaseModel):
    eventTime: Optional[datetime]
    actionCode: Optional[str]
    dispositionCode: Optional[str]
    businessStepCode: Optional[str]
    readPointId: Optional[str]
    locationId: Optional[str]
    certification: Optional[Certification]
    
class TransformationEventBase(BaseEvent):
    eventType: Literal['TransformationEvent']
    
    inputItemList: list[EventItem]
    inputQuantityList: list[QuantityListItem]
    outputItemList: list[EventItem]
    outputQuantityList: list[QuantityListItem]
    
class TransformationEvent(TransformationEventBase):
    eventID: UUID
    
class AggregationEventBase(BaseEvent):
    eventType: Literal['AggregationEvent']
    parentItem: EventItem
    childItems: list[EventItem]
    childQuantityList: list[QuantityListItem]
    
    
class AggregationEvent(AggregationEventBase):
    eventID: UUID
    
class TransactionEventBase(BaseEvent):
    eventType: Literal['TransactionEvent']
    sourceParty: Optional[Party]
    destinationParty: Optional[Party]
    itemList: list[EventItem]
    quantityList: list[QuantityListItem]
    
class TransactionEvent(TransactionEventBase):
    eventID: UUID
    
    
class ObjectEventBase(BaseEvent):
    eventType: Literal['ObjectEvent']
    itemList: list[EventItem]
    quantityList: list[QuantityListItem]
    
class ObjectEvent(ObjectEventBase):
    eventID: UUID
     
