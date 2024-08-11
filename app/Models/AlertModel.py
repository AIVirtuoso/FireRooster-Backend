from pydantic import BaseModel
from typing import Optional

class FilterModel(BaseModel):
    scanner_id: Optional[int] = None
    sub_category: Optional[str] = None
    page: Optional[int] = 1
    limit: Optional[int] = 10

class IdFilterModel(BaseModel):
    alert_id: Optional[int]
    scanner_id: Optional[int]

class CategoryFilterModel(BaseModel):
    category: Optional[str]