from pathlib import Path

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FULL_OUTPUT_PATH = OUTPUT_DIR / "msoa_layer_2_opportunity_scores.csv"
KEY_OUTPUT_PATH = OUTPUT_DIR / "merlin_key_recommendation_output.csv"
ATTRACTION_PATH = PROCESSED_DIR / "merlin_attraction_data.csv"

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
    if FULL_OUTPUT_PATH.exists():
        data = pd.read_csv(FULL_OUTPUT_PATH)
    else:
        data = pd.read_csv(KEY_OUTPUT_PATH)

    data = data.sort_values("opportunity_rank").reset_index(drop=True)
    data["area_name"] = data["geo_name"].str.replace(r"\s+\d+$", "", regex=True)
    data["top_10_opportunity_flag"] = data["opportunity_rank"].le(max(1, round(len(data) * 0.10)))
    data["recommended_commercial_play"] = data["recommended_commercial_play"].replace(
        {
            "Annual pass / repeat visit": "Annual pass",
            "Targeted day visit": "Other",
            "Destination-led campaign": "Other",
            "Seasonal / tactical activation": "Other",
        }
    )
    data["recommended_product_focus"] = data["recommended_commercial_play"]
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


def filtered_potential_revenue(data: pd.DataFrame, penetration_pct: float) -> float:
    return (
        data["total_population"]
        * (penetration_pct / 100)
        * REVENUE_PER_VISITOR_GBP
    ).sum()


def population_for_play(data: pd.DataFrame, play: str) -> int:
    return int(data.loc[data["recommended_commercial_play"].eq(play), "total_population"].sum())


def revenue_for_play(data: pd.DataFrame, play: str, penetration_pct: float) -> float:
    play_population = population_for_play(data, play)
    return play_population * (penetration_pct / 100) * REVENUE_PER_VISITOR_GBP


