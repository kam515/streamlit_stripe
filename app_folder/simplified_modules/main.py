import streamlit as st
import pandas as pd
import supabase
import re
import json
from datetime import datetime
from itertools import groupby
from operator import itemgetter
import pprint
# Local imports
from models import Project, making_openai_call, making_openai_call_sublayer
from openai_client import get_openai_client
from session_setup import (
    init_session_states, save_state, undo, redo
)
from data_ops import to_nested_dict, get_project_metadata, save_new_project, save_layer, get_user_projects, gather_project_dict, get_list_of_field_records_from_dict
from ui_components import inject_css, create_container_with_color
from supabase import create_client, Client

sb_url = st.secrets["supabase_info"]["sb_url"]
sb_key = st.secrets["supabase_info"]["sb_key"]
Client = create_client(sb_url, sb_key)

# ========== Configurations ==========
st.set_page_config(page_title="Thought Partner", layout="wide")
API_KEY = st.secrets["openai_api_info"]["openai_key"]
MODEL = "gpt-4o-2024-08-06"
client = get_openai_client(api_key=API_KEY)

# ========== Initialize Session State ==========
init_session_states()
inject_css()

# ========== User Info ==========
user_id = None

with st.sidebar:
    st.write('Navigation buttons will go here')

# ========== Options that appear first ==========
if not st.session_state["initiated_project"]:
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col2: # new
        st.session_state.new_project = st.button('+ New Project')
    with col3: # existing
        user_projects = get_user_projects(user_id)
        st.session_state["existing_project_selected"] = st.selectbox(
            "Select an existing project:",
            user_projects,
            index=None
        )

if st.session_state["existing_project_selected"] and not st.session_state["generated_once"]:
    st.session_state["layer_name"] = st.session_state["existing_project_selected"]
    st.session_state["initiated_project"] = True
    st.session_state["generated_once"] = True
    st.session_state["project_id"] = get_project_metadata(st.session_state["existing_project_selected"], user_id)
    st.session_state["project_title"] = st.session_state["existing_project_selected"]
    st.session_state["project_dict"] = gather_project_dict(st.session_state["project_id"])
    list_for_testing = get_list_of_field_records_from_dict(st.session_state["project_dict"])
    st.session_state.prompty = list_for_testing[0]['prompt_for_field'].replace("Make a comprehensive big picture outline of the full process of achieving this goal with about 2-5 items: ", "")
    df_data = pd.DataFrame(list_for_testing)
    st.session_state["current_layer_index"] = "1."
    df_data["outline_text"] = df_data["title"] + ": " + df_data["description"]
    st.session_state["df_data_complete"] = df_data.copy()
    df_data = df_data[df_data['layer_index'].str.count(r'\.') == 1]
    
            
# ========== Form Section ==========
if st.session_state.new_project:
    st.session_state["initiated_project"] = True
    if not st.session_state["form_submitted"]:
        with st.form("my_form"):
            st.session_state.prompty = st.text_input("What is the goal of your project?")
            submit_col = st.columns([11, 2])[1]
            with submit_col:
                if st.form_submit_button("Start my outline!"):
                    st.session_state["form_submitted"] = True
                    # st.rerun()

# ========== *SAVE_STATE_TO_DB* Build Dataframe for the first layer ==========
system_message = "You are an expert strategic planner who creates first big picture outlines that comprehensively accomplish the stated goal. You provide clear descriptions and justification."
if st.session_state["form_submitted"] and not st.session_state["generated_once"]:
    prompt = f"Make a comprehensive big picture outline of the full process of achieving this goal with about 2-5 items: {st.session_state.prompty}"
    response_format = Project
    nested_dict = making_openai_call(client, MODEL, system_message, prompt, response_format)
