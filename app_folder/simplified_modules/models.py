from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class VisibilityEnum(str, Enum):
    VISIBLE_CONTENT = "Visible Content"
    INVISIBLE_DESCRIPTION = "Invisible Description"

class ElementEnum(str, Enum):
    REGULAR_TEXT = "Regular text"
    IMAGE = "Image"
    NUMBERED_LIST = "Numbered list"
    BULLETED_LIST = "Bulleted List"
    HEADING_1 = "Heading 1"
    HEADING_2 = "Heading 2"
    HEADING_3 = "Heading 3"
    NONE = "None"

class OutlineItem(BaseModel):
    title: str = Field(..., description="1-3 word title for this section.")
    description: str = Field(..., description="Reason for this section.")
    criteria_for_success: str = Field(..., description="Success criteria.")
    justification: str = Field(..., description="Why it meets success criteria.")
    visible_content_or_invisible_description: VisibilityEnum = Field(
        ..., description="Must be 'Visible Content' or 'Invisible Description'."
    )
    element: Optional[ElementEnum] = None
    visible_content: Optional[str] = None

class OutlineLayer(BaseModel):
    layer_name: str = Field(..., description="1-3 word title for this outline layer.")
    outline_items: List[OutlineItem] = Field(...)

class Project(BaseModel):
    project_title: str
    outline_layers: List[OutlineLayer]
