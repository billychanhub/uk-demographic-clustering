from pathlib import Path
from typing import Optional, Tuple

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
FULL_OUTPUT_PATH = OUTPUT_DIR / "msoa_layer_2_opportunity_scores.csv"
KEY_OUTPUT_PATH = OUTPUT_DIR / "merlin_key_recommendation_output.csv"

MERLIN_PURPLE = "#2b1055"
MERLIN_BLUE = "#1155cc"
MERLIN_AQUA = "#23b6e6"
MERLIN_GOLD = "#ffd84d"
MERLIN_INK = "#15172f"
MERLIN_MIST = "#f5f7ff"

TIER_ORDER = [
    "Priority 1 - strongest opportunity",
    "Priority 2 - strong opportunity",
    "Priority 3 - selective opportunity",
    "Priority 4 - monitor / niche",
]

TIER_COLOURS = {
    "Priority 1 - strongest opportunity": MERLIN_GOLD,
    "Priority 2 - strong opportunity": MERLIN_AQUA,
    "Priority 3 - selective opportunity": MERLIN_BLUE,
    "Priority 4 - monitor / niche": "#8c7aa9",
}


st.set_page_config(
    page_title="Merlin UK Opportunity Explorer",
    layout="wide",
)


st.markdown(
    f"""
    <style>
    :root {{
        --merlin-purple: {MERLIN_PURPLE};
        --merlin-blue: {MERLIN_BLUE};
        --merlin-aqua: {MERLIN_AQUA};
        --merlin-gold: {MERLIN_GOLD};
        --merlin-ink: {MERLIN_INK};
        --merlin-mist: {MERLIN_MIST};
    }}

    .stApp {{
        background: linear-gradient(180deg, #ffffff 0%, #f7f5ff 42%, #ffffff 100%);
        color: var(--merlin-ink);
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #230943 0%, #2b1055 58%, #111a4b 100%);
    }}

    [data-testid="stSidebar"] * {{
        color: #ffffff;
    }}

    .hero {{
        background: linear-gradient(135deg, #2b1055 0%, #1f3a93 58%, #23b6e6 118%);
        border-radius: 8px;
        padding: 28px 32px;
        color: #ffffff;
        margin-bottom: 18px;
        box-shadow: 0 18px 42px rgba(43, 16, 85, 0.22);
        position: relative;
        overflow: hidden;
    }}

    .hero:after {{
        content: "";
        position: absolute;
        width: 120px;
        height: 120px;
        right: 30px;
        top: 26px;
        background:
            linear-gradient(90deg, transparent 48%, rgba(255, 216, 77, 0.95) 49%, rgba(255, 216, 77, 0.95) 51%, transparent 52%),
            linear-gradient(0deg, transparent 48%, rgba(255, 216, 77, 0.9) 49%, rgba(255, 216, 77, 0.9) 51%, transparent 52%);
        transform: rotate(22deg);
        opacity: 0.8;
    }}

    .hero h1 {{
        font-size: 2.2rem;
        line-height: 1.05;
        margin: 0 0 8px 0;
        letter-spacing: 0;
    }}

    .hero p {{
        max-width: 760px;
        margin: 0;
        color: rgba(255, 255, 255, 0.84);
        font-size: 1rem;
    }}

    .metric-card {{
        background: #ffffff;
        border: 1px solid rgba(43, 16, 85, 0.12);
        border-radius: 8px;
        padding: 18px 18px 16px 18px;
        min-height: 118px;
        box-shadow: 0 12px 28px rgba(43, 16, 85, 0.08);
        border-top: 4px solid var(--accent);
    }}

    .metric-label {{
        color: #5a5372;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-bottom: 8px;
    }}

    .metric-value {{
        color: var(--merlin-purple);
        font-size: 1.78rem;
        line-height: 1.05;
        font-weight: 800;
    }}

    .metric-note {{
        margin-top: 8px;
        color: #6e6882;
        font-size: 0.82rem;
    }}

    .section-panel {{
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid rgba(43, 16, 85, 0.10);
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 10px 26px rgba(43, 16, 85, 0.06);
    }}

    div[data-testid="stMetric"] {{
        background: #ffffff;
        border-radius: 8px;
        padding: 14px;
        border: 1px solid rgba(43, 16, 85, 0.10);
    }}

    h2, h3 {{
        color: var(--merlin-purple);
        letter-spacing: 0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    if FULL_OUTPUT_PATH.exists():
        data = pd.read_csv(FULL_OUTPUT_PATH)
    else:
        data = pd.read_csv(KEY_OUTPUT_PATH)

    data = data.sort_values("opportunity_rank").reset_index(drop=True)
    data["area_name"] = data["geo_name"].str.replace(r"\s+\d+$", "", regex=True)
    data["priority_1_flag"] = data.get("opportunity_tier", "").eq("Priority 1 - strongest opportunity")
    return data


def compact_number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}m"
    if value >= 1_000:
        return f"{value / 1_000:.0f}k"
    return f"{value:,.0f}"


def metric_card(label: str, value: str, note: str, accent: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card" style="--accent:{accent};">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_table(data: pd.DataFrame, rows: int = 10) -> pd.DataFrame:
    preferred_columns = [
        "opportunity_rank",
        "geo_name",
        "segment_label",
        "overall_opportunity_score",
        "key_contributing_driver",
        "recommended_attraction_name",
        "recommended_product_focus",
    ]
    optional_columns = [
        "recommended_activation",
        "recommended_attraction_category",
        "recommended_attraction_distance_km",
    ]
    columns = [column for column in preferred_columns + optional_columns if column in data.columns]
    return data.loc[:, columns].head(rows)


def find_matching_attraction(data: pd.DataFrame, question: str) -> Optional[str]:
    question_lower = question.lower()
    attraction_columns = [
        column
        for column in [
            "recommended_attraction_name",
            "recommended_attraction_brand",
            "recommended_attraction_category",
            "recommended_attraction_focus",
        ]
        if column in data.columns
    ]
    matches = []
    for column in attraction_columns:
        for value in data[column].dropna().unique():
            value_lower = str(value).lower()
            if value_lower in question_lower or any(part in question_lower for part in value_lower.split()):
                matches.append(str(value))
    if not matches:
        return None
    return sorted(matches, key=len, reverse=True)[0]


def answer_question(question: str, data: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
    question_lower = question.lower().strip()

    if not question_lower:
        return "Ask a question about opportunity areas, attractions, segments, or activation.", data.head(0)

    filtered = data.copy()
    title = "Top opportunity MSOAs"

    attraction = find_matching_attraction(data, question_lower)
    if attraction:
        attraction_mask = pd.Series(False, index=filtered.index)
        for column in [
            "recommended_attraction_name",
            "recommended_attraction_brand",
            "recommended_attraction_category",
            "recommended_attraction_focus",
        ]:
            if column in filtered.columns:
                attraction_mask = attraction_mask | filtered[column].astype(str).str.contains(attraction, case=False, na=False, regex=False)
        filtered = filtered.loc[attraction_mask]
        title = f"Highest opportunity areas for {attraction}"

    if "annual pass" in question_lower:
        filtered = filtered.loc[
            filtered["recommended_product_focus"].astype(str).str.contains("annual pass", case=False, na=False)
        ]
        title = "Best opportunities for annual pass propositions"

    if "family" in question_lower:
        filtered = filtered.loc[
            filtered["segment_label"].astype(str).str.contains("family|suburban", case=False, na=False)
            | filtered["recommended_product_focus"].astype(str).str.contains("family", case=False, na=False)
        ]
        title = "Best family-led opportunities"

    if "priority 1" in question_lower or "strongest" in question_lower:
        if "opportunity_tier" in filtered.columns:
            filtered = filtered.loc[filtered["opportunity_tier"].eq("Priority 1 - strongest opportunity")]
        title = f"{title}: Priority 1 only"

    area_matches = [
        area
        for area in data["area_name"].dropna().unique()
        if str(area).lower() in question_lower
    ]
    if area_matches:
        area = sorted(area_matches, key=len, reverse=True)[0]
        filtered = data.loc[data["area_name"].eq(area)]
        title = f"Highest opportunity MSOAs in {area}"

    if "underpenetrated" in question_lower:
        response = (
            "This public-data model cannot prove underpenetration because it does not include Merlin customer penetration. "
            "As a practical proxy, review high-scoring areas and validate them against internal booking, CRM, and passholder data."
        )
        return response, format_table(filtered, 10)

    if "segment" in question_lower and not attraction:
        summary = (
            filtered.groupby("segment_label", as_index=False)
            .agg(
                msoa_count=("geo_code", "count"),
                mean_opportunity_score=("overall_opportunity_score", "mean"),
                best_rank=("opportunity_rank", "min"),
            )
            .sort_values(["best_rank", "mean_opportunity_score"], ascending=[True, False])
        )
        return "Segments ranked by their strongest opportunity areas.", summary.head(10)

    if filtered.empty:
        return "I could not find matching rows. Try an attraction, place, segment, or phrase such as annual pass.", data.head(0)

    response = f"{title}. Showing the highest-ranked matching MSOAs."
    return response, format_table(filtered.sort_values("opportunity_rank"), 10)


def tier_headroom_chart(data: pd.DataFrame) -> alt.Chart:
    headroom = (
        data.groupby("opportunity_tier", as_index=False)
        .agg(total_population=("total_population", "sum"), msoa_count=("geo_code", "count"))
        .assign(opportunity_tier=lambda frame: pd.Categorical(frame["opportunity_tier"], TIER_ORDER, ordered=True))
        .sort_values("opportunity_tier")
    )
    headroom["population_millions"] = headroom["total_population"] / 1_000_000

    return (
        alt.Chart(headroom)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X("population_millions:Q", title="Addressable population, millions"),
            y=alt.Y("opportunity_tier:N", sort=TIER_ORDER, title=""),
            color=alt.Color(
                "opportunity_tier:N",
                scale=alt.Scale(domain=TIER_ORDER, range=[TIER_COLOURS[tier] for tier in TIER_ORDER]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("opportunity_tier:N", title="Tier"),
                alt.Tooltip("msoa_count:Q", title="MSOAs", format=","),
                alt.Tooltip("population_millions:Q", title="Population, m", format=".2f"),
            ],
        )
        .properties(height=210)
    )


def area_bar_chart(data: pd.DataFrame) -> alt.Chart:
    area_summary = (
        data.groupby("area_name", as_index=False)
        .agg(
            priority_1_msoas=("priority_1_flag", "sum"),
            mean_score=("overall_opportunity_score", "mean"),
            best_rank=("opportunity_rank", "min"),
            total_population=("total_population", "sum"),
        )
        .sort_values(["priority_1_msoas", "mean_score", "total_population"], ascending=[False, False, False])
        .head(12)
    )
    area_summary["label"] = area_summary["area_name"]

    return (
        alt.Chart(area_summary)
        .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
        .encode(
            x=alt.X("priority_1_msoas:Q", title="Priority 1 MSOAs"),
            y=alt.Y("label:N", sort="-x", title=""),
            color=alt.value(MERLIN_AQUA),
            tooltip=[
                alt.Tooltip("area_name:N", title="Area"),
                alt.Tooltip("priority_1_msoas:Q", title="Priority 1 MSOAs"),
                alt.Tooltip("mean_score:Q", title="Mean score", format=".1f"),
                alt.Tooltip("best_rank:Q", title="Best rank", format=","),
                alt.Tooltip("total_population:Q", title="Population", format=","),
            ],
        )
        .properties(height=330)
    )


def segment_mix_chart(data: pd.DataFrame) -> alt.Chart:
    segment_summary = (
        data.groupby("segment_label", as_index=False)
        .agg(msoa_count=("geo_code", "count"), mean_score=("overall_opportunity_score", "mean"))
        .sort_values("msoa_count", ascending=False)
    )

    return (
        alt.Chart(segment_summary)
        .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
        .encode(
            x=alt.X("msoa_count:Q", title="MSOAs"),
            y=alt.Y("segment_label:N", sort="-x", title=""),
            color=alt.value(MERLIN_PURPLE),
            tooltip=[
                alt.Tooltip("segment_label:N", title="Segment"),
                alt.Tooltip("msoa_count:Q", title="MSOAs", format=","),
                alt.Tooltip("mean_score:Q", title="Mean score", format=".1f"),
            ],
        )
        .properties(height=260)
    )


df = load_data()
top_attraction = (
    df.groupby("recommended_attraction_name")["priority_1_flag"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)

st.markdown(
    """
    <div class="hero">
        <h1>Merlin UK Opportunity Explorer</h1>
        <p>Attraction-led view of the strongest MSOA opportunities, designed for executive prioritisation and media activation planning.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Attraction Focus")
    attraction_options = sorted(df["recommended_attraction_name"].dropna().unique().tolist())
    default_index = attraction_options.index(top_attraction) if top_attraction in attraction_options else 0
    selected_attraction = st.selectbox("Merlin attraction", attraction_options, index=default_index)

    segment_options = ["All segments"] + sorted(df["segment_label"].dropna().unique().tolist())
    selected_segment = st.selectbox("Customer segment", segment_options)

    search_text = st.text_input("Search geography")
    max_rank = int(df["opportunity_rank"].max())
    rank_limit = st.slider("Include opportunity ranks up to", 1, max_rank, min(1000, max_rank))

selected_df = df.loc[df["recommended_attraction_name"].eq(selected_attraction)].copy()
filtered_df = selected_df.loc[selected_df["opportunity_rank"].le(rank_limit)].copy()
if selected_segment != "All segments":
    filtered_df = filtered_df.loc[filtered_df["segment_label"].eq(selected_segment)]
if search_text:
    filtered_df = filtered_df.loc[filtered_df["geo_name"].str.contains(search_text, case=False, na=False)]

selected_brand = selected_df["recommended_attraction_brand"].mode().iat[0] if "recommended_attraction_brand" in selected_df else selected_attraction
selected_category = selected_df["recommended_attraction_category"].mode().iat[0] if "recommended_attraction_category" in selected_df else "Attraction"

st.subheader(selected_attraction)
st.caption(f"{selected_brand} | {selected_category}")

priority_1 = selected_df.loc[selected_df["priority_1_flag"]]
priority_1_population = priority_1["total_population"].sum()
selected_population = selected_df["total_population"].sum()
best_rank = int(selected_df["opportunity_rank"].min())
mean_score = selected_df["overall_opportunity_score"].mean()
median_distance = selected_df["recommended_attraction_distance_km"].median() if "recommended_attraction_distance_km" in selected_df else None

metric_cols = st.columns(5)
with metric_cols[0]:
    metric_card("Priority 1 MSOAs", f"{len(priority_1):,}", "Strongest activation shortlist", MERLIN_GOLD)
with metric_cols[1]:
    metric_card("Priority 1 population", compact_number(priority_1_population), "Immediate headroom to validate", MERLIN_AQUA)
with metric_cols[2]:
    metric_card("Total opportunity population", compact_number(selected_population), "All MSOAs aligned to attraction", MERLIN_BLUE)
with metric_cols[3]:
    metric_card("Best national rank", f"#{best_rank:,}", "Best matching MSOA", MERLIN_PURPLE)
with metric_cols[4]:
    distance_note = f"Median recommended distance {median_distance:.0f} km" if median_distance is not None else "Distance not available"
    metric_card("Mean score", f"{mean_score:.1f}", distance_note, "#7b61ff")

chart_col, map_col = st.columns([1.08, 0.92])
with chart_col:
    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader("Growth Headroom by Opportunity Tier")
    st.altair_chart(tier_headroom_chart(selected_df), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with map_col:
    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader("Opportunity Map")
    map_df = filtered_df.loc[:, ["latitude", "longitude", "overall_opportunity_score"]].dropna().head(1200)
    if map_df.empty:
        st.info("No matching MSOAs for the current filters.")
    else:
        st.map(map_df.rename(columns={"latitude": "lat", "longitude": "lon"}))
    st.markdown("</div>", unsafe_allow_html=True)

area_col, segment_col = st.columns([1.1, 0.9])
with area_col:
    st.subheader("Highest Opportunity Local Markets")
    st.altair_chart(area_bar_chart(selected_df), use_container_width=True)

with segment_col:
    st.subheader("Customer Segment Mix")
    st.altair_chart(segment_mix_chart(selected_df), use_container_width=True)

st.subheader("Ranked MSOA Opportunities")
st.dataframe(format_table(filtered_df.sort_values("opportunity_rank"), 50), use_container_width=True, hide_index=True)

st.subheader("Lightweight Data Assistant")
st.caption("Ask a business question about attractions, segments, geographies, or activation.")

example_questions = [
    "Which areas are highest opportunity for LEGOLAND?",
    "Where should Merlin target family annual passes?",
    "Which MSOAs are highest opportunity in Birmingham?",
    "Which segments have the strongest opportunity?",
    "Which regions appear underpenetrated?",
]

question_cols = st.columns(len(example_questions))
for col, example in zip(question_cols, example_questions):
    if col.button(example):
        st.session_state["current_question"] = example

question = st.chat_input("Ask about attractions, segments, geographies, or activation")
if question:
    st.session_state["current_question"] = question

current_question = st.session_state.get("current_question")
if current_question:
    with st.chat_message("user"):
        st.write(current_question)
    answer, answer_df = answer_question(current_question, df)
    with st.chat_message("assistant"):
        st.write(answer)
        if not answer_df.empty:
            st.dataframe(answer_df, use_container_width=True, hide_index=True)
