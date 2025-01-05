import streamlit as st
from typing import List
import os
import json
import openai
import requests
from PIL import Image
from io import BytesIO
from pydantic import BaseModel
from openai import OpenAI
from typing import List
import os
import json
import openai
import requests
from PIL import Image
from io import BytesIO
from pydantic import BaseModel
from openai import OpenAI
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

MODEL = "gpt-4o-2024-08-06"
api_key = st.secrets["openai_api_info"]["openai_key"]
client = OpenAI(api_key=api_key)

# Set page configuration.
st.set_page_config(page_title="Sample App", layout="wide")
import streamlit as st
import copy  # Added to support save_state() function
import pandas as pd  # Needed for DataFrame operations

MODEL = "gpt-4o-2024-08-06"
# api_key = "secret_api_key"
client = OpenAI(api_key=api_key)

# Enums for allowed values
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
        ...,
        description="Must be 'Visible Content' or 'Invisible Description'."
    )
    element: Optional[ElementEnum] = None
    visible_content: Optional[str] = None

class OutlineLayer(BaseModel):
    # NOTE: The code references layer_name in some spots, 
    #       but the OutlineLayer model doesn't have it.
    #       We can add it or remove references to it. 
    #       We'll add it here to match usage below.
    layer_name: str = Field(..., description="1-3 word title for this outline layer.")
    # layer_name: str = Field("Layer Name")
    outline_items: List[OutlineItem] = Field(...)

class Project(BaseModel):
    project_title: str
    outline_layers: List[OutlineLayer]

def to_nested_dict(obj):
    """
    Convert Pydantic models, lists, and dicts 
    into fully nested Python dictionaries.
    """
    if isinstance(obj, BaseModel):
        data = obj.model_dump()
        return {k: to_nested_dict(v) for k, v in data.items()}
    elif isinstance(obj, list):
        return [to_nested_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: to_nested_dict(v) for k, v in obj.items()}
    else:
        return obj

def to_json(obj):
    """
    Return JSON string from nested dict form.
    """
    return json.dumps(to_nested_dict(obj), indent=2)

# Initialize session states safely
if "project_dict" not in st.session_state:
    st.session_state["project_dict"] = None
if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False
if "generated_once" not in st.session_state:
    st.session_state["generated_once"] = False

#--- FORM SECTION ---
with st.form("my_form"):
    prompty = st.text_input("What is the goal of your project?")
    submit_col = st.columns([11, 2])[1]
    with submit_col:
        prompty_submit = st.form_submit_button('Start my outline!')
        # If form_submit_button is clicked, set session_state
        if prompty_submit:
            st.session_state["form_submitted"] = True

system_message = "You are an expert strategic planner who creates first big picture, and then increasingly detailed outlines that comprehensively accomplish the stated goal."

if st.session_state["form_submitted"] and not st.session_state["generated_once"]:
    # Attempt the OpenAI call once
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Make a big picture outline of the following goal with 2-5 items that ensure the goal is accomplished from start to finish: {prompty}"},
        ],
        response_format=Project,
    )
    # Store parsed object
    project_response = completion.choices[0].message.parsed

    nested_dict = to_nested_dict(project_response)
    st.session_state["project_dict"] = nested_dict
    st.session_state["generated_once"] = True

