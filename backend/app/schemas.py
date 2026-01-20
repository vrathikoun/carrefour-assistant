from typing import List, Optional, Any, TypedDict, Annotated
from pydantic import BaseModel
import operator
import json

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
    message: Optional[str] = None
    context: PageContext
    chat_history: Optional[List[Any]] = []

class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = None
    actions: Optional[List[Any]] = None

class SuggestionsRequest(BaseModel):
    context: PageContext

class SuggestionsResponse(BaseModel):
    suggestions: List[str]