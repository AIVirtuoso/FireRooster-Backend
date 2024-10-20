from pydantic import BaseModel
from typing import Optional, List, Dict

class FilterModel(BaseModel):
    search: Optional[str] = ""
    state_id: Optional[List[int]] = None
    county_id: Optional[List[int]] = None
    page: Optional[int] = 1
    limit: Optional[int] = 10
    

class PurchaseScannerModel(BaseModel):
    scanner_id_list: List[int]
    
class DeleteScannerModel(BaseModel):
    scanner_id: int

class ToggleScraperModel(BaseModel):
    scraper_status: int

