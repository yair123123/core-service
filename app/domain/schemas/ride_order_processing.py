from pydantic import BaseModel, ConfigDict, Field


class ProcessCallOrderRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    call_session_id: str = Field(alias="callSessionId")
    from_phone: str = Field(alias="fromPhone")
    origin_recording_url: str = Field(alias="originRecordingUrl")
    destination_recording_url: str = Field(alias="destinationRecordingUrl")
    notes_recording_url: str = Field(alias="notesRecordingUrl")


class ProcessCallOrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool
    ride_id: int | None = Field(default=None, alias="rideId")
    summary_text: str = Field(alias="summaryText")
    can_confirm: bool = Field(alias="canConfirm")
