import streamlit as st
import pandas as pd
import pathlib
import datetime
import json

st.title('THOUGHT PARTNER')
st.subheader('Creating high-quality documents and projects with you in the drivers seat.')

# Function to inject custom CSS
def inject_css():
    st.markdown(
        """
        <style>
        /* General Body Styling */
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
            color: #333;
            margin: 0;
            padding: 0;
        }

        /* Full-Width Content */
        .main {
            width: 100% !important; /* Force full width */
            padding: 0 !important; /* Remove additional paddings */
        }

        /* Headers */
        h1, h2, h3 {
            font-weight: 700;
            color: #222;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            text-align: center;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: #343a40;
            color: #f8f9fa;
            border-right: 2px solid #495057;
        }

        /* Buttons */
        button {
            display: block; /* Ensure it's treated as a block element */
            margin: 20px auto; /* Center horizontally */
            background-color: #0d6efd;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        /* Table Styling */
        .ag-theme-streamlit {
            border: 1px solid #dee2e6;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%; /* Ensures table spans the full container width */
            height: 600px; /* Increases the height of the table */
        }
        .ag-header-cell-label {
            color: #333;
            font-weight: 600;
        }
        .ag-cell {
            color: #495057;
            font-size: 16px; /* Slightly larger font for better readability */
        }

        /* Ensuring Main Container Fills Full Width */
        [data-testid="stAppViewContainer"] {
            max-width: 100% !important; /* Full width of the page */
            padding: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# PART 1: Form Input
def part_1():
    st.subheader("Step 1: General Information")
    with st.form("form_inputs"):
        # Text inputs
        draft_title = st.text_input("Title:")
        big_picture_goal = st.text_input("Overall goal:")
        audience = st.text_input("Intended audience:")
        time_for_doc = st.time_input("How much time should the audience spend with the document?", value=None)
        time_for_doc = str(time_for_doc)

        col1, col2 = st.columns([8, 2])
        with col2:
            submitted = st.form_submit_button("Create Outline")

        if submitted:
            st.session_state['inputs'] = {
                "Question": ["Working project title", "Overall goal", "Intended audience", "Time with document"],
                "Answer": [draft_title, big_picture_goal, audience, time_for_doc],
                "Decision": ["Keep"] * 4,
            }
        else:
            st.session_state['inputs'] = {}


# PART 2: Editable Table and Markdown Preview
def part_2():
    st.subheader("Step 2: Review the drafted outline")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Editable table
        st.write("Editable Table")
        data = st.session_state.get("inputs", {})
        df = pd.DataFrame(data)
        df["cat"] = "Keep"

        df_edited = st.data_editor(df, num_rows="dynamic", hide_index=True, 
                                column_config={
                                        "Answer": st.column_config.TextColumn(
                                            width="large"
                                        ), 
            "cat": st.column_config.SelectboxColumn(
                "App Category",
                help="The category of the app",
                width="medium",
                options=[
                    "Keep",
                    "Edit",
                    "Delete",
                ],
                required=True,
            )
                                    },)

    df_edited = df_edited.to_json(orient="records", indent=4)
    df_edited = json.loads(df_edited)
    df_edited = pd.DataFrame(df_edited)

    st.session_state['outputs'] = df_edited

    with col2:
        # Markdown preview
        st.write("Markdown Preview")
        preview_md = generate_markdown(st.session_state['outputs'])
        st.markdown(preview_md)

    def render_markdown_columns(markdown_lines):
        actions = []  # To store user choices

        for idx, line in enumerate(markdown_lines):
            left, middle = st.columns([4, 1], gap="medium", border=True)
            with left:
                st.markdown(line)
            with middle:
                action = st.selectbox("", ["keep", "edit", "delete"], key=f"select_{idx}")
                actions.append((line, action))

        return actions

    st.title("Interactive Markdown Editor")

    # Fake markdown outline
    markdown_text = """# Strategic Plan for 2024

    ## 1. Executive Summary
    - Overview of Objectives
    - Key Challenges and Opportunities

    ## 2. Market Analysis
    - **Industry Trends**
    - Emerging Technologies
    - Competitive Landscape
    - **Target Audience**
    - Demographics
    - Behavior and Preferences

    ## 3. Strategic Goals
    - Goal 1: Expand Market Share
    - Goal 2: Enhance Customer Retention
    - Goal 3: Increase Operational Efficiency
    """

    # Render lines in compact containers
    def render_markdown_columns(markdown_lines):
        actions = []
        for line in markdown_lines:
            if line.strip():  # Skip blank lines
                col1, col2 = st.columns([3, 1])  # Shorter columns
                with col1:
                    st.markdown(line, unsafe_allow_html=True)  # Display line
                with col2:
                    action = st.selectbox(f"Action for: {line[:20]}", 
                                        ["None", "Edit", "Delete"], 
                                        key=line)
                    actions.append((line, action))
        return actions

    # Display Markdown with user interactions
    markdown_lines = markdown_text.splitlines()
    actions = render_markdown_columns(markdown_lines)


# Generate Markdown
def generate_markdown(data):
    df = pd.DataFrame(data)
    markdown = ""
    for _, row in df.iterrows():
        if row["Decision"] == "Keep":
            markdown += f"### {row['Question']}\n{row['Answer']}\n\n"
    return markdown

def part_2_6():
    import streamlit as st
    import pandas as pd
    import copy

    # Sample data
    data = {"Name": ["Alice", "Bob", "Charlie"], "Age": [25, 30, 35]}
    df = pd.DataFrame(data)

    # Initialize session state for order, data, and history
    if "data" not in st.session_state:
        st.session_state["data"] = df.copy()
        st.session_state["order"] = list(range(len(df)))
        st.session_state["history"] = []  # Stack for undo/redo
        st.session_state["redo_stack"] = []
        st.session_state["editing_row"] = None  # Track the row being edited

    # Save the current state for undo/redo
    def save_state():
        state = {
            "data": st.session_state["data"].copy(),
            "order": copy.deepcopy(st.session_state["order"]),
        }
        st.session_state["history"].append(state)
        st.session_state["redo_stack"].clear()

    # Move rows up or down
    def move_row(index, direction):
        save_state()
        order = st.session_state["order"]
        if direction == "up" and index > 0:
            order[index], order[index - 1] = order[index - 1], order[index]
        elif direction == "down" and index < len(order) - 1:
            order[index], order[index + 1] = order[index + 1], order[index]
        st.session_state["order"] = order

    # Delete a row
    def delete_row(index):
        save_state()
        order = st.session_state["order"]
        data = st.session_state["data"]
        row_to_remove = order.pop(index)
        st.session_state["data"] = data.drop(row_to_remove).reset_index(drop=True)
        st.session_state["order"] = list(range(len(st.session_state["data"])))

    # Edit a row
    def edit_row(index):
        st.session_state["editing_row"] = index

    def save_edit(index, new_name, new_age):
        save_state()
        ordered_data = st.session_state["data"].iloc[st.session_state["order"]].reset_index(drop=True)
        ordered_data.loc[index, "Name"] = new_name
        ordered_data.loc[index, "Age"] = new_age
        st.session_state["data"] = ordered_data
        st.session_state["editing_row"] = None

    # Undo/Redo functionality
    def undo():
        if st.session_state["history"]:
            state = st.session_state["history"].pop()
            st.session_state["redo_stack"].append(
                {"data": st.session_state["data"], "order": st.session_state["order"]}
            )
            st.session_state["data"] = state["data"]
            st.session_state["order"] = state["order"]

    def redo():
        if st.session_state["redo_stack"]:
            state = st.session_state["redo_stack"].pop()
            st.session_state["history"].append(
                {"data": st.session_state["data"], "order": st.session_state["order"]}
            )
            st.session_state["data"] = state["data"]
            st.session_state["order"] = state["order"]

    # UI Components
    st.write("Reorder rows, edit them, delete them, or undo/redo actions:")

    # Undo/Redo Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Undo", disabled=not st.session_state["history"]):
            undo()
    with col2:
        if st.button("Redo", disabled=not st.session_state["redo_stack"]):
            redo()

    # Reorder the dataframe based on the order column
    ordered_data = st.session_state["data"].iloc[st.session_state["order"]].reset_index(drop=True)

    # Display the table with buttons
    for i, row in ordered_data.iterrows():
        with st.container(border=True):
            cols = st.columns([1, 1, 1, 4, 1, 1, 1])
            with cols[0]:  # Zoom Out Button
                st.button("🔍-", key=f"zoom_out_{i}")
            with cols[1]:  # Up/Down Buttons
                if st.button("↑", key=f"up_{i}"):
                    move_row(i, "up")
                if st.button("↓", key=f"down_{i}"):
                    move_row(i, "down")
            with cols[2]:  # Delete Button
                if st.button("🗑️", key=f"delete_{i}"):
                    delete_row(i)
            with cols[3]:  # Row Content (Editable)
                if st.session_state["editing_row"] == i:
                    new_name = st.text_input("Name", value=row["Name"], key=f"name_edit_{i}")
                    new_age = st.number_input("Age", value=row["Age"], key=f"age_edit_{i}")
                    if st.button("Save", key=f"save_edit_{i}"):
                        save_edit(i, new_name, new_age)
                else:
                    st.write(row["Name"], row["Age"])
            with cols[4]:  # Edit Button
                if st.button("✏️", key=f"edit_{i}"):
                    edit_row(i)
            with cols[5]:  # Zoom In Button
                st.button("🔍+", key=f"zoom_in_{i}")

    # # Display the final ordered dataframe
    # st.write("Reordered DataFrame:")
    # st.dataframe(ordered_data)

    # Undo/Redo Buttons
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col2:
        if st.button("Go Back"):
            pass
    with col3:
        if st.button("Add Detail"):
            pass
    with col4:
        if st.button("Fill Outline"):
            pass


def part_2_5():
    st.subheader("Step 2: Review the drafted outline")
    with st.container(border=True):
    #######################
        import copy

        # Sample data
        data = {"Name": ["Alice", "Bob", "Charlie"], "Age": [25, 30, 35]}
        df = pd.DataFrame(data)

        # Initialize session state for order, data, and history
        if "data" not in st.session_state:
            st.session_state["data"] = df.copy()
            st.session_state["order"] = list(range(len(df)))
            st.session_state["history"] = []  # Stack for undo/redo
            st.session_state["redo_stack"] = []

        # Functions for managing row actions
        def save_state():
            """Save the current state for undo functionality."""
            state = {
                "data": st.session_state["data"].copy(),
                "order": copy.deepcopy(st.session_state["order"]),
            }
            st.session_state["history"].append(state)
            st.session_state["redo_stack"].clear()  # Clear redo stack on new action

        def move_row(index, direction):
            """Move a row up or down."""
            save_state()
            order = st.session_state["order"]
            if direction == "up" and index > 0:
                order[index], order[index - 1] = order[index - 1], order[index]
            elif direction == "down" and index < len(order) - 1:
                order[index], order[index + 1] = order[index + 1], order[index]
            st.session_state["order"] = order

        def delete_row(index):
            """Delete a row."""
            save_state()
            order = st.session_state["order"]
            data = st.session_state["data"]
            row_to_remove = order.pop(index)
            st.session_state["data"] = data.drop(row_to_remove).reset_index(drop=True)
            st.session_state["order"] = list(range(len(st.session_state["data"])))

        def undo():
            """Undo the last action."""
            if st.session_state["history"]:
                state = st.session_state["history"].pop()
                st.session_state["redo_stack"].append(
                    {"data": st.session_state["data"], "order": st.session_state["order"]}
                )
                st.session_state["data"] = state["data"]
                st.session_state["order"] = state["order"]

        def redo():
            """Redo the last undone action."""
            if st.session_state["redo_stack"]:
                state = st.session_state["redo_stack"].pop()
                st.session_state["history"].append(
                    {"data": st.session_state["data"], "order": st.session_state["order"]}
                )
                st.session_state["data"] = state["data"]
                st.session_state["order"] = state["order"]

        # UI Components
        st.write("Reorder rows, delete them, or undo/redo actions:")

        # Undo/Redo Buttons
        col1, col2, col3 = st.columns([0.2, 1.4, 10])
        with col2:
            if st.button("Undo", disabled=not st.session_state["history"]):
                undo()
        with col3:
            if st.button("Redo", disabled=not st.session_state["redo_stack"]):
                redo()

        # Reorder the dataframe based on the order column
        ordered_data = st.session_state["data"].iloc[st.session_state["order"]].reset_index(drop=True)

        with st.container(border=True):
            # Display the table with buttons
            for i, row in ordered_data.iterrows():
                with st.container(border=True):
                    cols = st.columns([0.5, 0.5, 0.5, 5, 1.1])
                    with cols[0]:  # Up/Down Buttons
                        if st.button("↑", key=f"up_{i}"):
                            move_row(i, "up")
                    with cols[1]:
                        if st.button("↓", key=f"down_{i}"):
                            move_row(i, "down")
                    with cols[3]:
                        st.write(row["Name"], row["Age"])
                    with cols[4]:  # Delete Button
                        if st.button("Delete", key=f"delete_{i}"):
                            delete_row(i)

        # Undo/Redo Buttons
        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
        with col2:
            if st.button("Go Back"):
                pass
        with col3:
            if st.button("Add Detail"):
                pass
        with col4:
            if st.button("Fill Outline"):
                pass

    ###############



# PART 3: Download Markdown File
def part_3():
    st.subheader("Final Markdown")
    final_md = generate_markdown(st.session_state['inputs'])
    st.markdown(final_md)

    # Download button
    st.download_button(
        label="Download Markdown",
        data=final_md,
        file_name="output.md",
        mime="text/markdown"
    )

# Main App
def main():
    part_1()
    part_2_6()
    part_2_5()
    # part_2_6()
    part_2()
    part_3()

if __name__ == "__main__":
    inject_css()
    main()
