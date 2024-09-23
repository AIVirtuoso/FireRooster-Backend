from pydantic import BaseModel
from typing import Optional

class SetProfileModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    prompt: str
    phone_number: str