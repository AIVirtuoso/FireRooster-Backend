from pydantic import BaseModel
from typing import Optional
from datetime import datetime  

class FilterModel(BaseModel):
    limit: Optional[int] = 10
    page: Optional[int] = 1
    search: Optional[str] = ""
    scanner_id: Optional[int] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    selected_from: Optional[datetime] = None  
    selected_to: Optional[datetime] = None  

class SelectedCategoryModel(BaseModel):
    is_selected: Optional[bool]
    sub_category: Optional[str]
    category: Optional[str]
    id: Optional[int]

class IdFilterModel(BaseModel):
    alert_id: Optional[int]
    scanner_id: Optional[int]

class CategoryFilterModel(BaseModel):
    category: Optional[str]
    search: Optional[str] = ""
    
class UnlockContactInfoModel(BaseModel):
    address_id: int