#     with open("data.txt", "w", encoding="utf-8") as file:
#         json.dump(nested_dict, file)
    # with open("data.txt", "r", encoding="utf-8") as file:
    #     nested_dict = json.load(file)
    # ========== AFTER GENERATION--CREATE NEW PROJECT ========== 
    st.session_state["project_dict"] = nested_dict
    st.session_state["project_title"] = nested_dict["project_title"]
    project_type = "drafted workflow"
    save_new_project(st.session_state["project_title"], project_type, user_id)
    # ========== FIRST LAYER DECONSTRUCTION ==========
    st.session_state["generated_once"] = True
    st.session_state["current_layer_index"] ="1."
    st.session_state["prompt_for_current_layer"] = f"Make a comprehensive big picture outline of the full process of achieving this goal with about 2-5 items: {st.session_state.prompty}"
    layer = st.session_state["project_dict"]["outline_layers"]
    st.session_state["layer_name"] = layer["layer_name"]
    outline_items = layer["outline_items"]
    df_data = pd.DataFrame(outline_items)
    st.session_state["df_data_complete"] = df_data.copy()
    df_data["outline_text"] = df_data["title"] + ": " + df_data["description"]
    # ========== GATHERING INFO + SAVING LAYER THE FIRST TIME ==========
    project_id = get_project_metadata(st.session_state["project_title"], user_id)
    field_types = ['outline_item' for i in outline_items] # all will be type outline_item for first layer
    prompt_for_field = st.session_state["prompt_for_current_layer"].replace("Make a comprehensive big picture outline of the full process of achieving this goal with about 2-5 items: ", "")
    current_layer = st.session_state["current_layer_index"].replace(".", "")
    save_layer(field_types, prompt_for_field, df_data, project_id, current_layer)
    st.session_state["project_id"] = get_project_metadata(st.session_state["project_title"], user_id)
    st.session_state["project_dict"] = gather_project_dict(st.session_state["project_id"])
    list_for_testing = get_list_of_field_records_from_dict(st.session_state["project_dict"])
    st.session_state.prompty = list_for_testing[0]['prompt_for_field'].replace("Make a comprehensive big picture outline of the full process of achieving this goal with about 2-5 items: ", "")
    df_data = pd.DataFrame(list_for_testing)
    st.session_state["current_layer_index"] = "1."
    df_data["outline_text"] = df_data["title"] + ": " + df_data["description"]
    st.session_state["df_data_complete"] = df_data.copy()
    df_data = df_data[df_data['layer_index'].str.count(r'\.') == 1]


# ========== *SAVE_STATE_TO_DB* Build Dataframe for layers after the first layer ==========

# list_for_testing = get_list_of_field_records_from_dict(gather_project_dict(17))
# st.write('LIST FOR TESTING')
# st.write(list_for_testing)
original_project_goal = st.session_state.prompty
# title_of_layer = 
def build_prompt_for_sub_layer_gen(original_project_goal, title_and_desc_of_layer):
    prompt = f"""
    Big picture project goal: \"{original_project_goal}\"
    Current phase of the project we are planning: \"{title_and_desc_of_layer}\"
    Make an outline of the full process of achieving the current phase goal with about 2-5 items.
    """
    return prompt

def build_sub_layer(client, MODEL, system_message, prompt, sesh_state_current_layer_index, sesh_state_project_title):
    nested_dict = making_openai_call_sublayer(client, MODEL, system_message, prompt)
    current_layer = str(sesh_state_current_layer_index) #+ str(idx)
    df_data = pd.DataFrame(nested_dict['outline_items'])
    field_types = ['outline_item' for i in nested_dict['outline_items']]
    project_id = get_project_metadata(sesh_state_project_title, user_id)
    save_layer(field_types, prompt, df_data, project_id, current_layer)
    return nested_dict

def check_for_sublayer(row, df_data_complete):
    sublayer_bool = False
    current_layer_idx = row["layer_index"]
    df_indices_for_project = list(df_data_complete["layer_index"].unique())
    if str(current_layer_idx) + ".0" in df_indices_for_project:
        sublayer_bool = True
    if "added_row" in current_layer_idx:
        sublayer_bool = False
    return sublayer_bool

