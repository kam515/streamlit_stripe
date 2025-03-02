from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from data_ops import to_nested_dict

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
    title: str = Field(..., description="1-3 word title.")
    description: str = Field(..., description="Reasoning for this section.")
    criteria_for_success: str = Field(..., description="Success criteria.")
    justification: str = Field(..., description="Why it meets success criteria.")
    # visible_content_or_invisible_description: VisibilityEnum = Field(
    #     ..., description="Must be 'Visible Content' or 'Invisible Description'."
    # )
    # element: Optional[ElementEnum] = None
    # visible_content: Optional[str] = None

class OutlineLayer(BaseModel):
    layer_name: str = Field(..., description="1-3 word title for this outline layer.")
    outline_items: List[OutlineItem] = Field(...)

# The project class will only be applicable on the first call/big picture outline
# It will be converted to a dictionary saved to session_state
# All other calls will be in the format of OutlineLayer^
class Project(BaseModel):
    project_title: str
    outline_layers: OutlineLayer

def making_openai_call(client, model, system_message, prompt, response_format):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": (
                    prompt
                ),
            },
        ],
        response_format=response_format,
    ) 
    project_response = completion.choices[0].message.parsed

    nested_dict = to_nested_dict(project_response)

    return nested_dict

def making_openai_call_sublayer(client, model, system_message, prompt, response_format=OutlineLayer):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": (
                    prompt
                ),
            },
        ],
        response_format=response_format,
    ) 
    project_response = completion.choices[0].message.parsed

    nested_dict = to_nested_dict(project_response)

    return nested_dict