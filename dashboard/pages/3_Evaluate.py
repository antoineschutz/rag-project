"""Evaluate page: chart existing benchmark runs (MLflow), or run a live evaluation.

Results are read from whatever tracking store mlflow resolves (shown in the page caption),
which is the same store scripts/benchmark.py logs to. Set MLFLOW_TRACKING_URI to point elsewhere.
"""

import os

import altair as alt
import mlflow
import pandas as pd
import streamlit as st

from api_client import APIError, demo_mode, get_presets, post_evaluate

# Must match src.evaluation.benchmark.EXPERIMENT_NAME.
EXPERIMENT_NAME = "rag-benchmark"
# Default must match src.config.env.MLFLOW_TRACKING_URI (the store benchmark.py writes to).
mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///var/mlflow.db"))

st.title("Evaluate")

if demo_mode():
    st.info(
        "Evaluation isn't available in the hosted demo: there's no MLflow store in the image, and "
        "a live run makes ~29 slow LLM calls (and the judge needs an OpenAI key). Clone the repo "
        "and run it locally:\n\n```\npython scripts/benchmark.py --config best\n```"
    )
    st.stop()

# --- Existing results -------------------------------------------------------------------
st.subheader("Benchmark results")
st.caption(f"Reading the '{EXPERIMENT_NAME}' experiment from {mlflow.get_tracking_uri()}")

try:
    runs = mlflow.search_runs(experiment_names=[EXPERIMENT_NAME])
except Exception:  # noqa: BLE001 - missing experiment / store; treat as no runs
    runs = pd.DataFrame()

if runs.empty:
    st.info(
        "No benchmark runs found yet. Generate some with "
        "`python scripts/benchmark.py --config best --judge`, or use the live run below."
    )
else:
    # Keep the most recent run per config (search_runs is newest-first), best accuracy first.
    latest = (
        runs.drop_duplicates(subset="params.config_name", keep="first")
        .set_index("params.config_name")
        .sort_values("metrics.accuracy_29", ascending=False)
    )

    # Accuracy is logged as a 0..1 fraction; show it as a percentage.
    table = pd.DataFrame(index=latest.index)
    table["keyword accuracy"] = latest["metrics.accuracy_29"] * 100
    if "metrics.score_judge" in latest:
        table["LLM judge"] = latest["metrics.score_judge"] * 100
    table.index.name = "config"

    # Grouped (not stacked) bars, x ordered by keyword accuracy (table is already sorted).
    order = table.index.tolist()
    long = table.reset_index().melt(id_vars="config", var_name="metric", value_name="accuracy")
    chart = (
        alt.Chart(long)
        .mark_bar()
        .encode(
            x=alt.X("config:N", sort=order, title=None),
            xOffset="metric:N",
            y=alt.Y("accuracy:Q", title="accuracy (%)"),
            color=alt.Color("metric:N", title=None),
            tooltip=["config", "metric", alt.Tooltip("accuracy:Q", format=".1f")],
        )
    )
    st.caption("Accuracy by config (%, higher is better)")
    st.altair_chart(chart, width=True)
    st.caption(
        "The LLM judge is stricter than the keyword check (it catches keyword false positives), "
        "so its scores usually sit a little below keyword accuracy."
    )

    st.dataframe(
        table.reset_index(),
        hide_index=True,
        width=True,
        column_config={
            "keyword accuracy": st.column_config.NumberColumn(format="%.1f%%"),
            "LLM judge": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

# --- Live run ---------------------------------------------------------------------------
st.divider()
st.subheader("Run a live evaluation")
st.caption("Scores a preset over the QA set via the API. Cached answers serve instantly; an uncached run can take minutes.")

try:
    presets = get_presets()
except APIError as exc:
    st.error(str(exc))
    st.stop()

preset = st.selectbox("Preset", sorted(presets))
judge = st.checkbox("LLM judge (independent gpt-4o-mini; needs OPENAI_API_KEY, ~29 API calls)")

if st.button("Run live", type="primary"):
    try:
        with st.spinner(f"Evaluating '{preset}'..."):
            report = post_evaluate(preset, config=None, fresh=False, judge=judge)
    except APIError as exc:
        st.error(str(exc))
        st.stop()

    m1, m2, m3 = st.columns(3)
    m1.metric("accuracy_29", f"{report['accuracy_29']:.1%}", f"{report['correct']}/{report['n_scored']}")
    if report.get("score_judge") is not None:
        m2.metric("score_judge", f"{report['score_judge']:.1%}")
        m3.metric("keyword/judge disagreements", report["judge_disagreements"])

    results = pd.DataFrame(report["results"])
    show = [c for c in ["id", "level", "correct", "judge", "question"] if c in results]
    st.dataframe(results[show], hide_index=True, width=True)
