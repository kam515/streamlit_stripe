import streamlit as st
import st_paywall

st.markdown('u need to subscribe here')

st_paywall.add_auth(required=True)

#after authentication, the email and subscription status is stored in session state
st.write(st.session_state.email)
st.write(st.session_state.user_subscribed)

st.markdown('hi')
st.markdown('hi again')

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
