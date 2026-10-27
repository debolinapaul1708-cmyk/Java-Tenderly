import streamlit as st


def render_report_section(results_df, eligibility_score, verdict):
    st.header("📋 Eligibility Report")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Eligibility Score", f"{eligibility_score * 100:.1f}%")
    with col2:
        st.metric("Final Verdict", verdict)
    with col3:
        st.metric("Clauses Checked", len(results_df))

    if verdict == "Eligible":
        st.success("✅ The bidder appears eligible based on the uploaded evidence.")
    elif verdict == "Partially Eligible":
        st.warning("⚠️ Some eligibility requirements are partially matched.")
    else:
        st.error("❌ The bidder does not meet the eligibility requirements.")

    st.subheader("Clause-Level Gap Report")
    st.dataframe(results_df, use_container_width=True)

    missing = results_df[results_df["Status"] == "Missing"]
    if not missing.empty:
        st.subheader("❌ Missing Requirements")
        for _, row in missing.iterrows():
            st.error(f"**{row['Type']}**: {row['Clause']}")

    partial = results_df[results_df["Status"] == "Partial"]
    if not partial.empty:
        st.subheader("⚠️ Partially Matched Requirements")
        for _, row in partial.iterrows():
            st.warning(f"**{row['Type']}**: {row['Clause']}")

    csv = results_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Gap Report",
        data=csv,
        file_name="tenderly_gap_report.csv",
        mime="text/csv",
        use_container_width=True
    )
