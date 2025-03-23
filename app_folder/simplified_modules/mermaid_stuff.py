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
# inject_css()

# ========== User Info ==========
user_id = None

list_of_field_records = get_list_of_field_records_from_dict(gather_project_dict(17))

df = pd.DataFrame(list_of_field_records)

df["layer_number"] = df["layer_index"].astype(str).apply(lambda x: x.count('.'))

st.write(df.sort_values(by="layer_index", ascending=True))

with st.popover('Document View'):
    for index, row in df.iterrows():
        heading_level = row["layer_number"]
        spaces_num = heading_level - 1
        st.markdown('\t'*spaces_num +'#'*heading_level + ' '+row["title"] + ": "+ row["description"])


# Filter only layer_number == 1 to get top-level nodes
top_level = df[df["layer_number"] == 1].sort_values("layer_index")

# Initialize the Mermaid diagram with a left-to-right direction
mermaid_code = ["graph LR"]

mermaid_code.append("""
    classDef smallBox fill:#f9f9f9,stroke:#333,stroke-width:2px,font-size:12px,width:160px,height:100px,white-space:normal;
""")

# Create a dictionary to track node relationships
node_map = {}

# Function to generate a valid Mermaid node identifier
def get_node_id(title):
    return title.replace(" ", "_").replace("-", "_").replace(".", "_")

# Process each row and generate the Mermaid graph
for _, row in df.iterrows():
    parent_id = get_node_id(str(row["layer_index"]))
    #node_label = f'["{row["title"]}: {row["description"]}"]'
    node_label = f'["{row["title"]}"]'
    
    # Store the node in a mapping to build relationships
    node_map[parent_id] = node_label

    # Find parent by truncating the layer_index (assuming dot notation for hierarchy)
    parent_layer = ".".join(str(row["layer_index"]).split(".")[:-1])
    parent_layer_id = get_node_id(parent_layer) if parent_layer else None

    # Add relationship if there is a parent
    if parent_layer and parent_layer_id in node_map:
        mermaid_code.append(f'{parent_layer_id} --> {parent_id}')

    # Add the node itself
    mermaid_code.append(f'{parent_id}{node_label}')

# Convert list to string and print the Mermaid code
mermaid_code_str = "\n".join(mermaid_code)
# st.markdown(mermaid_code_str)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</head>
<body>
    <div class="mermaid">{mermaid_code_str}</div>
</body>
</html>
"""

components.html(html_code, height=1000)

# Initialize the Mermaid diagram with a left-to-right direction
mermaid_code = ["graph LR"]

# Define Mermaid styling for nodes (improves readability)
mermaid_code.append("""
    classDef smallBox fill:#f9f9f9,stroke:#333,stroke-width:2px,font-size:12px;
""")

# Create a dictionary to track node relationships
node_map = {}

# Function to generate a valid Mermaid node identifier
def get_node_id(title):
    return title.replace(" ", "_").replace("-", "_").replace(".", "_")

# Process each row and generate the Mermaid graph
for _, row in df.iterrows():
    parent_id = get_node_id(str(row["layer_index"]))
    
    # Fix text wrapping with `wrap` keyword
    node_label = f'{parent_id}["{row["title"]}: <br> {row["description"]}"]:::smallBox'
    
    # Store the node in a mapping to build relationships
    node_map[parent_id] = node_label

    # Find parent by truncating the layer_index (assuming dot notation for hierarchy)
    parent_layer = ".".join(str(row["layer_index"]).split(".")[:-1])
    parent_layer_id = get_node_id(parent_layer) if parent_layer else None

    # Add relationship if there is a parent
    if parent_layer and parent_layer_id in node_map:
        mermaid_code.append(f'{parent_layer_id} --> {parent_id}')

    # Add the node itself
    mermaid_code.append(node_label)

# Convert list to string for Mermaid
mermaid_code_str = "\n".join(mermaid_code)

# Embed the Mermaid code into an HTML template
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    <style>
        .mermaid {{
            display: flex;
            justify-content: center;
            max-width: 100%;
        }}
        .mermaid svg {{
            max-width: 90%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
        {mermaid_code_str}
    </div>
</body>
</html>
"""

# Render Mermaid diagram in Streamlit
st.title("Styled Mermaid Diagram with Text Wrapping")
components.html(html_code, height=1000)



# Initialize the Mermaid diagram with a left-to-right direction
mermaid_code = ["graph LR"]

# Define Mermaid styling for nodes (improves readability)
mermaid_code.append("""
    classDef smallBox fill:#f9f9f9,stroke:#333,stroke-width:2px,font-size:12px;
""")

# Create a dictionary to track node relationships
node_map = {}

# Function to generate a valid Mermaid node identifier
def get_node_id(title):
    return title.replace(" ", "_").replace("-", "_").replace(".", "_")

# Process each row and generate the Mermaid graph
for _, row in df.iterrows():
    parent_id = get_node_id(str(row["layer_index"]))
    
    # Fix text wrapping with `wrap` keyword
    node_label = f'{parent_id}["{row["title"]}: <br> {row["description"]}"]:::smallBox'
    
    # Store the node in a mapping to build relationships
    node_map[parent_id] = node_label

    # Find parent by truncating the layer_index (assuming dot notation for hierarchy)
    parent_layer = ".".join(str(row["layer_index"]).split(".")[:-1])
    parent_layer_id = get_node_id(parent_layer) if parent_layer else None

    # Add relationship if there is a parent
    if parent_layer and parent_layer_id in node_map:
        mermaid_code.append(f'{parent_layer_id} --> {parent_id}')

    # Add the node itself
    mermaid_code.append(node_label)

# Convert list to string for Mermaid
mermaid_code_str = "\n".join(mermaid_code)

# Embed the Mermaid code into an HTML template with dynamic height adjustment
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    <style>
        .mermaid-container {{
            display: flex;
            justify-content: center;
            width: 100%;
            overflow: hidden;
        }}
        .mermaid svg {{
            max-width: 90%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="mermaid-container">
        <div id="mermaid-div" class="mermaid">
            {mermaid_code_str}
        </div>
    </div>
    <script>
        function adjustHeight() {{
            var mermaidDiv = document.getElementById("mermaid-div");
            var iframe = window.frameElement;
            if (iframe && mermaidDiv) {{
                setTimeout(() => {{
                    iframe.style.height = mermaidDiv.scrollHeight + "px";
                }}, 1000);
            }}
        }}
        window.onload = adjustHeight;
        window.addEventListener('resize', adjustHeight);
    </script>
</body>
</html>
"""

# Render Mermaid diagram in Streamlit with an initial default height
st.title("Dynamically Adjusting Mermaid Diagram in Streamlit")
components.html(html_code, height=1000, scrolling=True)
