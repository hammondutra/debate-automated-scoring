from __future__ import annotations

import streamlit as st

from debate_scoring.engine import run_tournament
from debate_scoring.io import export_excel, load_dataframe, template_dataframe

st.set_page_config(page_title="Debate Automated Scoring", page_icon="🏛️", layout="wide")

st.title("Debate Automated Scoring")
st.caption("Upload tournament results, validate the data, and export team and speaker rankings.")

format_label = st.selectbox(
    "Tournament format",
    ["TBDEM / WSDC-style", "WUDC / British Parliamentary"],
)
format_name = "tbdem" if format_label.startswith("TBDEM") else "wudc"

template = template_dataframe(format_name).to_csv(index=False).encode("utf-8")
st.download_button(
    "Download input template",
    data=template,
    file_name=f"{format_name}_template.csv",
    mime="text/csv",
)

uploaded = st.file_uploader("Upload completed CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded is None:
    st.info(
        "Start with the template above. English and common Portuguese column names "
        "are accepted."
    )
else:
    try:
        data = load_dataframe(uploaded, filename=uploaded.name)
        st.subheader("Input preview")
        st.dataframe(data.head(50), use_container_width=True)

        if st.button("Calculate rankings", type="primary"):
            result = run_tournament(data, format_name)
            for warning in result.warnings:
                st.warning(warning)

            team_tab, speaker_tab, round_tab, reply_tab = st.tabs(
                ["Teams", "Speakers", "Round results", "Reply speeches"]
            )
            with team_tab:
                st.dataframe(result.team_rankings, use_container_width=True)
            with speaker_tab:
                st.dataframe(result.speaker_rankings, use_container_width=True)
            with round_tab:
                st.dataframe(result.round_results, use_container_width=True)
            with reply_tab:
                if result.reply_rankings.empty:
                    st.info("This format/run has no separate reply-speech ranking.")
                else:
                    st.dataframe(result.reply_rankings, use_container_width=True)

            st.download_button(
                "Download results workbook",
                data=export_excel(result),
                file_name="debate_rankings.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    except Exception as exc:
        st.error(str(exc))