def render_existing_layer(sesh_state_df_data_complete, direction, current_layer_index, project_title=st.session_state["project_title"]):
    """
    Handles "zoom in" / "zoom out" logic based on current_layer_index.
    Returns (new_layer_df, layer_name).
    """

    df_data_complete = sesh_state_df_data_complete
    current_layer_period_count = current_layer_index.count('.')

    if direction == "down":
        # Filter for the current layer first to safely retrieve the layer_name
        filtered_down = df_data_complete[df_data_complete["layer_index"] == current_layer_index]
        if not filtered_down.empty:
            layer_name = filtered_down["title"].iloc[0]
        else:
            # Fallback if there's no row matching current_layer_index
            layer_name = project_title

        # Now retrieve all rows that are exactly one more period deeper
        new_layer_df = df_data_complete[
            (df_data_complete["layer_index"].str.count(r'\.') == current_layer_period_count + 1) &
            (df_data_complete["layer_index"].str.startswith(current_layer_index + "."))
        ]

    else:
        # Remove the last ".x" from current_layer_index
        layer_index_up = re.sub(r'\.[^.]*$', '', current_layer_index)

        # Next level up might require removing the next dot chunk
        layer_previx_up = re.sub(r'\.[^.]*$', '', layer_index_up)

        # Filter for the parent's parent index to retrieve layer_name
        filtered_up = df_data_complete[df_data_complete["layer_index"] == layer_previx_up]
        if not filtered_up.empty:
            layer_name = filtered_up["title"].iloc[0]
        else:
            # Default to project_title if we can't find a match
            layer_name = project_title

        # Now retrieve all rows that are exactly one fewer period (the parent's siblings)
        new_layer_df = df_data_complete[
            (df_data_complete["layer_index"].str.count(r'\.') == current_layer_period_count - 1) &
            (df_data_complete["layer_index"].str.startswith(layer_previx_up + "."))
        ]

    return new_layer_df, layer_name


def render_existing_layer(sesh_state_df_data_complete, direction, current_layer_index, project_title=st.session_state["project_title"]):
    """
    1.0
    - up: greyed out
    - down: everything with two periods and starting with 1.0.
    1.0.3
    - up: 1.0 (so removing the last period and anything following) and grabbing anything with one period starting with 1.
    - down: everything with three periods and starting with 1.0.3.
    """
    df_data_complete = sesh_state_df_data_complete
    # filter df_data_complete for rows where df_data_complete["layer_index"] has current_layer (int) + 1 periods in it and has row["layer_index"] (str) preceding the last period
    current_layer_period_count = current_layer_index.count('.')
    if direction == "down":
        layer_name = df_data_complete[df_data_complete["layer_index"]==current_layer_index]["title"].iloc[0]
        new_layer_df = df_data_complete[(df_data_complete["layer_index"].str.count(r'\.') == current_layer_period_count + 1) & (df_data_complete["layer_index"].str.startswith(current_layer_index + "."))]
    else:
        layer_index_up = str(re.sub(r'\.[^.]*$', '', current_layer_index))
        layer_previx_up = re.sub(r'\.[^.]*$', '', layer_index_up)
        
        try:
            layer_name = df_data_complete[df_data_complete["layer_index"]==layer_previx_up]["title"].iloc[0]
        except:
            layer_name = project_title
        new_layer_df = df_data_complete[(df_data_complete["layer_index"].str.count(r'\.') == current_layer_period_count - 1) & (df_data_complete["layer_index"].str.startswith(layer_previx_up + "."))]
    # for sub_idx, sub_row in sublayer_df.iterrows():
    #     st.markdown(f"- {sub_row['title']}: {sub_row['description']}")
    return new_layer_df, layer_name

