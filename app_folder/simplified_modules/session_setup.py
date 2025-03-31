import streamlit as st
import copy

def init_session_states():
    """
    Initialize keys if they don't exist in st.session_state.
    """
    defaults = {
        # project major things
        "initiated_project": False,
        "new_project": False,
        "existing_project_selected": None,
        "project_id": None,
        "project_title": None,
        "project_dict": None, # output of the openai API call
        "form_submitted": False, 
        # current page major things
        "generated_once": False, # changes to True and stays there after the first API call
        "current_layer": None, # quickly changing layer info on page
        "prompt_for_current_layer": None,
        "data": None, 
        "order": None,
        "history": [],
        "redo_stack": [],
        "editing_row": None,
        'skip_saving_to_db': False,
        "prompty": None,
        "layer_name": None,
        "prompt_for_sublayer": None,
        "direction": None,
        "switch_action": False,
        "row_layer_index": None,
        "edit_counter": 0,
        "layer_period_count": 1
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def save_state():
    """
    Save current data/order for undo.
    """
    state = {
        "data": st.session_state["data"].copy(),
        "order": st.session_state["order"][:]
    }
    st.session_state["history"].append(state)
    st.session_state["redo_stack"].clear()

def undo():
    if st.session_state["history"]:
        prev_state = st.session_state["history"].pop()
        # Save current state for redo
        st.session_state["redo_stack"].append({
            "data": st.session_state["data"].copy(),
            "order": st.session_state["order"][:]
        })
        st.session_state["data"] = prev_state["data"]
        st.session_state["order"] = prev_state["order"]

def redo():
    if st.session_state["redo_stack"]:
        next_state = st.session_state["redo_stack"].pop()
        # Save current state for another undo
        st.session_state["history"].append({
            "data": st.session_state["data"].copy(),
            "order": st.session_state["order"][:]
        })
        st.session_state["data"] = next_state["data"]
        st.session_state["order"] = next_state["order"]
