from pydantic import BaseModel, EmailStr
from typing import List, Optional

class EmailSchema(BaseModel):
    recipients: List[EmailStr]
    subject: str
    template_name: Optional[str] = None
    template_data: Optional[dict] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    attachment_paths: Optional[List[str]] = None