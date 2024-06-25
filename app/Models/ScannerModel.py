from pydantic import BaseModel
from typing import Optional, List

class FilterModel(BaseModel):
    state_id: Optional[int] = None
    county_id: Optional[int] = None
    page: Optional[int] = 1
    limit: Optional[int] = 10
    
class PurchaseScannerModel(BaseModel):
    scanner_id_list: List[int]