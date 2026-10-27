import streamlit as st
from tenderly_database import register_user, login_user


def render_auth_page():
    st.markdown("""
        <div style='text-align:center; padding:20px;'>
            <h1>🔐 Welcome to Tenderly</h1>
            <p style='font-size:18px;'>AI-Based Government Tender Eligibility & Evidence Matching System</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

    with tab1:
        st.subheader("Sign In")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Sign In", type="primary", use_container_width=True):
            if not email or not password:
                st.error("Please enter email and password.")
            else:
                user = login_user(email, password)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    with tab2:
        st.subheader("Create Account")
        full_name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        organization = st.text_input("Organization", key="signup_organization")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Sign Up", type="primary", use_container_width=True):
            if not full_name or not email or not password:
                st.error("Please fill all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success, message = register_user(full_name, email, organization, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
