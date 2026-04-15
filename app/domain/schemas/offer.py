from pydantic import ConfigDict, BaseModel


class Offer(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        customer_id: int
        dispatcher_id: int
        station_id: int
        status: RideStatus
        created_at: datetime