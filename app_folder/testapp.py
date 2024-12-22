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
MODEL = "gpt-4o-2024-08-06"
api_key = ...
client = OpenAI(api_key=api_key)

st.set_page_config(layout="wide")
st.title("Katie's Subscription App POC")

class Dataset(BaseModel):
    chart_type: str
    x_axis_label: str
    x_axis_values: list[float]
    y_axis_label: str
    y_axis_values: list[float]

class OutlineSection(BaseModel):
    section_title: str
    subsections: list[str]

class OutlineBuilder(BaseModel):
    title: str
    major_subsections: list[OutlineSection]

class MarkdownGen(BaseModel):
    markdown_to_render: str
    justification_of_meeting_criteria_in_prompt: str

with st.form("my_form"):
    st.write("Inside the form")
    my_number = st.slider('Pick a number', 1, 10)
    my_color = st.selectbox('Pick a color', ['red','orange','green','blue','violet'])
    prompty = st.text_input(
        "Write your prompt:",
        "",
        key="placeholder",
    )
    submitted = st.form_submit_button('Submit')

    if submitted:
        # Markdown GEN
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Generate content in markdown based on the instructions given."},
                {"role": "user", "content": prompty},
                # {"role": "user", "content": "I want a 2x3 table with column titles that are the column numbers and nothing in the rows."},
            ],
            response_format=MarkdownGen,
        )
        markdown_created = completion.choices[0].message.parsed.markdown_to_render
    
if submitted:
    st.markdown(markdown_created)
