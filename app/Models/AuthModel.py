from pydantic import BaseModel
from typing import Optional

class SignUpModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    password2: str
    forgot_password_token: Optional[str] = ""
    
class SignInModel(BaseModel):
    email: str
    password: str
    
