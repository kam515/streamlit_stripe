import streamlit as st
import pandas as pd

# Local imports
from models import Project
from openai_client import get_openai_client
from session_setup import (
    init_session_states, save_state, undo, redo
)
from data_ops import to_nested_dict
from ui_components import inject_css, create_container_with_color

# ========== Configurations ==========
st.set_page_config(page_title="Sample App", layout="wide")
API_KEY = st.secrets["openai_api_info"]["openai_key"]
MODEL = "gpt-4o-2024-08-06"
client = get_openai_client(api_key=API_KEY)

# ========== Initialize Session State ==========
init_session_states()
inject_css()

# ========== Form Section ==========

st.latex(r'''x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}''')


with st.form("my_form"):
    prompty = st.text_input("What is the goal of your project?")
    submit_col = st.columns([11, 2])[1]
    with submit_col:
        if st.form_submit_button("Start my outline!"):
            st.session_state["form_submitted"] = True

# Biggest picture layer API call
system_message = "You are an expert strategic planner who creates first big picture outlines that comprehensively accomplish the stated goal. You provide clear descriptions and justification."
if st.session_state["form_submitted"] and not st.session_state["generated_once"]:
    # Example of an OpenAI call that returns a Project object
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": (
                    f"Make a comprehensive big picture outline of the full process of achieving this goal with about 2-5 items: {prompty}"
                ),
            },
        ],
        response_format=Project,  # Pydantic parse
   ) 
    project_response = completion.choices[0].message.parsed
    nested_dict = to_nested_dict(project_response)
    st.write('nested_dict:')
    st.session_state["project_dict"] = nested_dict
    st.write(nested_dict)
    st.session_state["generated_once"] = True
    st.session_state["current_layer"] = 0

# if st.session_state["current_layer"] > 0:
#     ...

# ========== *SAVE_STATE_TO_DB* Build Dataframe for the first layer ==========
if st.session_state["project_dict"] is not None and st.session_state["current_layer"] == 0: # AND WE ARE ON THE FIRST LAYER!!!
    layer = st.session_state["project_dict"]["outline_layers"]
    layer_name = layer["layer_name"]
    outline_items = layer["outline_items"]
    df_data = pd.DataFrame(outline_items)
    df_data["outline_text"] = df_data["title"] + ": " + df_data["description"]
    

    # Create local session states if not set
    if st.session_state["data"] is None:
        st.session_state["data"] = df_data.copy()
    if st.session_state["order"] is None:
        st.session_state["order"] = list(range(len(df_data)))

    # ========== Utility Functions for the Data Table ==========
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
        st.session_state["order"] = list(range(len(data_local)))
        st.session_state["data"] = data_local

    def edit_row(index):
        st.session_state["editing_row"] = index

    def save_edit(index, new_desc):
        save_state()
        ordered_data = st.session_state["data"].iloc[st.session_state["order"]].reset_index(drop=True)
        ordered_data.loc[index, "outline_text"] = new_desc
        global_index = st.session_state["order"][index]
        st.session_state["data"].loc[global_index, "outline_text"] = new_desc
        st.session_state["editing_row"] = None

    def add_row(position, new_desc=""):
        save_state()
        data_local = st.session_state["data"]
        order_local = st.session_state["order"]
        new_id = (data_local.index.max() + 1) if not data_local.empty else 0
        new_row = pd.DataFrame({"outline_text": [new_desc]}, index=[new_id])
        st.session_state["data"] = pd.concat([data_local, new_row])
        order_local.insert(position + 1, new_id)
        st.session_state["order"] = order_local

    # ========== Undo/Redo Buttons ==========
    top_row = st.columns([0.5, 0.5, 7, 2])
    with top_row[0]:
        st.button("⟲", on_click=undo, disabled=not st.session_state["history"], help="Undo")
    with top_row[1]:
        st.button("↻", on_click=redo, disabled=not st.session_state["redo_stack"], help="Redo")

    # *SAVE_STATE_TO_DB* Navigate to previous layer (if it exists--otherwise don't allow the button to be pressed and show a helper text)
    if st.button("<  Bigger Picture"):
        st.info("Will navigate to an earlier outline layer (future feature).")

    st.markdown(f"<h2 style='text-align:center;'>{layer_name}</h2>", unsafe_allow_html=True)
    st.write("---")

    ordered_data = st.session_state["data"].iloc[st.session_state["order"]].reset_index(drop=True)

    if ordered_data.empty:
        st.write("No items yet.")
    else:
        for idx, row in ordered_data.iterrows():
            container = create_container_with_color(f"row_{idx}", color="#E4F2EC")
            with container:
                row_cols = st.columns([0.5, 0.5, 5, 0.5, 0.5, 0.5])
                with row_cols[0]:
                    if idx > 0 and st.button("↑", key=f"up_{idx}"):
                        move_row(idx, "up")
                with row_cols[1]:
                    if idx < len(ordered_data) - 1 and st.button("↓", key=f"down_{idx}"):
                        move_row(idx, "down")
                with row_cols[2]:
                    if st.session_state["editing_row"] == idx:
                        new_desc = st.text_input(
                            "Outline Section",
                            value=row["outline_text"],
                            key=f"description_edit_{idx}"
                        )
                        if st.button("Save", key=f"save_edit_{idx}"):
                            save_edit(idx, new_desc)
                    else:
                        st.write(f"**{row.get('outline_text', '(No description)')}**")
                with row_cols[4]:
                    if st.button("✐", key=f"rename_{idx}"):
                        edit_row(idx)
                with row_cols[5]:
                    if st.button("🗑", key=f"delete_{idx}"):
                        delete_row(idx)

                
                # *SAVE_STATE_TO_DB* Future sub-layer expansion
                with row_cols[2]:
                    with st.expander("See more detail"):
                        # if st.button("See more detail →", key=f"next_{idx}"):
                        st.success("Detail expansion (future feature).")
                
                bottom_of_container = st.columns([4, 1, 4])
                # Adds a row
                add_item_center = bottom_of_container[1]
                with add_item_center:
                    if st.button("➕ Add Item", key=f"plus_{idx}"):
                        add_row(idx)

    # *SAVE_STATE_TO_DB* Sync final data back to session's project_dict
    st.session_state["project_dict"]["outline_layers"]["outline_items"] = (
        st.session_state["data"].to_dict(orient="records")
    )

