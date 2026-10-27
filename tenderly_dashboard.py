import streamlit as st
from tenderly_database import get_user_statistics, get_user_checks


def render_dashboard(user):
    st.header("📊 Dashboard")

    stats = get_user_statistics(user["id"])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Checks", stats["total_checks"])
    with col2:
        st.metric("Eligible", stats["eligible"])
    with col3:
        st.metric("Not Eligible", stats["not_eligible"])
    with col4:
        st.metric("Average Score", f"{stats['average_score'] * 100:.1f}%")

    st.subheader("👤 Profile Details")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Name:** {user['full_name']}")
        st.info(f"**Email:** {user['email']}")

    with col2:
        st.info(f"**Organization:** {user['organization'] or 'Not provided'}")
        st.info("**Role:** Bidder / Tender Analyst")

    st.subheader("📁 Recent Eligibility Checks")

    checks = get_user_checks(user["id"])

    if checks.empty:
        st.info("No eligibility checks yet. Start by running a new check.")
    else:
        checks["eligibility_score"] = checks["eligibility_score"].apply(
            lambda value: f"{value * 100:.1f}%"
        )
        st.dataframe(checks, use_container_width=True)
