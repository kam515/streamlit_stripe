import streamlit as st
from st_paywall import add_auth

st.markdown('hi')

# Cache the function that retrieves user subscription data.
@st.cache_data
def retrieve_user_data():
    # Simulate fetching authenticated user email and subscription status
    # Replace with actual retrieval logic if needed.
    email = st.session_state.get("email", None)
    subscribed = st.session_state.get("user_subscribed", None)
    return email, subscribed

# Authenticate the user
add_auth(
    required=True,
    login_button_text="Login with Google",
    login_button_color="#FD504D",
    login_sidebar=True,
)

st.write("Congrats, you are subscribed!")
st.write("the email of the user is " + str(st.session_state.email))

# After successful authentication, set the email and subscription status in session state
if "email" not in st.session_state or "user_subscribed" not in st.session_state:
    # Replace with actual logic for setting authenticated values
    st.session_state.email = "user@example.com"  # Example authenticated email
    st.session_state.user_subscribed = True  # Example subscription status

# Retrieve user data (cached)
user_email, user_subscribed = retrieve_user_data()

# Display the cached session state information
st.write(user_email)
st.write(user_subscribed)
