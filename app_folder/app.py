import streamlit as st

from st_paywall import add_auth

# add_auth(required=True)

# #after authentication, the email and subscription status is stored in session state
# st.write(st.session_state.email)
# st.write(st.session_state.user_subscribed)

# st.markdown('hi')

st.set_page_config(layout="wide")
st.title("Katie's Subscription app POC")

add_auth(
    required=True,
    login_button_text="Login with Google",
    login_button_color="#FD504D",
    login_sidebar=True,
)

st.balloons()
st.write("Congrats, you are subscribed!")
st.write("the email of the user is " + str(st.session_state.email))
