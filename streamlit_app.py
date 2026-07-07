from pathlib import Path
from typing import Optional

import altair as alt
import pandas as pd
import pydeck as pdk
import requests
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FULL_OUTPUT_PATH = OUTPUT_DIR / "msoa_layer_2_opportunity_scores.csv"
ATTRACTION_PATH = PROCESSED_DIR / "merlin_attraction_data.csv"
FACT_SHEET_PATH = OUTPUT_DIR / "merlin_project_fact_sheet.md"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
OPENAI_CHAT_MODEL = "gpt-5.4-nano"

MERLIN_PURPLE = "#2b1055"
MERLIN_BLUE = "#1155cc"
MERLIN_AQUA = "#23b6e6"
MERLIN_GOLD = "#ffd84d"
MERLIN_INK = "#15172f"
MERLIN_MIST = "#f5f7ff"
REVENUE_PER_VISITOR_GBP = 33.0

PLAY_COLOURS = {
    "Multi-attraction cluster marketing": [35, 182, 230, 190],
    "Annual pass": [255, 138, 0, 195],
    "Short break": [123, 97, 255, 190],
    "Other": [130, 125, 155, 135],
}

PLAY_COLOURS_HEX = {
    "Multi-attraction cluster marketing": MERLIN_AQUA,
    "Annual pass": "#ff8a00",
    "Short break": "#7b61ff",
    "Other": "#827d9b",
}
PLAY_ORDER = ["Multi-attraction cluster marketing", "Annual pass", "Short break", "Other"]

