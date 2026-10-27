import streamlit as st

from tenderly_auth import render_auth_page
from tenderly_dashboard import render_dashboard
from tenderly_database import create_tables, save_check, get_user_checks
from tenderly_upload import render_upload_section
from tenderly_report import render_report_section
from tenderly_text_extractor import extract_text_from_file
from tenderly_clause_extractor import extract_clauses
from tenderly_scorer import calculate_results
from tenderly_settings import APP_NAME, DEFAULT_WEIGHTS

st.set_page_config(
    page_title="Tenderly",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_tables()

if "user" not in st.session_state:
    st.session_state["user"] = None

if "weights" not in st.session_state:
    st.session_state["weights"] = DEFAULT_WEIGHTS.copy()

user = st.session_state["user"]

if user is None:
    render_auth_page()
    st.stop()

with st.sidebar:
    st.title(f"📄 {APP_NAME}")
    st.success(f"Welcome, {user['full_name']}")

    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📄 New Check", "📁 Check History", "⚙️ Settings"]
    )

    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state["user"] = None
        st.rerun()

if page == "📊 Dashboard":
    render_dashboard(user)

elif page == "📄 New Check":
    tender_file, evidence_files = render_upload_section()

    st.subheader("⚙️ Scoring Weights")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        turnover_weight = st.slider("Turnover Weight", 0, 100, st.session_state["weights"]["TURNOVER"])
    with col2:
        experience_weight = st.slider("Experience Weight", 0, 100, st.session_state["weights"]["EXPERIENCE"])
    with col3:
        cert_weight = st.slider("Certification Weight", 0, 100, st.session_state["weights"]["CERT"])
    with col4:
        project_weight = st.slider("Past Projects Weight", 0, 100, st.session_state["weights"]["PROJECT"])

    weights = {
        "TURNOVER": turnover_weight,
        "EXPERIENCE": experience_weight,
        "CERT": cert_weight,
        "PROJECT": project_weight
    }

    if st.button("🚀 Run Eligibility Check", type="primary", use_container_width=True):
        if not tender_file:
            st.error("Please upload a tender document.")
            st.stop()

        if not evidence_files:
            st.error("Please upload at least one evidence document.")
            st.stop()

        try:
            with st.spinner("Extracting tender text..."):
                tender_text = extract_text_from_file(tender_file)
                clauses = extract_clauses(tender_text)
        except Exception as error:
            st.error(f"Could not process tender: {error}")
            st.stop()

        with st.spinner("Extracting evidence text..."):
            evidence_documents = []

            for evidence_file in evidence_files:
                try:
                    evidence_text = extract_text_from_file(evidence_file)
                    if evidence_text.strip():
                        evidence_documents.append({
                            "name": evidence_file.name,
                            "text": evidence_text
                        })
                except Exception:
                    st.warning(f"Could not read file: {evidence_file.name}")

        if not evidence_documents:
            st.error("No readable text found in evidence documents.")
            st.stop()

        with st.spinner("Matching clauses with evidence..."):
            results_df, eligibility_score, verdict = calculate_results(
                clauses, evidence_documents, weights
            )

        save_check(
            user["id"],
            tender_file.name,
            eligibility_score,
            verdict,
            len(results_df)
        )

        st.success("Eligibility check completed.")
        render_report_section(results_df, eligibility_score, verdict)

elif page == "📁 Check History":
    st.header("📁 Check History")

    checks = get_user_checks(user["id"])

    if checks.empty:
        st.info("No checks found yet.")
    else:
        checks["eligibility_score"] = checks["eligibility_score"].apply(
            lambda value: f"{value * 100:.1f}%"
        )
        st.dataframe(checks, use_container_width=True)

        csv = checks.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Check History",
            data=csv,
            file_name="tenderly_check_history.csv",
            mime="text/csv",
            use_container_width=True
        )

elif page == "⚙️ Settings":
    st.header("⚙️ Settings")

    st.subheader("👤 Account Details")
    st.info(f"**Name:** {user['full_name']}")
    st.info(f"**Email:** {user['email']}")
    st.info(f"**Organization:** {user['organization'] or 'Not provided'}")

    st.subheader("⚖️ Default Scoring Weights")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Turnover", st.session_state["weights"]["TURNOVER"])
        st.metric("Certification", st.session_state["weights"]["CERT"])

    with col2:
        st.metric("Experience", st.session_state["weights"]["EXPERIENCE"])
        st.metric("Past Projects", st.session_state["weights"]["PROJECT"])

    if st.button("♻️ Reset Weights", use_container_width=True):
        st.session_state["weights"] = DEFAULT_WEIGHTS.copy()
        st.rerun()
