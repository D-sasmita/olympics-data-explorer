
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Country Comparison",
    page_icon="🌍",
    layout="wide",
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
    st.error(f"Unable to load the Olympic dataset: {exc}")
    st.stop()


# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("Country Comparison")
st.markdown(
    "Compare Olympic medal records and performance across countries "
    "from 1896 to 2016."
)

st.divider()


# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.header("Comparison Controls")

years = sorted(df["Year"].dropna().astype(int).unique().tolist())

year_range = st.sidebar.slider(
    "Olympic year range",
    min_value=min(years),
    max_value=max(years),
    value=(min(years), max(years)),
    key="comparison_year_range",
)

regions = sorted(df["Region"].dropna().unique().tolist())

default_countries = [
    country for country in ["USA", "China", "India", "Great Britain"]
    if country in regions
][:3]

selected_countries = st.sidebar.multiselect(
    "Select 2 to 5 countries",
    options=regions,
    default=default_countries,
    max_selections=5,
    key="comparison_countries",
)

if len(selected_countries) < 2:
    st.info("Select at least two countries in the sidebar to compare them.")
    st.stop()


# --------------------------------------------------
# Filter medal records
# --------------------------------------------------
medal_df = df[
    df["Region"].isin(selected_countries)
    & df["Year"].between(year_range[0], year_range[1])
    & df["Medal"].notna()
].copy()

medal_types = ["Gold", "Silver", "Bronze"]


# --------------------------------------------------
# Summary table
# --------------------------------------------------
st.subheader("Medal Summary")

if medal_df.empty:
    st.warning("No medal records match the selected countries and years.")
    st.stop()

summary = (
    medal_df.groupby(["Region", "Medal"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=medal_types, fill_value=0)
)

summary["Total"] = summary[medal_types].sum(axis=1)

summary = (
    summary.reindex(selected_countries)
    .fillna(0)
    .astype(int)
    .reset_index()
)

summary.index = summary.index + 1
summary.insert(0, "Rank", summary.index)

summary = summary.sort_values(
    ["Gold", "Silver", "Bronze"],
    ascending=False,
).reset_index(drop=True)

summary["Rank"] = range(1, len(summary) + 1)

# Country-level metric cards
st.subheader("Country Performance")

for start in range(0, len(selected_countries), 2):
    pair = selected_countries[start:start + 2]
    cols = st.columns(len(pair))

    for col, country in zip(cols, pair):
        country_row = summary[summary["Region"] == country]

        if country_row.empty:
            gold = silver = bronze = total = 0
        else:
            row = country_row.iloc[0]
            gold = int(row["Gold"])
            silver = int(row["Silver"])
            bronze = int(row["Bronze"])
            total = int(row["Total"])

        with col:
            st.markdown(f"#### {country}")
            m1, m2 = st.columns(2)
            m1.metric("Gold", f"{gold:,}")
            m2.metric("Silver", f"{silver:,}")
            m3, m4 = st.columns(2)
            m3.metric("Bronze", f"{bronze:,}")
            m4.metric("Total", f"{total:,}")

st.divider()


# --------------------------------------------------
# Medal type comparison
# --------------------------------------------------
st.subheader("Medal Type Comparison")

medal_comparison = summary.melt(
    id_vars="Region",
    value_vars=medal_types,
    var_name="Medal",
    value_name="Medal Records",
)

fig_medals = px.bar(
    medal_comparison,
    x="Region",
    y="Medal Records",
    color="Medal",
    barmode="group",
    text="Medal Records",
    title="Gold, Silver and Bronze Records by Country",
    color_discrete_map={
        "Gold": "#D4A017",
        "Silver": "#94A3B8",
        "Bronze": "#B77945",
    },
    labels={
        "Region": "Country / Region",
        "Medal Records": "Medal Records",
    },
)

fig_medals.update_layout(
    template="plotly_white",
    height=430,
    hovermode="x unified",
    margin=dict(l=20, r=20, t=70, b=30),
)

fig_medals.update_traces(
    textposition="outside",
    cliponaxis=False,
)

st.plotly_chart(
    fig_medals,
    width="stretch",
    config={"displaylogo": False, "responsive": True},
)


# --------------------------------------------------
# Medal performance over time
# --------------------------------------------------
st.subheader("Medal Performance Over Time")

yearly_medals = (
    medal_df.groupby(["Year", "Region"])
    .size()
    .reset_index(name="Medal Records")
)

fig_trend = px.line(
    yearly_medals,
    x="Year",
    y="Medal Records",
    color="Region",
    markers=True,
    title="Medal Records by Olympic Year",
    labels={
        "Year": "Olympic Year",
        "Medal Records": "Medal Records",
        "Region": "Country / Region",
    },
)

fig_trend.update_layout(
    template="plotly_white",
    height=450,
    hovermode="x unified",
    margin=dict(l=20, r=20, t=70, b=30),
)

st.plotly_chart(
    fig_trend,
    width="stretch",
    config={"displaylogo": False, "responsive": True},
)


# --------------------------------------------------
# Comparison table
# --------------------------------------------------
st.subheader("Detailed Comparison")

st.dataframe(
    summary,
    width="stretch",
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn(
            "Rank",
            format="%d",
        ),
        "Gold": st.column_config.NumberColumn(
            "Gold",
            format="%d",
        ),
        "Silver": st.column_config.NumberColumn(
            "Silver",
            format="%d",
        ),
        "Bronze": st.column_config.NumberColumn(
            "Bronze",
            format="%d",
        ),
        "Total": st.column_config.NumberColumn(
            "Total",
            format="%d",
        ),
    },
)

st.caption(
    "Medal counts represent athlete-event records, not distinct medals "
    "awarded. Team events may contribute records for multiple athletes."
)
