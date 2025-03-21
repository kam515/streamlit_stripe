import json
from pydantic import BaseModel
import streamlit as st
import supabase
from supabase import create_client, Client
sb_url = st.secrets["supabase_info"]["sb_url"]
sb_key = st.secrets["supabase_info"]["sb_key"]
Client = create_client(sb_url, sb_key)
from datetime import datetime
from itertools import groupby
from operator import itemgetter
import pprint

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

def get_user_projects(user_id):
    response = (
        Client.table("projects")
        .select("project_title")
        .is_("UID", user_id)  # Ensure we correctly check for NULL in the "UID" column
        .execute()
    )
    # Access the "data" attribute to get the actual result list
    data = response.data
    project_titles = [i['project_title'] for i in data]

    if data:  # Ensure there's at least one result
        return project_titles
    else:
        return []  # Return None if no matching project is found 

def get_project_metadata(project_title, user_id):
    response = (
        Client.table("projects")
        .select("project_id")
        .eq("project_title", project_title)
        .is_("UID", user_id)  
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

def save_layer(field_types, prompt_for_field, df_data, project_id, current_layer):
    # layer name
    print('~~~~~~~~~~~~~~IN SAVE_LAYER FUNCTION~~~~~~~~~~~~~~')
    #TODO: add layer name to this function and save it as a field "like 1." so it would always be sorted first--even before 0
    for row_number, row in df_data.iterrows():  # Proper way to iterate over rows with index
        title = row['title']  # Access value by column name
        description = row['description']
        criteria_for_success = row['criteria_for_success']
        justification = row['justification']
        # I want to chop everything off after the last period and the last period
        # 1.0.2.4 --> 
        layer_index = f"{current_layer}.{row_number}"
        print('layer_index being saved to db: ', layer_index) 
        field_type = field_types[row_number-1] # getting correct index in field_types
        response = (
            Client.table("fields")
            .insert({"field_type": field_type, 
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

def gather_project_dict(project_id):
    response = Client.table("fields") \
    .select("* distinct on (layer_index)") \
    .eq("project_id", project_id) \
    .order("layer_index") \
    .order("field_datetime", desc=True) \
    .execute()
    nested_dict = to_nested_dict(response)
    return nested_dict

def get_list_of_field_records_from_dict(dict_):
    list_of_field_records = dict_['data']
    # make df with cols field_id, field_type, prompt_for_field, project_id, field_datetime, 
    for record in list_of_field_records:
        if isinstance(record["field_datetime"], str):  # Convert only if still a string
            record["field_datetime"] = datetime.fromisoformat(record["field_datetime"])
    # Sort by layer_index first, then by field_datetime (latest first)
    list_of_field_records.sort(key=lambda x: (x["layer_index"], x["field_datetime"]), reverse=True)
    # Use groupby to keep only the most recent entry per layer_index
    list_filtered = [next(group) for _, group in groupby(list_of_field_records, key=itemgetter("layer_index"))]
    # Convert datetime back to string if needed
    for record in list_filtered:
        record["field_datetime"] = record["field_datetime"].isoformat()
    list_filtered.sort(key=lambda x: (x["layer_index"]))
    return list_filtered
