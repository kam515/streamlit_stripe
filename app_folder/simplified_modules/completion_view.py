import streamlit as st
import streamlit.components.v1 as components
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
#inject_css()

# ========== User Info ==========
user_id = None

list_of_field_records = get_list_of_field_records_from_dict(gather_project_dict(17))

df = pd.DataFrame(list_of_field_records)

df["layer_number"] = df["layer_index"].astype(str).apply(lambda x: x.count('.'))

st.write(df.sort_values(by="layer_index", ascending=True))

cols_for_layers = st.columns([1, 1, 1, 1, 1])

for index, row in df.iterrows():
    heading_level = row["layer_number"]
    spaces_num = heading_level - 1
    st.markdown('#'*heading_level + ' '+row["title"] + ": "+ row["description"])

    with cols_for_layers[0]:
        with st.container(border=True):
            st.markdown()


# regenerate option
# dynamically make columns/containers based on layers and items w/in layer
# add tags to each layer
# functions for headings, diagrams, images, laTeX, etc.


# OUTLINE MAKER--> PLANNING ELEMENTS--> EXECUTE

# inputs... like lesson objective, age, etc.


# Home button
# Landing page