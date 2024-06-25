from pydantic import BaseModel
from typing import Optional

class FilterModel(BaseModel):
    scanner_id: Optional[int] = None
    page: Optional[int] = 1
    limit: Optional[int] = 10