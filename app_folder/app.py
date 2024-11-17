import streamlit as st
import st_paywall
import pypandoc
import tempfile

st.markdown('u need to subscribe here')

st_paywall.add_auth(required=True)

#after authentication, the email and subscription status is stored in session state
st.write(st.session_state.email)
st.write(st.session_state.user_subscribed)

st.markdown('hi')
st.markdown('hi again')

st.markdown('## Upload your markdown document here:')

# UPLOAD FILE(S)
uploaded_files = st.file_uploader(
    "Choose a Markdown file", accept_multiple_files=True
)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    st.write("filename:", uploaded_file.name)

# # # CONVERT TO PDF
# def markdown_to_pdf(input_file_path, output_file_path):
#     pypandoc.convert_file(input_file_path, "pdf", outputfile=output_file_path)
#     return 

# if uploaded_files:
#     output_file_path = uploaded_file.name + "_as_pdf.pdf"
#     markdown_to_pdf(..., output_file_path)

# CONVERT TO PDF
def markdown_to_pdf(input_file_content, output_file_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp_input_file:
        # Write the uploaded file content to a temporary file
        temp_input_file.write(input_file_content)
        temp_input_file_path = temp_input_file.name
    
    # Convert the temporary file to PDF
    pypandoc.convert_file(temp_input_file_path, "pdf", outputfile=output_file_path, extra_args=["--pdf-engine=xelatex"])


if uploaded_files:
    for uploaded_file in uploaded_files:
        # Generate output file path
        output_file_path = uploaded_file.name + "_as_pdf.pdf"

        # Call the conversion function
        markdown_to_pdf(uploaded_file.read(), output_file_path)

        # Show download link for the converted PDF
        st.write(f"Converted PDF for {uploaded_file.name}:")
        with open(output_file_path, "rb") as pdf_file:
            st.download_button(
                label="Download PDF",
                data=pdf_file,
                file_name=output_file_path,
                mime="application/pdf",
            )


# st.markdown('## Download your pdf here:')

# if uploaded_files:
#     st.download_button(
#         label="Download data as PDF",
#         data=output_file_path,
#         file_name=output_file_path,
#         mime="pdf",
#     )



# # Cache the function that retrieves user subscription data.
# @st.cache_data
# def retrieve_user_data():
#     # Simulate fetching authenticated user email and subscription status
#     # Replace with actual retrieval logic if needed.
#     email = st.session_state.get("email", None)
#     subscribed = st.session_state.get("user_subscribed", None)
#     return email, subscribed

# # Authenticate the user
# add_auth(
#     required=True,
#     login_button_text="Login with Google",
#     login_button_color="#FD504D",
#     login_sidebar=True,
# )

# st.write("Congrats, you are subscribed!")
# st.write("the email of the user is " + str(st.session_state.email))

# # Retrieve user data (cached)
# user_email, user_subscribed = retrieve_user_data()

# # Display the cached session state information
# st.write(user_email)
# st.write(user_subscribed)
