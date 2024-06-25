from pydantic import BaseModel
from typing import Optional

class StripeModel(BaseModel):
    email: Optional[str] = ""
    plan_id: Optional[str] = ""