CENTRAL_LONDON_LABEL_ATTRACTIONS = {
    "London Eye": "London Eye",
    "London Dungeon": "Dungeons",
    "Shrek's Adventure! London": "Shrek's",
    "SEA LIFE London Aquarium": "SEA LIFE",
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
        background: linear-gradient(180deg, #ffffff 0%, #f7f5ff 45%, #ffffff 100%);
        color: var(--merlin-ink);
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #230943 0%, #2b1055 58%, #111a4b 100%);
    }}

    [data-testid="stSidebar"] * {{
        color: #ffffff;
    }}

    [data-testid="stSidebar"] div[data-baseweb="select"] *,
    [data-testid="stSidebar"] div[data-baseweb="input"] *,
    [data-testid="stSidebar"] div[data-baseweb="popover"] * {{
        color: var(--merlin-ink) !important;
    }}

    [data-testid="stSidebar"] div[data-baseweb="tag"] {{
        background-color: var(--merlin-gold);
    }}

    [data-testid="stSidebar"] div[data-baseweb="tag"] * {{
        color: var(--merlin-purple) !important;
        font-weight: 700;
    }}

    [data-testid="stSidebar"] button {{
        background-color: #ffffff !important;
        border: 1px solid rgba(255, 216, 77, 0.65) !important;
    }}

    [data-testid="stSidebar"] button * {{
        color: var(--merlin-purple) !important;
        font-weight: 800;
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
        max-width: 860px;
        margin: 0;
        color: rgba(255, 255, 255, 0.84);
        font-size: 1rem;
    }}

    .metric-card {{
        background: #ffffff;
        border: 1px solid rgba(43, 16, 85, 0.12);
        border-radius: 8px;
        padding: 16px 15px 14px 15px;
        min-height: 154px;
        height: auto;
        box-shadow: 0 12px 28px rgba(43, 16, 85, 0.08);
        border-top: 4px solid var(--accent);
        box-sizing: border-box;
        overflow: visible;
    }}

    .metric-label {{
        color: #5a5372;
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-bottom: 8px;
    }}

    .metric-value {{
        color: var(--merlin-purple);
        font-size: 1.38rem;
        line-height: 1.08;
        font-weight: 850;
        overflow-wrap: anywhere;
    }}

    .metric-note {{
        margin-top: 8px;
        color: #6e6882;
        font-size: 0.78rem;
        line-height: 1.22;
        overflow-wrap: anywhere;
    }}

    div[data-testid="stMetric"],
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] > div {{
        white-space: normal;
        overflow: visible;
        overflow-wrap: anywhere;
        text-overflow: clip;
        max-width: 100%;
        line-height: 1.08;
    }}

    .section-panel {{
        background: rgba(255, 255, 255, 0.90);
        border: 1px solid rgba(43, 16, 85, 0.10);
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 10px 26px rgba(43, 16, 85, 0.06);
    }}

    .map-legend {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px 18px;
        align-items: center;
        margin: 0 0 12px 0;
        color: var(--merlin-ink);
        font-size: 0.84rem;
    }}

    .legend-item {{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        white-space: nowrap;
    }}

    .legend-swatch {{
        width: 12px;
        height: 12px;
        border-radius: 999px;
        display: inline-block;
        border: 1px solid rgba(43, 16, 85, 0.35);
    }}

    .legend-attraction {{
        width: 18px;
        height: 18px;
        border-radius: 999px;
        display: inline-block;
        background: var(--merlin-gold);
        border: 2px solid var(--merlin-purple);
        color: var(--merlin-purple);
        font-size: 0.55rem;
        font-weight: 900;
        line-height: 15px;
        text-align: center;
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
def load_opportunity_data() -> pd.DataFrame:
    if not FULL_OUTPUT_PATH.exists():
        st.error(f"Full dashboard output is required but was not found: {FULL_OUTPUT_PATH}")
        st.stop()
    data = pd.read_csv(FULL_OUTPUT_PATH)

    data = data.sort_values("opportunity_rank").reset_index(drop=True)
    data["area_name"] = data["geo_name"].str.replace(r"\s+\d+$", "", regex=True)
    if "recommended_activation_type" not in data.columns and "recommended_commercial_play" in data.columns:
        data["recommended_activation_type"] = data["recommended_commercial_play"]
    if "recommended_activation_type" not in data.columns and "recommended_product_focus" in data.columns:
        data["recommended_activation_type"] = data["recommended_product_focus"]
    data["recommended_activation_type"] = data["recommended_activation_type"].replace(
        {
            "Annual pass / repeat visit": "Annual pass",
            "Targeted day visit": "Other",
            "Destination-led campaign": "Other",
            "Seasonal / tactical activation": "Other",
        }
    )
    return data


@st.cache_data
def load_attractions() -> pd.DataFrame:
    attractions = pd.read_csv(ATTRACTION_PATH)
    return attractions.rename(
        columns={
            "attraction_name_official": "attraction_name",
            "brand_official": "brand",
            "experience_category_inferred": "category",
        }
    )


@st.cache_data
def load_project_fact_sheet() -> str:
    if FACT_SHEET_PATH.exists():
        return FACT_SHEET_PATH.read_text(encoding="utf-8")
    return (
        "This dashboard identifies MSOA-level customer opportunity for Merlin UK using public demographic data, "
        "Merlin attraction locations, opportunity scoring, and activation recommendations. The analysis is a "
        "market opportunity prototype and does not use internal Merlin customer, sales, CRM, or campaign data."
    )


def compact_number(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}m"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.0f}k"
    return f"{value:,.0f}"


def currency_number(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"£{value / 1_000_000:.1f}m"
    if abs(value) >= 1_000:
        return f"£{value / 1_000:.0f}k"
    return f"£{value:,.0f}"


def metric_card(label: str, value: str, note: str, accent: str, tooltip: Optional[str] = None) -> None:
    with st.container(border=True):
        st.markdown(
            f'<div style="height:4px;background:{accent};border-radius:8px 8px 0 0;margin-bottom:6px;"></div>',
            unsafe_allow_html=True,
        )
        st.metric(label=label, value=value, help=tooltip)
        st.caption(note)


def filtered_potential_revenue(data: pd.DataFrame, penetration_pct: float) -> float:
    return (
        data["total_population"]
        * (penetration_pct / 100)
        * REVENUE_PER_VISITOR_GBP
    ).sum()


def population_for_play(data: pd.DataFrame, play: str) -> int:
    return int(data.loc[data["recommended_activation_type"].eq(play), "total_population"].sum())


def revenue_for_play(data: pd.DataFrame, play: str, penetration_pct: float) -> float:
    play_population = population_for_play(data, play)
    return play_population * (penetration_pct / 100) * REVENUE_PER_VISITOR_GBP


def revenue_by_activation_chart(data: pd.DataFrame, penetration_pct: float) -> alt.Chart:
    chart_data = (
        data.groupby("recommended_activation_type", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
        )
        .assign(
            revenue_scenario=lambda df: df["total_population"] * (penetration_pct / 100) * REVENUE_PER_VISITOR_GBP,
            revenue_scenario_millions=lambda df: df["revenue_scenario"] / 1_000_000,
            play_order=lambda df: df["recommended_activation_type"].map({play: i for i, play in enumerate(PLAY_ORDER)}),
            activation_label=lambda df: df["recommended_activation_type"].replace(
                {"Multi-attraction cluster marketing": "Cluster marketing"}
            ),
        )
        .sort_values("play_order")
    )
    label_order = ["Cluster marketing", "Annual pass", "Short break", "Other"]

    return (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
        .encode(
            x=alt.X("revenue_scenario_millions:Q", title="Revenue scenario, GBP m"),
            y=alt.Y("activation_label:N", sort=label_order, title=""),
            color=alt.Color(
                "activation_label:N",
                scale=alt.Scale(domain=label_order, range=[PLAY_COLOURS_HEX[play] for play in PLAY_ORDER]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("activation_label:N", title="Activation type"),
                alt.Tooltip("revenue_scenario_millions:Q", title="Revenue scenario, GBP m", format=".1f"),
                alt.Tooltip("total_population:Q", title="Population", format=","),
                alt.Tooltip("msoa_count:Q", title="MSOAs", format=","),
            ],
        )
        .properties(height=250)
    )


def top_attractions_by_audience_chart(data: pd.DataFrame, penetration_pct: float, top_n: int = 8) -> alt.Chart:
    chart_data = (
        data.groupby("recommended_attraction_name", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
            mean_score=("overall_opportunity_score", "mean"),
        )
        .assign(
            revenue_scenario=lambda df: df["total_population"] * (penetration_pct / 100) * REVENUE_PER_VISITOR_GBP,
            population_millions=lambda df: df["total_population"] / 1_000_000,
            revenue_scenario_millions=lambda df: df["revenue_scenario"] / 1_000_000,
        )
        .sort_values(["total_population", "mean_score"], ascending=[False, False])
        .head(top_n)
    )

    return (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
        .encode(
            x=alt.X("population_millions:Q", title="Recommended audience, millions"),
            y=alt.Y("recommended_attraction_name:N", sort="-x", title=""),
            color=alt.value(MERLIN_PURPLE),
            tooltip=[
                alt.Tooltip("recommended_attraction_name:N", title="Recommended attraction"),
                alt.Tooltip("total_population:Q", title="Population", format=","),
                alt.Tooltip("revenue_scenario_millions:Q", title="Revenue scenario, GBP m", format=".1f"),
                alt.Tooltip("msoa_count:Q", title="MSOAs", format=","),
                alt.Tooltip("mean_score:Q", title="Mean GOI", format=".1f"),
            ],
        )
        .properties(height=250)
    )


def highest_opportunity_area(data: pd.DataFrame) -> tuple:
    if data.empty:
        return "n/a", "No matching MSOAs"
    area_summary = top_opportunity_areas(data, top_n=None)
    row = area_summary.iloc[0]
    return (
        str(row["area_name"]),
        f"Mean GOI {row['mean_score']:.1f} | {compact_number(row['total_population'])} people",
    )


def top_opportunity_areas(data: pd.DataFrame, top_n: Optional[int] = 5) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(columns=["area_name", "msoa_count", "total_population", "mean_score"])
    area_summary = (
        data.groupby("area_name", as_index=False)
        .agg(
            msoa_count=("geo_code", "count"),
            total_population=("total_population", "sum"),
            mean_score=("overall_opportunity_score", "mean"),
        )
        .sort_values(["mean_score", "total_population", "msoa_count"], ascending=[False, False, False])
    )
    if top_n is None:
        return area_summary
    return area_summary.head(top_n)


def largest_attraction_audience_in_area(data: pd.DataFrame, area_name: str) -> tuple:
    if data.empty:
        return "n/a", "No matching MSOAs"
    if area_name == "n/a":
        return "n/a", "No area cluster selected"
    area_data = data.loc[data["area_name"].eq(area_name)].copy()
    if area_data.empty:
        return "n/a", "No MSOAs in selected area"
    attraction_summary = (
        area_data.groupby("recommended_attraction_name", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
            mean_score=("overall_opportunity_score", "mean"),
        )
        .sort_values(["total_population", "mean_score"], ascending=[False, False])
    )
    row = attraction_summary.iloc[0]
    return (
        str(row["recommended_attraction_name"]),
        f"Recommended to {compact_number(row['total_population'])} people in {area_name}",
    )


def dataframe_preview(data: pd.DataFrame, columns: list, max_rows: int = 8) -> str:
    available_columns = [column for column in columns if column in data.columns]
    if data.empty or not available_columns:
        return "No rows available."
    return data.loc[:, available_columns].head(max_rows).to_csv(index=False)


def normalize_question_text(value: str) -> str:
    return " ".join("".join(character.lower() if character.isalnum() else " " for character in value).split())


def mentioned_values(question: str, values: pd.Series) -> list:
    question_text = normalize_question_text(question)
    matches = []
    for value in values.dropna().astype(str).unique():
        normalized_value = normalize_question_text(value)
        if len(normalized_value) >= 4 and normalized_value in question_text:
            matches.append(value)
    return matches


def add_revenue_scenario(data: pd.DataFrame, penetration_pct: float) -> pd.DataFrame:
    if data.empty:
        return data.copy()
    data = data.copy()
    data["revenue_scenario"] = data["total_population"] * (penetration_pct / 100) * REVENUE_PER_VISITOR_GBP
    return data


def build_question_dataset_extract(
    full_data: pd.DataFrame,
    filtered_data: pd.DataFrame,
    question: str,
    penetration_pct: float,
) -> str:
    question_text = normalize_question_text(question)
    current_view_terms = ["current", "filtered", "selected", "selection", "view", "dashboard", "these filters"]
    full_dataset_terms = ["full", "overall", "all msoas", "entire", "national", "across the dataset"]
    compare_terms = ["compare", "versus", "vs", "against"]

    use_current_view = any(term in question_text for term in current_view_terms)
    use_full_dataset = any(term in question_text for term in full_dataset_terms)
    compare_scopes = any(term in question_text for term in compare_terms) and (use_current_view or use_full_dataset)
    if use_current_view and not use_full_dataset:
        base_data = filtered_data
        base_label = "current dashboard filters"
    else:
        base_data = full_data
        base_label = "full opportunity dataset"

    area_matches = mentioned_values(question, full_data["area_name"])
    attraction_matches = mentioned_values(question, full_data["recommended_attraction_name"])
    activation_matches = mentioned_values(question, full_data["recommended_activation_type"])
    segment_matches = mentioned_values(question, full_data["segment_label"])

    query_data = base_data.copy()
    applied_filters = []
    if area_matches:
        query_data = query_data.loc[query_data["area_name"].isin(area_matches)]
        applied_filters.append("area_name in " + ", ".join(area_matches[:8]))
    if attraction_matches:
        query_data = query_data.loc[query_data["recommended_attraction_name"].isin(attraction_matches)]
        applied_filters.append("recommended_attraction_name in " + ", ".join(attraction_matches[:8]))
    if activation_matches:
        query_data = query_data.loc[query_data["recommended_activation_type"].isin(activation_matches)]
        applied_filters.append("recommended_activation_type in " + ", ".join(activation_matches[:8]))
    if segment_matches:
        query_data = query_data.loc[query_data["segment_label"].isin(segment_matches)]
        applied_filters.append("segment_label in " + ", ".join(segment_matches[:8]))
    if "family" in question_text and not segment_matches:
        query_data = query_data.loc[query_data["segment_label"].str.contains("family", case=False, na=False)]
        applied_filters.append("segment_label contains family")
    if "legoland" in question_text and not attraction_matches:
        query_data = query_data.loc[query_data["recommended_attraction_name"].str.contains("LEGOLAND", case=False, na=False)]
        applied_filters.append("recommended_attraction_name contains LEGOLAND")

    query_data = add_revenue_scenario(query_data, penetration_pct)
    if query_data.empty:
        return "\n".join(
            [
                "Question-specific dataset extract:",
                f"- Primary source queried: {base_label}",
                "- Matching rows after question-specific filters: 0",
                f"- Filters inferred from question: {', '.join(applied_filters) if applied_filters else 'none'}",
            ]
        )

    area_summary = (
        query_data.groupby("area_name", as_index=False)
        .agg(
            msoa_count=("geo_code", "count"),
            total_population=("total_population", "sum"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
            revenue_scenario=("revenue_scenario", "sum"),
        )
        .sort_values(["mean_opportunity_score", "total_population", "msoa_count"], ascending=[False, False, False])
    )
    attraction_summary = (
        query_data.groupby("recommended_attraction_name", as_index=False)
        .agg(
            msoa_count=("geo_code", "count"),
            total_population=("total_population", "sum"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
            revenue_scenario=("revenue_scenario", "sum"),
        )
        .sort_values(["total_population", "mean_opportunity_score"], ascending=[False, False])
    )
    activation_summary = (
        query_data.groupby("recommended_activation_type", as_index=False)
        .agg(
            msoa_count=("geo_code", "count"),
            total_population=("total_population", "sum"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
            revenue_scenario=("revenue_scenario", "sum"),
        )
        .sort_values(["total_population", "mean_opportunity_score"], ascending=[False, False])
    )
    segment_summary = (
        query_data.groupby("segment_label", as_index=False)
        .agg(
            msoa_count=("geo_code", "count"),
            total_population=("total_population", "sum"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
            revenue_scenario=("revenue_scenario", "sum"),
        )
        .sort_values(["total_population", "mean_opportunity_score"], ascending=[False, False])
    )
    top_msoas = query_data.sort_values("opportunity_rank").head(12)

    extract_lines = [
        "Question-specific dataset extract:",
        f"- Primary source queried: {base_label}",
        f"- Matching rows after question-specific filters: {len(query_data):,}",
        f"- Matching population: {query_data['total_population'].sum():,.0f}",
        f"- Mean opportunity score: {query_data['overall_opportunity_score'].mean():.1f}",
        f"- Revenue scenario: {currency_number(query_data['revenue_scenario'].sum())}",
        f"- Filters inferred from question: {', '.join(applied_filters) if applied_filters else 'none'}",
        "",
        "Top matching areas:",
        dataframe_preview(
            area_summary,
            ["area_name", "msoa_count", "total_population", "mean_opportunity_score", "revenue_scenario"],
            max_rows=12,
        ),
        "Top matching attractions:",
        dataframe_preview(
            attraction_summary,
            [
                "recommended_attraction_name",
                "msoa_count",
                "total_population",
                "mean_opportunity_score",
                "revenue_scenario",
            ],
            max_rows=12,
        ),
        "Matching activation types:",
        dataframe_preview(
            activation_summary,
            ["recommended_activation_type", "msoa_count", "total_population", "mean_opportunity_score", "revenue_scenario"],
            max_rows=8,
        ),
        "Top matching customer segments:",
        dataframe_preview(
            segment_summary,
            ["segment_label", "msoa_count", "total_population", "mean_opportunity_score", "revenue_scenario"],
            max_rows=12,
        ),
        "Highest ranked matching MSOAs:",
        dataframe_preview(
            top_msoas,
            [
                "geo_name",
                "area_name",
                "segment_label",
                "overall_opportunity_score",
                "opportunity_rank",
                "recommended_attraction_name",
                "recommended_activation_type",
                "recommended_attraction_distance_miles",
                "key_contributing_driver",
                "total_population",
                "revenue_scenario",
            ],
            max_rows=12,
        ),
    ]

    if compare_scopes and not filtered_data.empty:
        filtered_with_revenue = add_revenue_scenario(filtered_data, penetration_pct)
        extract_lines.extend(
            [
                "",
                "Current-filter comparison metrics:",
                f"- Current filtered MSOAs: {len(filtered_with_revenue):,}",
                f"- Current filtered population: {filtered_with_revenue['total_population'].sum():,.0f}",
                f"- Current filtered mean opportunity score: {filtered_with_revenue['overall_opportunity_score'].mean():.1f}",
                f"- Current filtered revenue scenario: {currency_number(filtered_with_revenue['revenue_scenario'].sum())}",
            ]
        )

    return "\n".join(extract_lines)


def build_chatbot_context(
    full_data: pd.DataFrame,
    filtered_data: pd.DataFrame,
    penetration_pct: float,
    selected_attractions: list,
    selected_segments: list,
    selected_plays: list,
    area_search: str,
    rank_limit: int,
    top_area: str,
    top_attraction: str,
) -> str:
    filter_summary = {
        "Merlin attraction": ", ".join(selected_attractions) if selected_attractions else "All attractions",
        "Customer segment": ", ".join(selected_segments) if selected_segments else "All segments",
        "Activation type": ", ".join(selected_plays) if selected_plays else "All activation types",
        "Area name contains": area_search if area_search else "All areas",
        "Top opportunity MSOAs": f"Rank 1 to {rank_limit:,}",
        "Market penetration": f"{penetration_pct}%",
    }

    full_activation_summary = (
        full_data.groupby("recommended_activation_type", as_index=False)
        .agg(total_population=("total_population", "sum"), msoa_count=("geo_code", "count"))
        .sort_values("total_population", ascending=False)
    )
    full_attraction_summary = (
        full_data.groupby("recommended_attraction_name", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
        )
        .sort_values(["total_population", "mean_opportunity_score"], ascending=[False, False])
        .head(10)
    )
    full_segment_summary = (
        full_data.groupby("segment_label", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
        )
        .sort_values(["mean_opportunity_score", "total_population"], ascending=[False, False])
    )
    full_area_summary = top_opportunity_areas(full_data, top_n=10)
    family_annual_pass_summary = (
        full_data.loc[
            full_data["recommended_activation_type"].eq("Annual pass")
            & full_data["segment_label"].str.contains("family", case=False, na=False)
        ]
        .groupby("area_name", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
        )
        .sort_values(["mean_opportunity_score", "total_population"], ascending=[False, False])
        .head(8)
    )
    legoland_summary = (
        full_data.loc[full_data["recommended_attraction_name"].str.contains("LEGOLAND", case=False, na=False)]
        .groupby("area_name", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
        )
        .sort_values(["mean_opportunity_score", "total_population"], ascending=[False, False])
        .head(8)
    )

    full_context_lines = [
        "Full opportunity dataset context:",
        f"- Total MSOAs: {len(full_data):,}",
        f"- Total population: {full_data['total_population'].sum():,.0f}",
        f"- Mean opportunity score: {full_data['overall_opportunity_score'].mean():.1f}",
        "",
        "Customer segments across the full dataset:",
        dataframe_preview(full_segment_summary, ["segment_label", "total_population", "msoa_count", "mean_opportunity_score"], max_rows=12),
        "Highest opportunity areas across the full dataset:",
        dataframe_preview(full_area_summary, ["area_name", "msoa_count", "total_population", "mean_score"], max_rows=10),
        "Top recommended attractions by audience across the full dataset:",
        dataframe_preview(
            full_attraction_summary,
            ["recommended_attraction_name", "total_population", "msoa_count", "mean_opportunity_score"],
            max_rows=10,
        ),
        "Activation types across the full dataset:",
        dataframe_preview(full_activation_summary, ["recommended_activation_type", "total_population", "msoa_count"]),
        "Highest opportunity areas for LEGOLAND across the full dataset:",
        dataframe_preview(legoland_summary, ["area_name", "total_population", "msoa_count", "mean_opportunity_score"]),
        "Highest opportunity family annual pass areas across the full dataset:",
        dataframe_preview(family_annual_pass_summary, ["area_name", "total_population", "msoa_count", "mean_opportunity_score"]),
    ]

    if filtered_data.empty:
        return (
            "\n".join(full_context_lines)
            + "\n\nCurrent dashboard filter context:\n"
            + "\n".join([f"- {label}: {value}" for label, value in filter_summary.items()])
            + "\n"
            "- The current filters return no matching MSOAs.\n"
        )

    revenue = filtered_potential_revenue(filtered_data, penetration_pct)
    activation_summary = (
        filtered_data.groupby("recommended_activation_type", as_index=False)
        .agg(total_population=("total_population", "sum"), msoa_count=("geo_code", "count"))
        .assign(revenue_scenario=lambda df: df["total_population"] * (penetration_pct / 100) * REVENUE_PER_VISITOR_GBP)
        .sort_values("total_population", ascending=False)
    )
    attraction_summary = (
        filtered_data.groupby("recommended_attraction_name", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
        )
        .sort_values(["total_population", "mean_opportunity_score"], ascending=[False, False])
        .head(8)
    )
    segment_summary = (
        filtered_data.groupby("segment_label", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
            mean_opportunity_score=("overall_opportunity_score", "mean"),
        )
        .sort_values(["total_population", "mean_opportunity_score"], ascending=[False, False])
        .head(8)
    )
    top_msoas = filtered_data.sort_values("opportunity_rank").head(8)

    return "\n".join(
        [
            *full_context_lines,
            "",
            "Current dashboard filter context:",
            *[f"- {label}: {value}" for label, value in filter_summary.items()],
            "",
            "Current filtered headline metrics:",
            f"- Matching MSOAs: {len(filtered_data):,}",
            f"- Total population: {filtered_data['total_population'].sum():,.0f}",
            f"- Revenue scenario: {currency_number(revenue)}",
            f"- Top opportunity area: {top_area}",
            f"- Recommended attraction for the top opportunity area: {top_attraction}",
            f"- Mean opportunity score: {filtered_data['overall_opportunity_score'].mean():.1f}",
            f"- Best opportunity rank in current filters: {int(filtered_data['opportunity_rank'].min()):,}",
            "",
            "Activation summary for current filters:",
            dataframe_preview(
                activation_summary,
                ["recommended_activation_type", "total_population", "msoa_count", "revenue_scenario"],
            ),
            "Top recommended attractions by audience for current filters:",
            dataframe_preview(
                attraction_summary,
                ["recommended_attraction_name", "total_population", "msoa_count", "mean_opportunity_score"],
            ),
            "Top customer segments by audience for current filters:",
            dataframe_preview(segment_summary, ["segment_label", "total_population", "msoa_count", "mean_opportunity_score"]),
            "Highest ranked MSOAs in current filters:",
            dataframe_preview(
                top_msoas,
                [
                    "geo_name",
                    "segment_label",
                    "overall_opportunity_score",
                    "opportunity_rank",
                    "recommended_attraction_name",
                    "recommended_activation_type",
                    "recommended_attraction_distance_miles",
                    "key_contributing_driver",
                    "total_population",
                ],
            ),
        ]
    )


def extract_openai_text(response_payload: dict) -> str:
    text_parts = []
    for item in response_payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                text_parts.append(content["text"])
    return "\n".join(text_parts).strip()


def ask_openai_data_assistant(
    api_key: str,
    question: str,
    fact_sheet: str,
    dashboard_context: str,
    dataset_extract: str,
) -> str:
    instructions = """
You are a concise data Q&A assistant embedded in a Merlin UK growth opportunity dashboard.

Answer only from the supplied project fact sheet, full opportunity dataset context, current dashboard filter context, and question-specific dataset extract.
If the supplied data does not contain enough information, say: "I do not have enough information in the provided data to answer that."
If the project fact sheet contains a preloaded answer for the stakeholder's question, use that answer as the primary source and adapt it lightly to the current dashboard context where relevant.
Do not invent Merlin internal performance, current penetration, ticket prices, campaign results, customer behaviour, or competitor information.
Do not answer questions unrelated to this Merlin UK opportunity analysis.
Use plain English for senior stakeholders. Keep the answer under 160 words unless the user asks for detail.
When giving numbers, make clear whether they come from the full opportunity dataset, the current dashboard filters, or illustrative revenue scenarios.
Prioritise the question-specific dataset extract for questions about areas, attractions, segments, activation types, rankings, comparisons, or MSOA lists.
If the question asks about the current view or selected filters, prioritise the current dashboard filter context. Otherwise, use the full opportunity dataset context.
"""
    user_input = f"""
Project fact sheet:
{fact_sheet}

Dashboard data context:
{dashboard_context}

Question-specific dataset extract:
{dataset_extract}

Stakeholder question:
{question}
"""
    response = requests.post(
        OPENAI_RESPONSES_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENAI_CHAT_MODEL,
            "instructions": instructions,
            "input": user_input,
            "temperature": 0.2,
            "max_output_tokens": 450,
            "store": False,
        },
        timeout=45,
    )
    if response.status_code != 200:
        try:
            error_message = response.json().get("error", {}).get("message", response.text)
        except ValueError:
            error_message = response.text
        raise RuntimeError(f"OpenAI API request failed: {error_message}")

    answer = extract_openai_text(response.json())
    if not answer:
        raise RuntimeError("OpenAI API returned no text response.")
    return answer


def queue_suggested_question(question: str) -> None:
    st.session_state["pending_chat_question"] = question


def prepare_map_data(data: pd.DataFrame, penetration_pct: float) -> pd.DataFrame:
    map_data = data.dropna(subset=["latitude", "longitude"]).copy()
    map_data["potential_revenue"] = (
        map_data["total_population"]
        * (penetration_pct / 100)
        * REVENUE_PER_VISITOR_GBP
    )
    map_data["potential_revenue_label"] = map_data["potential_revenue"].map(currency_number)
    map_data["population_label"] = map_data["total_population"].map(lambda x: f"{x:,.0f}")
    map_data["score_label"] = map_data["overall_opportunity_score"].map(lambda x: f"{x:.1f}")
    map_data["distance_label"] = map_data["recommended_attraction_distance_miles"].map(lambda x: f"{x:.1f} miles")
    map_data["play_colour"] = map_data["recommended_activation_type"].apply(
        lambda play: PLAY_COLOURS.get(play, [130, 125, 155, 135])
    )
    map_data["radius"] = (map_data["total_population"].clip(lower=2_000, upper=18_000) / 18_000 * 1100) + 350
    map_data["tooltip_title"] = map_data["geo_name"]
    map_data["tooltip_line_1"] = "Segment: " + map_data["segment_label"].astype(str)
    map_data["tooltip_line_2"] = "Activation type: " + map_data["recommended_activation_type"].astype(str)
    map_data["tooltip_line_3"] = (
        "GOI: " + map_data["score_label"] + " | Rank: " + map_data["opportunity_rank"].astype(str)
    )
    map_data["tooltip_line_4"] = "Population: " + map_data["population_label"]
    map_data["tooltip_line_5"] = "Recommended attraction: " + map_data["recommended_attraction_name"].astype(str)
    map_data["tooltip_line_6"] = "Distance: " + map_data["distance_label"]
    map_data["tooltip_line_7"] = "Revenue scenario: " + map_data["potential_revenue_label"]
    map_data["tooltip_line_8"] = "Driver: " + map_data["key_contributing_driver"].astype(str)
    return map_data


def build_map(
    data: pd.DataFrame,
    attractions: pd.DataFrame,
    penetration_pct: float,
    focused_area: Optional[str] = None,
) -> pdk.Deck:
    map_data = prepare_map_data(data, penetration_pct)
    highlight_map_data = pd.DataFrame()
    if focused_area:
        highlight_map_data = map_data.loc[map_data["area_name"].eq(focused_area)].copy()
        if not highlight_map_data.empty:
            highlight_map_data["highlight_radius"] = highlight_map_data["radius"] + 140
    attraction_map_data = attractions.dropna(subset=["latitude", "longitude"]).copy()
    attraction_map_data["tooltip_title"] = attraction_map_data["attraction_name"]
    attraction_map_data["tooltip_line_1"] = "Merlin attraction"
    attraction_map_data["tooltip_line_2"] = "Brand: " + attraction_map_data["brand"].astype(str)
    attraction_map_data["tooltip_line_3"] = "Category: " + attraction_map_data["category"].astype(str)
    attraction_map_data["tooltip_line_4"] = "Location: " + attraction_map_data["city_official"].astype(str)
    attraction_map_data["tooltip_line_5"] = "Postcode: " + attraction_map_data["postcode_official"].astype(str)
    attraction_map_data["tooltip_line_6"] = ""
    attraction_map_data["tooltip_line_7"] = ""
    attraction_map_data["tooltip_line_8"] = ""

    central_london_mask = attraction_map_data["attraction_name"].isin(CENTRAL_LONDON_LABEL_ATTRACTIONS)
    attraction_label_data = attraction_map_data.loc[~central_london_mask].copy()
    central_london_labels = attraction_map_data.loc[central_london_mask].copy()
    if not central_london_labels.empty:
        visible_central_names = set(central_london_labels["attraction_name"])
        combined_label = " / ".join(
            label
            for attraction_name, label in CENTRAL_LONDON_LABEL_ATTRACTIONS.items()
            if attraction_name in visible_central_names
        )
        attraction_label_data = pd.concat(
            [
                attraction_label_data,
                pd.DataFrame(
                    [
                        {
                            "latitude": central_london_labels["latitude"].mean(),
                            "longitude": central_london_labels["longitude"].mean(),
                            "brand": combined_label,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    if map_data.empty:
        latitude, longitude, zoom = 54.5, -2.5, 5
    elif not highlight_map_data.empty:
        latitude = highlight_map_data["latitude"].mean()
        longitude = highlight_map_data["longitude"].mean()
        zoom = 9.0 if len(highlight_map_data) <= 30 else 8.0
    else:
        latitude = map_data["latitude"].mean()
        longitude = map_data["longitude"].mean()
        zoom = 5.4 if len(map_data) > 800 else 7.0

    msoa_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position="[longitude, latitude]",
        get_radius="radius",
        get_fill_color="play_colour",
        get_line_color=[43, 16, 85, 180],
        line_width_min_pixels=0.6,
        pickable=True,
        opacity=0.72,
    )
    highlight_layer = pdk.Layer(
        "ScatterplotLayer",
        data=highlight_map_data,
        get_position="[longitude, latitude]",
        get_radius="highlight_radius",
        get_fill_color=[0, 0, 0, 0],
        get_line_color=[255, 216, 77, 255],
        line_width_min_pixels=3,
        pickable=False,
        stroked=True,
        filled=False,
        opacity=1.0,
    )
    attraction_layer = pdk.Layer(
        "ScatterplotLayer",
        data=attraction_map_data,
        get_position="[longitude, latitude]",
        get_radius=2600,
        get_fill_color=[255, 216, 77, 245],
        get_line_color=[43, 16, 85, 255],
        line_width_min_pixels=2,
        pickable=True,
        opacity=0.95,
    )
    attraction_symbol_layer = pdk.Layer(
        "TextLayer",
        data=attraction_label_data,
        get_position="[longitude, latitude]",
        get_text="brand",
        get_size=12,
        get_color=[43, 16, 85, 255],
        get_angle=0,
        get_text_anchor='"middle"',
        get_alignment_baseline='"bottom"',
        pickable=False,
    )
    tooltip = {
        "html": """
            <b>{tooltip_title}</b><br/>
            {tooltip_line_1}<br/>
            {tooltip_line_2}<br/>
            {tooltip_line_3}<br/>
            {tooltip_line_4}<br/>
            {tooltip_line_5}<br/>
            {tooltip_line_6}<br/>
            {tooltip_line_7}<br/>
            {tooltip_line_8}
        """,
        "style": {"backgroundColor": "#2b1055", "color": "white", "fontSize": "12px"},
    }
    layers = [msoa_layer]
    if not highlight_map_data.empty:
        layers.append(highlight_layer)
    layers.extend([attraction_layer, attraction_symbol_layer])

    return pdk.Deck(
        map_provider="carto",
        map_style="light",
        initial_view_state=pdk.ViewState(latitude=latitude, longitude=longitude, zoom=zoom, pitch=0),
        layers=layers,
        tooltip=tooltip,
    )


df = load_opportunity_data()
attractions = load_attractions()
project_fact_sheet = load_project_fact_sheet()
default_rank_limit = int(df["opportunity_rank"].max())

if "attraction_filter" not in st.session_state:
    st.session_state["attraction_filter"] = ["All attractions"]
if "segment_filter" not in st.session_state:
    st.session_state["segment_filter"] = ["All segments"]
if "activation_filter" not in st.session_state:
    st.session_state["activation_filter"] = ["All activation types"]
if "area_filter" not in st.session_state:
    st.session_state["area_filter"] = "All areas"
if "rank_filter" not in st.session_state:
    st.session_state["rank_filter"] = default_rank_limit
if "penetration_filter" not in st.session_state:
    st.session_state["penetration_filter"] = 30
if "leaderboard_area_focus" not in st.session_state:
    st.session_state["leaderboard_area_focus"] = None
if "map_reset_counter" not in st.session_state:
    st.session_state["map_reset_counter"] = 0
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []


def reset_map_view():
    st.session_state["leaderboard_area_focus"] = None
    st.session_state["map_reset_counter"] += 1


def reset_filters():
    st.session_state["attraction_filter"] = ["All attractions"]
    st.session_state["segment_filter"] = ["All segments"]
    st.session_state["activation_filter"] = ["All activation types"]
    st.session_state["area_filter"] = "All areas"
    st.session_state["rank_filter"] = default_rank_limit
    st.session_state["penetration_filter"] = 30
    st.session_state["leaderboard_area_focus"] = None
    st.session_state["map_reset_counter"] += 1


st.markdown(
    """
    <div class="hero">
        <h1>Merlin Growth Opportunity Explorer</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filters")

    attraction_options = ["All attractions"] + sorted(df["recommended_attraction_name"].dropna().unique().tolist())
    selected_attractions = st.multiselect(
        "Merlin attraction",
        attraction_options,
        key="attraction_filter",
    )

    segment_options = ["All segments"] + sorted(df["segment_label"].dropna().unique().tolist())
    selected_segments = st.multiselect("Customer segment", segment_options, key="segment_filter")

    play_options = ["All activation types"] + sorted(df["recommended_activation_type"].dropna().unique().tolist())
    selected_plays = st.multiselect("Activation type", play_options, key="activation_filter")

    area_options = ["All areas"] + sorted(df["area_name"].dropna().unique().tolist())
    selected_area = st.selectbox(
        "Area name",
        area_options,
        key="area_filter",
        help="Start typing to search and select an area.",
    )
    area_search = "" if selected_area == "All areas" else selected_area

    max_rank = int(df["opportunity_rank"].max())
    rank_limit = st.slider(
        "Top opportunity MSOAs",
        1,
        max_rank,
        default_rank_limit,
        key="rank_filter",
        help=(
            "MSOA stands for Middle Layer Super Output Area. It is a small UK statistical geography, "
            "typically containing around 5,000 to 15,000 residents. This slider includes MSOAs from rank 1 "
            "up to the selected rank."
        ),
    )
    penetration_pct = st.slider("Market penetration", 10, 100, 30, 10, format="%d%%", key="penetration_filter")

    st.button("Reset filters", use_container_width=True, on_click=reset_filters)

filtered_df = df.loc[df["opportunity_rank"].le(rank_limit)].copy()
selected_attraction_values = [value for value in selected_attractions if value != "All attractions"]
selected_segment_values = [value for value in selected_segments if value != "All segments"]
selected_play_values = [value for value in selected_plays if value != "All activation types"]
if selected_attraction_values:
    filtered_df = filtered_df.loc[filtered_df["recommended_attraction_name"].isin(selected_attraction_values)]
if selected_segment_values:
    filtered_df = filtered_df.loc[filtered_df["segment_label"].isin(selected_segment_values)]
if selected_play_values:
    filtered_df = filtered_df.loc[filtered_df["recommended_activation_type"].isin(selected_play_values)]
if area_search:
    filtered_df = filtered_df.loc[filtered_df["area_name"].eq(area_search)]

if not selected_attraction_values:
    map_attractions = attractions.copy()
else:
    map_attractions = attractions.loc[attractions["attraction_name"].isin(selected_attraction_values)].copy()

potential_revenue = filtered_potential_revenue(filtered_df, penetration_pct)
filtered_population = int(filtered_df["total_population"].sum()) if not filtered_df.empty else 0
filtered_msoa_count = len(filtered_df)
cluster_population = population_for_play(filtered_df, "Multi-attraction cluster marketing")
annual_pass_population = population_for_play(filtered_df, "Annual pass")
short_break_population = population_for_play(filtered_df, "Short break")
cluster_revenue = revenue_for_play(filtered_df, "Multi-attraction cluster marketing", penetration_pct)
annual_pass_revenue = revenue_for_play(filtered_df, "Annual pass", penetration_pct)
short_break_revenue = revenue_for_play(filtered_df, "Short break", penetration_pct)
top_area, top_area_note = highest_opportunity_area(filtered_df)
top_attraction, top_attraction_note = largest_attraction_audience_in_area(filtered_df, top_area)

metric_cols = st.columns(6)
with metric_cols[0]:
    metric_card(
        "Population",
        compact_number(filtered_population),
        f"{filtered_msoa_count:,} matching MSOAs",
        MERLIN_PURPLE,
        tooltip=(
            "MSOA stands for Middle Layer Super Output Area. It is a small UK statistical geography, "
            "typically containing around 5,000 to 15,000 residents, used here as the local market area."
        ),
    )
with metric_cols[1]:
    metric_card("Revenue Scenario", currency_number(potential_revenue), f"{penetration_pct}% population x £33 revenue per visitor", MERLIN_GOLD)
with metric_cols[2]:
    metric_card("Cluster Marketing Opportunity", compact_number(cluster_population), f"Revenue scenario: {currency_number(cluster_revenue)}", MERLIN_AQUA)
with metric_cols[3]:
    metric_card("Annual Pass Opportunity", compact_number(annual_pass_population), f"Revenue scenario: {currency_number(annual_pass_revenue)}", MERLIN_BLUE)
with metric_cols[4]:
    metric_card("Short Break Opportunity", compact_number(short_break_population), f"Revenue scenario: {currency_number(short_break_revenue)}", "#7b61ff")
with metric_cols[5]:
    metric_card(
        "Top Opportunity Area",
        top_area,
        top_area_note,
        MERLIN_PURPLE,
        tooltip=(
            "GOI means Growth Opportunity Index. It combines market size, segment priority and recommended "
            "attraction alignment. This BAN groups the current filtered MSOAs by area and selects the area "
            "with the highest mean GOI, using population and MSOA count as tie-breakers."
        ),
    )

chart_col_1, chart_col_2 = st.columns(2)
with chart_col_1:
    with st.container(border=True):
        st.subheader("Revenue Scenario by Activation Type")
        if filtered_df.empty:
            st.info("No matching MSOAs for the current filters.")
        else:
            st.altair_chart(revenue_by_activation_chart(filtered_df, penetration_pct), use_container_width=True)

with chart_col_2:
    with st.container(border=True):
        st.subheader("Top Recommended Attractions by Audience")
        if filtered_df.empty:
            st.info("No matching MSOAs for the current filters.")
        else:
            st.altair_chart(top_attractions_by_audience_chart(filtered_df, penetration_pct), use_container_width=True)

with st.container(border=True):
    map_col, leaderboard_col = st.columns([4.6, 1.4])
    area_leaderboard = top_opportunity_areas(filtered_df, top_n=5)
    focused_area = st.session_state.get("leaderboard_area_focus")
    if focused_area and focused_area not in set(filtered_df["area_name"].dropna()):
        focused_area = None
        st.session_state["leaderboard_area_focus"] = None

    with leaderboard_col:
        st.subheader("Top Opportunity Areas")
        if area_leaderboard.empty:
            st.info("No areas to rank.")
        else:
            for index, row in enumerate(area_leaderboard.itertuples(index=False), start=1):
                is_selected = row.area_name == focused_area
                if st.button(
                    f"{index}. {row.area_name}",
                    key=f"leaderboard_area_{index}_{row.area_name}",
                    type="primary" if is_selected else "secondary",
                    use_container_width=True,
                ):
                    focused_area = row.area_name
                    st.session_state["leaderboard_area_focus"] = focused_area
                st.caption(
                    f"Mean GOI {row.mean_score:.1f} | "
                    f"{compact_number(row.total_population)} people | "
                    f"{int(row.msoa_count):,} MSOAs"
                )

    with map_col:
        reset_map_col = st.columns([1, 0.24])
        with reset_map_col[1]:
            st.button("Reset map view", use_container_width=True, on_click=reset_map_view)
        st.markdown(
            """
            <div class="map-legend">
                <span class="legend-item"><span class="legend-swatch" style="background: rgba(35, 182, 230, 0.75);"></span>Cluster marketing</span>
                <span class="legend-item"><span class="legend-swatch" style="background: rgba(255, 138, 0, 0.85);"></span>Annual pass</span>
                <span class="legend-item"><span class="legend-swatch" style="background: rgba(123, 97, 255, 0.75);"></span>Short break</span>
                <span class="legend-item"><span class="legend-swatch" style="background: rgba(130, 125, 155, 0.55);"></span>Other</span>
                <span class="legend-item"><span class="legend-attraction">M</span>Merlin attraction</span>
                <span class="legend-item"><span class="legend-swatch" style="background: transparent; border: 3px solid #ffd84d;"></span>Selected leaderboard area</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if filtered_df.empty:
            st.info("No MSOAs match the current filters.")
        else:
            st.pydeck_chart(
                build_map(filtered_df, map_attractions, penetration_pct, focused_area),
                use_container_width=True,
                height=650,
                key=f"opportunity_map_{st.session_state['map_reset_counter']}",
            )

with st.container(border=True):
    st.subheader("Ask the Data")

    openai_api_key = st.text_input(
        "OpenAI API key",
        type="password",
        key="openai_api_key",
        help="Used only for this Streamlit session. The key is not saved by the app.",
    )

    suggested_questions = [
        "Explain each customer segment to me.",
        "Which areas are highest opportunity for LEGOLAND?",
        "Where should Merlin target family annual passes?",
        "Which attractions have the largest recommended audience?",
    ]
    suggestion_cols = st.columns(4)
    for index, question in enumerate(suggested_questions):
        with suggestion_cols[index]:
            st.button(
                question,
                key=f"suggested_question_{index}",
                use_container_width=True,
                on_click=queue_suggested_question,
                args=(question,),
            )

    question_to_answer = None
    if "pending_chat_question" in st.session_state:
        question_to_answer = st.session_state.pop("pending_chat_question")

    with st.form("stakeholder_chat_form", clear_on_submit=True):
        typed_question = st.text_input(
            "Ask a question about the dashboard (AI could be wrong; follow-ups are not supported by design.)",
            placeholder="Example: Where should Merlin target family annual passes?",
        )
        submitted_question = st.form_submit_button("Ask assistant")
        if submitted_question and typed_question.strip():
            question_to_answer = typed_question.strip()

    if question_to_answer:
        if not openai_api_key:
            st.warning("Paste an OpenAI API key to activate the assistant.")
        else:
            st.session_state["chat_messages"].append({"role": "user", "content": question_to_answer})
            dashboard_context = build_chatbot_context(
                df,
                filtered_df,
                penetration_pct,
                selected_attraction_values,
                selected_segment_values,
                selected_play_values,
                area_search,
                rank_limit,
                top_area,
                top_attraction,
            )
            dataset_extract = build_question_dataset_extract(
                df,
                filtered_df,
                question_to_answer,
                penetration_pct,
            )
            with st.spinner("Asking the data assistant..."):
                try:
                    assistant_answer = ask_openai_data_assistant(
                        openai_api_key,
                        question_to_answer,
                        project_fact_sheet,
                        dashboard_context,
                        dataset_extract,
                    )
                except Exception as exc:
                    assistant_answer = (
                        "I could not complete the OpenAI API request. "
                        f"Please check the API key and try again. Details: {exc}"
                    )
            st.session_state["chat_messages"].append({"role": "assistant", "content": assistant_answer})

    if st.session_state["chat_messages"]:
        for message in st.session_state["chat_messages"][-8:]:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        if st.button("Clear chat", use_container_width=False):
            st.session_state["chat_messages"] = []
            st.rerun()
    else:
        st.info("Try one of the suggested questions, or ask your own question about the filtered opportunity data.")
