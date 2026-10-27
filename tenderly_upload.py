import streamlit as st


def render_upload_section():
    st.header("📄 New Eligibility Check")

    tender_file = st.file_uploader(
        "Upload Tender Document",
        type=["pdf", "docx", "txt"]
    )

    evidence_files = st.file_uploader(
        "Upload Bidder Evidence Documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    return tender_file, evidence_files