def revenue_by_activation_chart(data: pd.DataFrame, penetration_pct: float) -> alt.Chart:
    chart_data = (
        data.groupby("recommended_commercial_play", as_index=False)
        .agg(
            total_population=("total_population", "sum"),
            msoa_count=("geo_code", "count"),
        )
        .assign(
            revenue_scenario=lambda df: df["total_population"] * (penetration_pct / 100) * REVENUE_PER_VISITOR_GBP,
            revenue_scenario_millions=lambda df: df["revenue_scenario"] / 1_000_000,
            play_order=lambda df: df["recommended_commercial_play"].map({play: i for i, play in enumerate(PLAY_ORDER)}),
            activation_label=lambda df: df["recommended_commercial_play"].replace(
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
    top_area_data = data.loc[data["top_10_opportunity_flag"]].copy()
    if top_area_data.empty:
        return "n/a", "No top-10% MSOAs in current filters"
    area_summary = (
        top_area_data.groupby("area_name", as_index=False)
        .agg(
            top_10_msoas=("geo_code", "count"),
            top_10_population=("total_population", "sum"),
            mean_score=("overall_opportunity_score", "mean"),
        )
        .sort_values(["top_10_msoas", "top_10_population", "mean_score"], ascending=[False, False, False])
    )
    row = area_summary.iloc[0]
    return (
        str(row["area_name"]),
        f"{int(row['top_10_msoas']):,} top-10% MSOAs | {compact_number(row['top_10_population'])} people",
    )


def largest_attraction_audience_in_area(data: pd.DataFrame, area_name: str) -> tuple:
    if data.empty:
        return "n/a", "No matching MSOAs"
    if area_name == "n/a":
        return "n/a", "No area cluster selected"
    area_data = data.loc[data["area_name"].eq(area_name) & data["top_10_opportunity_flag"]].copy()
    if area_data.empty:
        return "n/a", "No top-10% MSOAs in area cluster"
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
    map_data["play_colour"] = map_data["recommended_commercial_play"].apply(
        lambda play: PLAY_COLOURS.get(play, [130, 125, 155, 135])
    )
    map_data["radius"] = (map_data["total_population"].clip(lower=2_000, upper=18_000) / 18_000 * 1100) + 350
    map_data["tooltip_title"] = map_data["geo_name"]
    map_data["tooltip_line_1"] = "Segment: " + map_data["segment_label"].astype(str)
    map_data["tooltip_line_2"] = "Activation type: " + map_data["recommended_commercial_play"].astype(str)
    map_data["tooltip_line_3"] = (
        "GOI: " + map_data["score_label"] + " | Rank: " + map_data["opportunity_rank"].astype(str)
    )
    map_data["tooltip_line_4"] = "Population: " + map_data["population_label"]
    map_data["tooltip_line_5"] = "Recommended attraction: " + map_data["recommended_attraction_name"].astype(str)
    map_data["tooltip_line_6"] = "Distance: " + map_data["distance_label"]
    map_data["tooltip_line_7"] = "Revenue scenario: " + map_data["potential_revenue_label"]
    map_data["tooltip_line_8"] = "Driver: " + map_data["key_contributing_driver"].astype(str)
    return map_data


def build_map(data: pd.DataFrame, attractions: pd.DataFrame, penetration_pct: float) -> pdk.Deck:
    map_data = prepare_map_data(data, penetration_pct)
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
    return pdk.Deck(
        map_provider="carto",
        map_style="light",
        initial_view_state=pdk.ViewState(latitude=latitude, longitude=longitude, zoom=zoom, pitch=0),
        layers=[msoa_layer, attraction_layer, attraction_symbol_layer],
        tooltip=tooltip,
    )


df = load_opportunity_data()
attractions = load_attractions()
default_rank_limit = min(1000, int(df["opportunity_rank"].max()))

if "attraction_filter" not in st.session_state:
    st.session_state["attraction_filter"] = ["All attractions"]
if "segment_filter" not in st.session_state:
    st.session_state["segment_filter"] = ["All segments"]
if "activation_filter" not in st.session_state:
    st.session_state["activation_filter"] = ["All activation types"]
if "rank_filter" not in st.session_state:
    st.session_state["rank_filter"] = default_rank_limit
if "penetration_filter" not in st.session_state:
    st.session_state["penetration_filter"] = 30


def reset_filters():
    st.session_state["attraction_filter"] = ["All attractions"]
    st.session_state["segment_filter"] = ["All segments"]
    st.session_state["activation_filter"] = ["All activation types"]
    st.session_state["rank_filter"] = default_rank_limit
    st.session_state["penetration_filter"] = 30


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

    play_options = ["All activation types"] + sorted(df["recommended_commercial_play"].dropna().unique().tolist())
    selected_plays = st.multiselect("Activation type", play_options, key="activation_filter")

    max_rank = int(df["opportunity_rank"].max())
    rank_limit = st.slider("Top opportunity areas", 1, max_rank, default_rank_limit, key="rank_filter")
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
    filtered_df = filtered_df.loc[filtered_df["recommended_commercial_play"].isin(selected_play_values)]

if not selected_attraction_values:
    map_attractions = attractions.copy()
else:
    map_attractions = attractions.loc[attractions["attraction_name"].isin(selected_attraction_values)].copy()

potential_revenue = filtered_potential_revenue(filtered_df, penetration_pct)
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
    metric_card("Revenue Scenario", currency_number(potential_revenue), f"{penetration_pct}% population x £33 revenue per visitor", MERLIN_GOLD)
with metric_cols[1]:
    metric_card("Clustering Opportunity", compact_number(cluster_population), f"Revenue scenario: {currency_number(cluster_revenue)}", MERLIN_AQUA)
with metric_cols[2]:
    metric_card("Annual Pass Opportunity", compact_number(annual_pass_population), f"Revenue scenario: {currency_number(annual_pass_revenue)}", MERLIN_BLUE)
with metric_cols[3]:
    metric_card("Short Break Opportunity", compact_number(short_break_population), f"Revenue scenario: {currency_number(short_break_revenue)}", "#7b61ff")
with metric_cols[4]:
    metric_card("Top Opportunity Area", top_area, top_area_note, MERLIN_PURPLE)
with metric_cols[5]:
    metric_card("Recommended Attraction", top_attraction, top_attraction_note, "#ff8a00")

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
    st.markdown(
        """
        <div class="map-legend">
            <span class="legend-item"><span class="legend-swatch" style="background: rgba(35, 182, 230, 0.75);"></span>Cluster marketing</span>
            <span class="legend-item"><span class="legend-swatch" style="background: rgba(255, 138, 0, 0.85);"></span>Annual pass</span>
            <span class="legend-item"><span class="legend-swatch" style="background: rgba(123, 97, 255, 0.75);"></span>Short break</span>
            <span class="legend-item"><span class="legend-swatch" style="background: rgba(130, 125, 155, 0.55);"></span>Other</span>
            <span class="legend-item"><span class="legend-attraction">M</span>Merlin attraction</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if filtered_df.empty:
        st.info("No MSOAs match the current filters.")
    else:
        st.pydeck_chart(build_map(filtered_df, map_attractions, penetration_pct), use_container_width=True, height=650)
