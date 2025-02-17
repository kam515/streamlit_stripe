import json
from pydantic import BaseModel
import streamlit as st
import supabase
from supabase import create_client, Client
sb_url = st.secrets["supabase_info"]["sb_url"]
sb_key = st.secrets["supabase_info"]["sb_key"]
Client = create_client(sb_url, sb_key)

def to_nested_dict(obj):
    """
    Convert Pydantic models, lists, and dicts to nested dicts.
    """
    if isinstance(obj, BaseModel):
        data = obj.model_dump()
        return {k: to_nested_dict(v) for k, v in data.items()}
    elif isinstance(obj, list):
        return [to_nested_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: to_nested_dict(v) for k, v in obj.items()}
    return obj

def to_json(obj):
    """
    Return JSON string from nested dict form.
    """
    return json.dumps(to_nested_dict(obj), indent=2)

def get_project_metadata(project_title, user_id):
    response = (
        Client.table("projects")
        .select("project_id")
        .eq("project_title", project_title)
        .is_("UID", None)  # Ensure we correctly check for NULL in the "UID" column
        .execute()
    )
    # Access the "data" attribute to get the actual result list
    data = response.data  

    if data and len(data) > 0:  # Ensure there's at least one result
        return data[0]["project_id"]
    else:
        return None  # Return None if no matching project is found



def save_new_project(project_title, project_type, user_id):
    response = (
            Client.table("projects")
            .insert({"project_title": project_title, 
                     "project_type": project_type,
                     "UID": user_id
                     })
            .execute()
            )

def save_layer(field_type_id, prompt_for_field, df_data, project_id, current_layer):
    for row_number, row in df_data.iterrows():  # Proper way to iterate over rows with index
        title = row['title']  # Access value by column name
        description = row['description']
        criteria_for_success = row['criteria_for_success']
        justification = row['justification']
        layer_index = f"{current_layer}.{row_number}" 
        response = (
            Client.table("fields")
            .insert({"field_type_id": field_type_id, 
                     "prompt_for_field": prompt_for_field,
                     "title": title,
                     "description": description,
                     "criteria_for_success": criteria_for_success,
                     "justification": justification,
                     "project_id": project_id,
                     "layer_index": layer_index
                     })
            .execute()
            )