#--- Once we have a project_dict, build the data for the first layer ---
if st.session_state["project_dict"] is not None:
    outline_layer = st.session_state["project_dict"]["outline_layers"][0]
    outline_items = outline_layer["outline_items"]
    layer_name = outline_layer["layer_name"]  # from the updated OutlineLayer model
    data = pd.DataFrame(outline_items)

    if "data" not in st.session_state:
        st.session_state["data"] = data.copy()
    if "order" not in st.session_state:
        st.session_state["order"] = list(range(len(data)))
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "redo_stack" not in st.session_state:
        st.session_state["redo_stack"] = []
    if "editing_row" not in st.session_state:
        st.session_state["editing_row"] = None

    def save_state():
        state = {
            "data": st.session_state["data"].copy(),
            "order": copy.deepcopy(st.session_state["order"]),
        }
        st.session_state["history"].append(state)
        st.session_state["redo_stack"].clear()

    def move_row(index, direction):
        save_state()
        order = st.session_state["order"]
        if direction == "up" and index > 0:
            order[index], order[index - 1] = order[index - 1], order[index]
        elif direction == "down" and index < len(order) - 1:
            order[index], order[index + 1] = order[index + 1], order[index]
        st.session_state["order"] = order

    def delete_row(index):
        save_state()
        order = st.session_state["order"]
        data_local = st.session_state["data"]
        row_to_remove = order.pop(index)
        data_local = data_local.drop(row_to_remove).reset_index(drop=True)
        # Rebuild order to match new indexes
        st.session_state["order"] = list(range(len(data_local)))
        st.session_state["data"] = data_local

    def edit_row(index):
        st.session_state["editing_row"] = index

    def save_edit(index, new_desc):
        save_state()
        # Reorder, edit, then update original
        ordered_data = st.session_state["data"].iloc[st.session_state["order"]].reset_index(drop=True)
        ordered_data.loc[index, "description"] = new_desc
        # Now map it back to st.session_state["data"] respecting old indexes
        # Easier path: write changes back in correct row ID
        global_index = st.session_state["order"][index]
        st.session_state["data"].loc[global_index, "description"] = new_desc
        st.session_state["editing_row"] = None

    def undo():
        if st.session_state["history"]:
            prev_state = st.session_state["history"].pop()
            # Save current for potential redo
            st.session_state["redo_stack"].append(
                {
                    "data": st.session_state["data"].copy(),
                    "order": st.session_state["order"][:]
                }
            )
            st.session_state["data"] = prev_state["data"]
            st.session_state["order"] = prev_state["order"]

    def redo():
        if st.session_state["redo_stack"]:
            next_state = st.session_state["redo_stack"].pop()
            # Push current onto history
            st.session_state["history"].append(
                {
                    "data": st.session_state["data"].copy(),
                    "order": st.session_state["order"][:]
                }
            )
            st.session_state["data"] = next_state["data"]
            st.session_state["order"] = next_state["order"]

    def add_row(position, new_desc=""):
        save_state()
        data_local = st.session_state["data"]
        order_local = st.session_state["order"]
        if data_local.empty:
            new_id = 0
        else:
            new_id = data_local.index.max() + 1
        new_row = pd.DataFrame({"description": [new_desc]}, index=[new_id])
        st.session_state["data"] = pd.concat([data_local, new_row])
        # Insert new index into the display order
        order_local.insert(position + 1, new_id)
        st.session_state["order"] = order_local

    ordered_data = st.session_state["data"].iloc[st.session_state["order"]].reset_index(drop=True)

    top_row = st.columns([0.5, 0.5, 7, 2])
    with top_row[0]:
        if st.button("⟲", help="Undo", disabled=len(st.session_state["history"]) == 0):
            undo()
    with top_row[1]:
        if st.button("↻", help="Redo", disabled=len(st.session_state["redo_stack"]) == 0):
            redo()

    #--- BIGGER PICTURE BUTTON ---
    # PSEUDOCODE for shifting layers:
    # """
    # if st.button("<  Bigger Picture"):
    #     # Step 1: Identify current layer index in session_state if tracking multiple layers
    #     # Step 2: If not at top layer, decrement layer index
    #     #         st.session_state["current_layer_index"] = max(0, st.session_state["current_layer_index"] - 1)
    #     # Step 3: Rerender or update data from the higher-level layer 
    #     #         st.session_state["data"] = ...
    #     # (Future expansion to handle multiple layers)
    # """
    if st.button("<  Bigger Picture"):
        st.info("Will move to a higher outline layer in future version.")

    st.markdown(f"<h2 style='text-align:center;'>{layer_name}</h2>", unsafe_allow_html=True)
    st.write("---")

    def inject_css():
        st.markdown(
            """
            <style>
            /* General Body Styling */
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
                color: #333;
                margin: 0;
                padding: 0;
            }

            /* Full-Width Content */
            .main {
                width: 100% !important; /* Force full width */
                padding: 0 !important; /* Remove additional paddings */
            }

            /* Headers */
            h1, h2, h3 {
                font-weight: 700;
                color: #222;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
                text-align: center;
            }

            /* Sidebar */
            [data-testid="stSidebar"] {
                background: #343a40;
                color: #f8f9fa;
                border-right: 2px solid #495057;
            }

            /* Buttons */
            button {
                display: block; /* Ensure it's treated as a block element */
                margin: 20px auto; /* Center horizontally */
                background-color: #0d6efd;
                color: #fff;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }

            /* Table Styling */
            .ag-theme-streamlit {
                border: 1px solid #dee2e6;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                width: 100%; /* Ensures table spans the full container width */
                height: 600px; /* Increases the height of the table */
            }
            .ag-header-cell-label {
                color: #333;
                font-weight: 600;
            }
            .ag-cell {
                color: #495057;
                font-size: 16px; /* Slightly larger font for better readability */
            }

            /* Ensuring Main Container Fills Full Width */
            [data-testid="stAppViewContainer"] {
                max-width: 100% !important; /* Full width of the page */
                padding: 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    inject_css()

    def create_container_with_color(id, color="#E4F2EC"):
        # todo: instead of color you can send in any css
        plh = st.container()
        html_code = """<div id = 'my_div_outer'></div>"""
        st.markdown(html_code, unsafe_allow_html=True)
        with plh:
            inner_html_code = """<div id = 'my_div_inner_%s'></div>""" % id
            plh.markdown(inner_html_code, unsafe_allow_html=True)
        ## applying style
        chat_plh_style = """
            <style>
                div[data-testid='stVerticalBlock']:has(div#my_div_inner_%s):not(:has(div#my_div_outer)) {
                    background-color: %s;
                    border-radius: 20px;
                    padding: 10px;
                };
            </style>
            """
        chat_plh_style = chat_plh_style % (id, color)
        st.markdown(chat_plh_style, unsafe_allow_html=True)
        return plh



    if len(ordered_data) == 0:
        st.write("No items yet.")
    else:
        for index, item in ordered_data.iterrows():
            test_color = st.container(border=True, key=f"bluey_{index}")
            testsse_color = create_container_with_color(f"bluey_{index}", color="#E4F2EC")
            with testsse_color:
                item_cols = st.columns([0.5, 0.5, 5, 0.5, 0.5, 0.5])
                with item_cols[0]:
                    if index > 0:
                        if st.button("↑", key=f"up_{index}"):
                            move_row(index, "up")
                with item_cols[1]:
                    if index < len(ordered_data) - 1:
                        if st.button("↓", key=f"down_{index}"):
                            move_row(index, "down")
                with item_cols[2]:
                    if st.session_state["editing_row"] == index:
                        new_desc = st.text_input(
                            "Outline Section", 
                            value=item["description"], 
                            key=f"description_edit_{index}"
                        )
                        if st.button("Save", key=f"save_edit_{index}"):
                            save_edit(index, new_desc)
                    else:
                        st.write(f"**{item.get('description', '(No description)')}**")
                with item_cols[4]:
                    if st.button("✐", key=f"rename_{index}"):
                        edit_row(index)
                with item_cols[5]:
                    if st.button("🗑", key=f"delete_{index}"):
                        delete_row(index)
                #--- SEE MORE DETAIL BUTTON (PSEUDOCODE) ---
                # """
                # if st.button("See more detail →", key=f"next_{index}"):
                #     # Step 1: Potentially expand sub-layers or sub-items
                #     # Step 2: Could display hidden content if 'Invisible Description' 
                #     # Step 3: Could set st.session_state["current_layer_index"] to next level 
                #     # or open a modal with details. 
                #     # (Implementation depends on your final structure)
                # """
                next_button_col = st.columns([10, 1])[1]
                with next_button_col:
                    if st.button("See more detail →", key=f"next_{index}"):
                        st.success("Detail expansion (future feature).")

            # 'Add Item' button:
            add_item_center = st.columns([4, 1, 4])[1]
            with add_item_center:
                if st.button("➕ Add Item", key=f"plus_{index}"):
                    add_row(index)

    # At the end, update the original project_dict with the final data
    # so subsequent code can stay in sync.
    st.session_state["project_dict"]["outline_layers"][0]["outline_items"] = (
        st.session_state["data"].to_dict(orient="records")
    )
