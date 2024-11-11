import streamlit as st

from st_paywall import add_auth

add_auth(
    required=True,
)
st.write(st.session_state.email)
st.write(st.session_state.user_subscribed)
st.balloons()
st.write("Congrats, you are subscribed!")
st.write("the email of the user is " + str(st.session_state.email))
