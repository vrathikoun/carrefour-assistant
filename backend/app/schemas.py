from typing import List, Optional, Any
from pydantic import BaseModel

class ProductItem(BaseModel):
    title: str
    price: str
    desc: Optional[str] = None

class PageContext(BaseModel):
    url: str
    title: str
    page_type: str
    promos: Optional[List[str]] = None
    products: Optional[List[ProductItem]] = None
    product: Optional[ProductItem] = None
    bodyText: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    context: PageContext
    chat_history: Optional[List[Any]] = []

class ChatResponse(BaseModel):
    response: str
    actions: Optional[List[Any]] = None