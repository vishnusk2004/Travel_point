from pydantic import BaseModel
from typing import List, Optional

class ArticleSection(BaseModel):
    type: str  # 'heading', 'paragraph', 'subheading', 'quote', etc.
    content: str
    level: Optional[int] = None  # For headings (h1, h2, etc.)

class ArticleContent(BaseModel):
    title: str
    sections: List[ArticleSection]
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None 