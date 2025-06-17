from typing import List, Optional, Any
from pydantic import BaseModel, Field


class MapItem(BaseModel):
    """Represents a map location point."""

    id: int
    type: str
    long: str
    lat: str

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class Activity(BaseModel):
    """Represents a single tracking activity/event."""

    id: str
    status: str
    status_code: str = Field(..., alias="statusCode")
    status_type_code: str = Field(..., alias="statusTypeCode")
    date: str
    country_code: str = Field(..., alias="countryCode")
    state: str
    city: str
    zip: str
    proof_of_delivery: str = Field(..., alias="proofOfDelivery")
    signatory: str
    timezone_offset: str = Field(..., alias="timezoneOffset")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class Banner(BaseModel):
    """Represents a banner image in the response."""

    widget_id: int = Field(..., alias="widgetId")
    alt: str
    filename: str
    id: int
    url: Optional[str] = None
    custom_label: str = Field(..., alias="customLabel")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class WismoData(BaseModel):
    """The main data object from the WismoLabs API response."""

    slug: str
    order_number: str = Field(..., alias="orderNumber")
    tracking_number: str = Field(..., alias="trackingNumber")
    map: List[MapItem]
    errors: List[Any]
    activities: List[Activity]
    banners: List[Banner]
    status: str
    eta: str
    eta_source: str = Field(..., alias="etaSource")
    eta_begin: str = Field(..., alias="etaBegin")
    eta_end: str = Field(..., alias="etaEnd")
    eta_display_median: str = Field(..., alias="etaDisplayMedian")
    delivered_time: Optional[str] = Field(None, alias="deliveredTime")
    last_status_date: str = Field(..., alias="lastStatusDate")
    service: str
    service_desc: str = Field(..., alias="serviceDesc")
    ship_date: str = Field(..., alias="shipDate")
    carrier_id: str = Field(..., alias="carrierId")
    carrier_name: str = Field(..., alias="carrierName")
    orig_city: str = Field(..., alias="origCity")
    orig_country: str = Field(..., alias="origCountry")
    orig_state: str = Field(..., alias="origState")
    dest_city: str = Field(..., alias="destCity")
    dest_country: str = Field(..., alias="destCountry")
    dest_state: str = Field(..., alias="destState")
    status_code: str = Field(..., alias="statusCode")
    status_type_code: str = Field(..., alias="statusTypeCode")
    status_desc: str = Field(..., alias="statusDesc")
    status_summary: str = Field(..., alias="statusSummary")
    carrier_eta: str = Field(..., alias="carrierEta")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class WismoApiResponse(BaseModel):
    """The root object for the WismoLabs API response."""

    data: WismoData

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
