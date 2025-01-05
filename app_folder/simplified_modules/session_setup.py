import streamlit as st
import copy

def init_session_states():
    """
    Initialize keys if they don't exist in st.session_state.
    """
    defaults = {
        "project_dict": None,
        "form_submitted": False,
        "generated_once": False,
        "data": None,
        "order": None,
        "history": [],
        "redo_stack": [],
        "editing_row": None
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