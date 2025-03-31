import streamlit as st

def inject_css():
    """
    Inject custom CSS to override default Streamlit styling.
    """
    st.markdown(
        """
        <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
            color: #333;
            margin: 0;
            padding: 0;
        }
        .main {
            width: 100% !important;
            padding: 0 !important;
        }
        h1, h2, h3 {
            font-weight: 700;
            color: #222;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            text-align: center;
        }
        [data-testid="stSidebar"] {
            background: #343a40;
            color: #f8f9fa;
            border-right: 2px solid #495057;
        }
        button {
            display: block;
            margin: 20px auto;
            background-color: #0d6efd;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .ag-theme-streamlit {
            border: 1px solid #dee2e6;
            background-color: #ffffff;
            primaryColor: #40ffe8;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            height: 600px;
        }
        .ag-header-cell-label {
            color: #333;
            font-weight: 600;
        }
        .ag-cell {
            color: #495057;
            font-size: 16px;
        }
        [data-testid="stAppViewContainer"] {
            max-width: 100% !important;
            padding: 0 !important;
        }
        a {
            color: #40ffe8; 
        }
        a:hover {
            color: #2ea395; /* Slightly darker shade for hover effect */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def create_container_with_color(id_tag, color="#E4F2EC"):
    """
    Build a placeholder container with a custom background color.
    """
    plh = st.container()
    html_code = "<div id='my_div_outer'></div>"
    st.markdown(html_code, unsafe_allow_html=True)
    with plh:
        inner_html_code = f"<div id='my_div_inner_{id_tag}'></div>"
        plh.markdown(inner_html_code, unsafe_allow_html=True)
    style = f"""
        <style>
        div[data-testid='stVerticalBlock']:has(div#my_div_inner_{id_tag}):not(:has(div#my_div_outer)) {{
            background-color: {color};
            border-radius: 20px;
            padding: 10px;
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)
    return plh