if st.session_state["project_dict"] is not None: # OR WE CAME IN WITH A PROJECT_ID--BUILD THIS CASE (GRAB EVERYTHING FROM FIELDS THAT HAS A LAYER_INDEX STARTING WITH 1.) 
    # Create local session states if not set
    if st.session_state["data"] is None:
        st.session_state["data"] = df_data.copy()
    if st.session_state["order"] is None:
        st.session_state["order"] = list(range(len(df_data)))
    if st.session_state["switch_action"]:
        st.session_state["project_dict"] = gather_project_dict(st.session_state["project_id"])
        list_for_testing = get_list_of_field_records_from_dict(st.session_state["project_dict"])
        df_data = pd.DataFrame(list_for_testing)
        df_data["outline_text"] = df_data["title"] + ": " + df_data["description"]
        st.session_state["df_data_complete"] = df_data.copy()
        current_layer_index = st.session_state["current_layer_index"]
        direction = st.session_state["direction"]
        st.session_state["data"], st.session_state["layer_name"] = render_existing_layer(st.session_state["df_data_complete"], direction, current_layer_index)
        st.session_state["order"] = list(range(len(st.session_state["data"])))
        st.session_state["current_layer_index"] = st.session_state["data"]["layer_index"]
        st.session_state["switch_action"] = False

    # ========== Utility Functions for the Data Table ==========
    def move_row(index, direction):
        save_state()
        order = st.session_state["order"]
        if direction == "up" and index > 0:
            order[index], order[index - 1] = order[index - 1], order[index]
        elif direction == "down" and index < len(order) - 1:
            order[index], order[index + 1] = order[index + 1], order[index]
        st.session_state["order"] = order
        st.rerun()

    def delete_row(index):
        save_state()
        order = st.session_state["order"]
        data_local = st.session_state["data"]
        row_to_remove = order.pop(index)
        data_local = data_local.drop(row_to_remove).reset_index(drop=True)
        st.session_state["order"] = list(range(len(data_local)))
        st.session_state["data"] = data_local
        st.rerun()

    def edit_row(index):
        st.session_state["editing_row"] = index
        st.rerun()

    def save_edit(index, new_desc):
        save_state()
        ordered_data = st.session_state["data"].iloc[st.session_state["order"]].reset_index(drop=True)
        ordered_data.loc[index, "outline_text"] = new_desc
        global_index = st.session_state["order"][index]
        st.session_state["data"].loc[global_index, "outline_text"] = new_desc
        st.session_state["editing_row"] = None
        st.rerun()

    def add_row(position, field_id="", field_type="", prompt_for_field="", project_id="",
                field_datetime="", layer_index="", title="", description="",
                criteria_for_success="", justification="", outline_text=""):
        save_state()
        data_local = st.session_state["data"]
        order = st.session_state["order"]
        # Determine the previous layer index
        if position == 0:
            prev_layer_index = "_"
        else:
            prev_layer_index = str(data_local.iloc[position - 1]["layer_index"])
        # Determine the next layer index
        if position >= len(data_local):
            next_layer_index = "_"
        else:
            next_layer_index = str(data_local.iloc[position]["layer_index"])
        # Overwrite layer_index for new row
        computed_layer_index = prev_layer_index + next_layer_index + "added_row"
        # Prepare new row with desired columns
        new_row = {
            "field_id": field_id,
            "field_type": field_type,
            "prompt_for_field": prompt_for_field,
            "project_id": project_id,
            "field_datetime": field_datetime,
            "layer_index": computed_layer_index,
            "title": title,
            "description": description,
            "criteria_for_success": criteria_for_success,
            "justification": justification,
            "outline_text": outline_text
        }
        # Split data at position, then insert new row
        before = data_local.iloc[:position+1]
        after = data_local.iloc[position+1:]
        data_local = pd.concat([before, pd.DataFrame([new_row]), after]).reset_index(drop=True)
        # Update session state
        st.session_state["data"] = data_local
        st.session_state["order"] = list(range(len(data_local)))
        st.rerun()





    ## RENDERING CURRENT LAYER ##
    # ========== Undo/Redo Buttons ==========
    top_row = st.columns([0.5, 0.5, 7, 2])
    with top_row[0]:
        st.button("⟲", on_click=undo, disabled=not st.session_state["history"], help="Undo")
    with top_row[1]:
        st.button("↻", on_click=redo, disabled=not st.session_state["redo_stack"], help="Redo")

    # *SAVE_STATE_TO_DB* Navigate to previous layer (if it exists--otherwise don't allow the button to be pressed and show a helper text)
    # WILL FIGURE OUT THE DISABLED THINGY SOON: st.button("<  Bigger Picture", disabled=True, key="dummy_button")
    if st.button("<  Zoom Out"):
        st.session_state["direction"] = "up"
        st.session_state["switch_action"] = True
        st.rerun()


    layer_name = st.session_state["layer_name"]
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
                    sublayer_bool = check_for_sublayer(row, st.session_state["df_data_complete"])
                    st.session_state["current_layer_index"] = row["layer_index"]
                    current_layer_index = st.session_state["current_layer_index"]
                    # Generating sublayer because it isn't there
                    with st.columns([4, 2, 3.2])[1]:
                        if f"sublayer_gen_button_for{current_layer_index}" not in st.session_state:
                            st.session_state[f"sublayer_gen_button_for{current_layer_index}"] = False
                        if not st.session_state[f"sublayer_gen_button_for{current_layer_index}"] and sublayer_bool == False: # NEED TO ADD CONDITION TO DISPLAY SUBLAYER IF IT ALREADY EXISTS
                            gen_yn = st.button("Generate Sub-Items  >", key=f"sublayer_gen_button_for{current_layer_index}_")
                            if gen_yn:
                                st.session_state[f"sublayer_gen_button_for{current_layer_index}"] = True
                                title_and_desc_of_layer = row['title'] + ": " + row['description']
                                st.session_state.prompt_for_sublayer = build_prompt_for_sub_layer_gen(original_project_goal, title_and_desc_of_layer)
                                st.rerun()
                    if st.session_state[f"sublayer_gen_button_for{current_layer_index}"] and sublayer_bool == False:
                        global_index = st.session_state["order"][idx]
                        dict_of_sublayer = build_sub_layer(client, MODEL, system_message, st.session_state.prompt_for_sublayer, st.session_state["current_layer_index"], st.session_state["project_title"])
                        st.session_state["project_dict"] = gather_project_dict(st.session_state["project_id"])
                        list_for_testing = get_list_of_field_records_from_dict(st.session_state["project_dict"])
                        df_data = pd.DataFrame(list_for_testing)
                        df_data["outline_text"] = df_data["title"] + ": " + df_data["description"]
                        st.session_state["df_data_complete"] = df_data.copy()
                        for outline_item in dict_of_sublayer["outline_items"]:
                            st.markdown(f"- {outline_item['title']}: {outline_item['description']}")
                        st.rerun()

                    # SUBLAYER EXISTS
                    if sublayer_bool == True:
                        df_data_complete = st.session_state["df_data_complete"]
                        current_layer_period_count = st.session_state["current_layer_index"].count(".")
                        sublayer_df = df_data_complete[(df_data_complete["layer_index"].str.count(r'\.') == current_layer_period_count + 1) & (df_data_complete["layer_index"].str.startswith(st.session_state["current_layer_index"]+"."))]
                        for sub_idx, sub_row in sublayer_df.iterrows():
                            st.markdown(f"- {sub_row['title']}: {sub_row['description']}")

                        with st.columns([7, 1])[1]:
                            if f"zoom_in_button_for{current_layer_index}" not in st.session_state:
                                st.session_state[f"zoom_in_button_for{current_layer_index}"] = False
                            if not st.session_state[f"zoom_in_button_for{current_layer_index}"]:
                                go_to_level = st.button('Zoom in 🔍', key = f"zoom_in_button_for{current_layer_index}__")
                                if go_to_level:
                                    st.session_state["direction"] = "down"
                                    st.session_state["switch_action"] = True
                                    st.rerun()
       
                bottom_of_container = st.columns([4, 1, 4])
                # Adds a row
                add_item_center = bottom_of_container[1]
                with add_item_center:
                    if st.button("➕", key=f"plus_{idx}"):
                        add_row(idx)
                        # skip saving to db!
                        st.session_state['skip_saving_to_db'] = True
                        st.rerun()

    
    # st.session_state["project_dict"]["outline_layers"]["outline_items"] = (
    #     st.session_state["data"].to_dict(orient="records")
    # )

