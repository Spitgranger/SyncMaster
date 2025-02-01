from pydantic import BaseModel, Field

class LocationVerificationRequest(BaseModel):
    latitude: float = Field(..., description="Latitude of the current location.")
    longitude: float = Field(..., description="Longitude of the current location.")
    accuracy: float = Field(0, description="Accuracy of the location in meters.")
