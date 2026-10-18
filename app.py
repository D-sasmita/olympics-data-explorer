
import pandas as pd
import streamlit as st
import plotly.express as px

from utils.data_loader import load_data


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Olympics Data Explorer",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Custom styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .dashboard-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }

    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.18);
        padding: 18px 20px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 650;
    }

    div[data-testid="stPlotlyChart"] {
        border: 1px solid rgba(128, 128, 128, 0.16);
        border-radius: 12px;
        padding: 8px;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.15);
    }

    h2, h3 {
        letter-spacing: -0.02em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def get_data():
    return load_data()


try:
    df = get_data()
except (FileNotFoundError, pd.errors.EmptyDataError) as exc:
    st.error(f"Could not load the cleaned dataset: {exc}")
    st.stop()
except Exception as exc:
    st.error(f"Unexpected error while loading data: {exc}")
    st.stop()


# --------------------------------------------------
# Dashboard header
# --------------------------------------------------
st.title("Olympics Data Explorer")

st.markdown(
    """
    <div class="dashboard-subtitle">
        Explore 120 years of Olympic history through athlete participation,
        medal records, and country-level performance.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()



# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.title("Dashboard Controls")
st.sidebar.caption("Customize the Olympic data shown below.")
st.sidebar.divider()

seasons = sorted(df["Season"].dropna().unique().tolist())
years = sorted(df["Year"].dropna().astype(int).unique().tolist())

if not years:
    st.error("No valid Olympic years were found in the dataset.")
    st.stop()

# Reset button: reset widget state before the next rerun
if st.sidebar.button("Reset filters", use_container_width=True):
    st.session_state["season_filter"] = seasons
    st.session_state["year_range_filter"] = (min(years), max(years))
    st.rerun()

# Season filter
selected_seasons = st.sidebar.multiselect(
    "Olympic season",
    options=seasons,
    default=seasons,
    key="season_filter",
)

# Year-range filter
selected_years = st.sidebar.slider(
    "Olympic year range",
    min_value=min(years),
    max_value=max(years),
    value=(min(years), max(years)),
    step=1,
    key="year_range_filter",
)

# --------------------------------------------------
# Filter dataset
# --------------------------------------------------
filtered = df[
    df["Season"].isin(selected_seasons)
    & df["Year"].between(selected_years[0], selected_years[1])
].copy()

if filtered.empty:
    st.warning(
        "No records match your selected filters. "
        "Try selecting another season or year range."
    )
    st.stop()

medal_df = filtered[filtered["Medal"].notna()].copy()


# --------------------------------------------------
# KPI metrics
# --------------------------------------------------
st.subheader("At a glance")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.metric(
        "Athlete Records",
        f"{len(filtered):,}",
        help="Number of athlete-event records after filtering.",
    )

with col2:
    st.metric(
        "Unique Athletes",
        f"{filtered['ID'].nunique():,}",
        help="Distinct athlete IDs represented in the filtered data.",
    )

with col3:
    st.metric(
        "Regions",
        f"{filtered['Region'].nunique():,}",
        help="Distinct regions represented in the filtered data.",
    )

with col4:
    st.metric(
        "Medal Records",
        f"{len(medal_df):,}",
        help=(
            "Athlete-event records with a medal. "
            "Team events can contribute records for multiple athletes."
        ),
    )

st.divider()


# --------------------------------------------------
# Chart styling helper
# --------------------------------------------------
def style_chart(fig, height=380):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=65, b=25),
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="#334155",
        ),
        title=dict(
            x=0.02,
            xanchor="left",
            font=dict(size=17, color="#0f172a"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial, sans-serif",
        ),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#e9edf2",
        zeroline=False,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e9edf2",
        zeroline=False,
    )

    return fig


# --------------------------------------------------
# Olympic participation trend
# --------------------------------------------------
st.subheader("Olympic Participation")

st.caption(
    "Track the number of unique athletes participating in each Olympic year."
)

participation = (
    filtered.groupby(["Year", "Season"])
    .agg(
        Unique_Athletes=("ID", "nunique"),
        Athlete_Entries=("ID", "size"),
    )
    .reset_index()
)

fig_participation = px.line(
    participation,
    x="Year",
    y="Unique_Athletes",
    color="Season",
    markers=True,
    title="Athlete Participation Over Time",
    labels={
        "Year": "Olympic Year",
        "Unique_Athletes": "Unique Athletes",
        "Season": "Season",
        "Athlete_Entries": "Athlete-Event Records",
    },
    hover_data={
        "Athlete_Entries": ":,",
        "Unique_Athletes": ":,",
        "Year": True,
        "Season": True,
    },
    color_discrete_map={
        "Summer": "#2563eb",
        "Winter": "#0f9d8a",
    },
)

fig_participation.update_traces(
    line=dict(width=3),
    marker=dict(size=6),
)

fig_participation.update_yaxes(
    rangemode="tozero",
    tickformat=",",
)

style_chart(fig_participation, height=430)

st.plotly_chart(
    fig_participation,
    width="stretch",
    config={"displaylogo": False, "responsive": True},
)


# --------------------------------------------------
# Medal analysis
# --------------------------------------------------
st.divider()
st.subheader("Medal Analysis")

st.caption(
    "Explore medal records by medal type and compare the top-performing regions."
)

if medal_df.empty:
    st.info("No medal records are available for the selected filters.")
else:
    medal_summary = (
        medal_df["Medal"]
        .value_counts()
        .reindex(["Gold", "Silver", "Bronze"], fill_value=0)
        .rename_axis("Medal")
        .reset_index(name="Medal Records")
    )

    left, right = st.columns(2, gap="large")

    # Medal distribution
    with left:
        fig_medals = px.bar(
            medal_summary,
            x="Medal",
            y="Medal Records",
            color="Medal",
            title="Medal Records by Type",
            text="Medal Records",
            color_discrete_map={
                "Gold": "#D4A017",
                "Silver": "#94A3B8",
                "Bronze": "#B77945",
            },
            labels={
                "Medal": "Medal Type",
                "Medal Records": "Number of Records",
            },
        )

        fig_medals.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            cliponaxis=False,
        )

        fig_medals.update_layout(
            showlegend=False,
            uniformtext_minsize=10,
            uniformtext_mode="hide",
        )

        fig_medals.update_yaxes(
            rangemode="tozero",
            tickformat=",",
        )

        style_chart(fig_medals, height=380)

        st.plotly_chart(
            fig_medals,
            width="stretch",
            config={"displaylogo": False, "responsive": True},
        )

    # Top 10 regions
    with right:
        top_regions = (
            medal_df.groupby("Region")
            .size()
            .sort_values(ascending=False)
            .head(10)
            .rename("Medal Records")
            .reset_index()
            .sort_values("Medal Records", ascending=True)
        )

        fig_regions = px.bar(
            top_regions,
            x="Medal Records",
            y="Region",
            orientation="h",
            title="Top 10 Regions by Medal Records",
            text="Medal Records",
            labels={
                "Region": "Region",
                "Medal Records": "Number of Records",
            },
            color_discrete_sequence=["#2563eb"],
        )

        fig_regions.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            cliponaxis=False,
        )

        fig_regions.update_layout(
            showlegend=False,
        )

        fig_regions.update_xaxes(
            rangemode="tozero",
            tickformat=",",
        )

        style_chart(fig_regions, height=380)

        st.plotly_chart(
            fig_regions,
            width="stretch",
            config={"displaylogo": False, "responsive": True},
        )


# --------------------------------------------------
# Data note
# --------------------------------------------------
st.divider()

st.caption(
    "Source: 120 Years of Olympic History: Athletes and Results "
    "(1896–2016). Medal counts represent athlete-event records, "
    "not distinct medals awarded. Team events may contribute records "
    "for multiple athletes."
)
