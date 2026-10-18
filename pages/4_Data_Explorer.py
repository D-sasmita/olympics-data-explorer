
import streamlit as st
import pandas as pd

from utils.data_loader import load_data


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Olympics Data Explorer",
    page_icon="🔎",
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
st.title("Olympics Data Explorer")

st.markdown(
    "Explore, filter, inspect, and download Olympic athlete-event records "
    "from 1896 to 2016."
)

st.divider()


# --------------------------------------------------
# Search and filters
# --------------------------------------------------
st.sidebar.header("Explore the Dataset")

search_name = st.sidebar.text_input(
    "Search athlete name",
    placeholder="e.g. Abhinav Bindra",
)

available_years = sorted(
    df["Year"].dropna().astype(int).unique().tolist()
)

year_range = st.sidebar.slider(
    "Olympic year range",
    min_value=min(available_years),
    max_value=max(available_years),
    value=(min(available_years), max(available_years)),
)

seasons = sorted(df["Season"].dropna().unique().tolist())

selected_seasons = st.sidebar.multiselect(
    "Season",
    options=seasons,
    default=seasons,
)

regions = sorted(df["Region"].dropna().unique().tolist())

selected_regions = st.sidebar.multiselect(
    "Region",
    options=regions,
)

sports = sorted(df["Sport"].dropna().unique().tolist())

selected_sports = st.sidebar.multiselect(
    "Sport",
    options=sports,
)

sexes = sorted(df["Sex"].dropna().unique().tolist())

selected_sexes = st.sidebar.multiselect(
    "Sex",
    options=sexes,
    default=sexes,
)

medal_options = ["Gold", "Silver", "Bronze", "No Medal"]

selected_medals = st.sidebar.multiselect(
    "Medal",
    options=medal_options,
    default=medal_options,
)

st.sidebar.caption(
    "Leave Region or Sport empty to include all available options."
)


# --------------------------------------------------
# Apply filters
# --------------------------------------------------
filtered = df[
    df["Year"].between(year_range[0], year_range[1])
    & df["Season"].isin(selected_seasons)
    & df["Sex"].isin(selected_sexes)
].copy()

if selected_regions:
    filtered = filtered[filtered["Region"].isin(selected_regions)]

if selected_sports:
    filtered = filtered[filtered["Sport"].isin(selected_sports)]

if search_name.strip():
    filtered = filtered[
        filtered["Name"].str.contains(
            search_name.strip(),
            case=False,
            na=False,
            regex=False,
        )
    ]

if selected_medals:
    medal_mask = (
        filtered["Medal"].isin(
            [medal for medal in selected_medals if medal != "No Medal"]
        )
    )

    if "No Medal" in selected_medals:
        medal_mask = medal_mask | filtered["Medal"].isna()

    filtered = filtered[medal_mask]
else:
    filtered = filtered.iloc[0:0]


# --------------------------------------------------
# Summary metrics
# --------------------------------------------------
st.subheader("Filtered Dataset Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Records", f"{len(filtered):,}")
col2.metric("Unique Athletes", f"{filtered['ID'].nunique():,}")
col3.metric("Regions", f"{filtered['Region'].nunique():,}")
col4.metric("Sports", f"{filtered['Sport'].nunique():,}")

st.divider()


# --------------------------------------------------
# Data table
# --------------------------------------------------
st.subheader("Olympic Records")

st.caption(
    "Each row represents an athlete's participation in an Olympic event."
)

if filtered.empty:
    st.warning(
        "No records match these filters. Try broadening your search."
    )
else:
    # Table display settings
    display_columns = [
        "Name",
        "Sex",
        "Age",
        "Height",
        "Weight",
        "Team",
        "Region",
        "Year",
        "Season",
        "Sport",
        "Event",
        "Medal",
    ]

    available_columns = [
        column for column in display_columns
        if column in filtered.columns
    ]

    st.dataframe(
        filtered[available_columns],
        width="stretch",
        hide_index=True,
        height=500,
        column_config={
            "Year": st.column_config.NumberColumn(
                "Year",
                format="%d",
            ),
            "Age": st.column_config.NumberColumn(
                "Age",
                format="%d",
            ),
        },
    )

    st.caption(
        f"Showing {len(filtered):,} matching records."
    )


    # --------------------------------------------------
    # Download filtered data
    # --------------------------------------------------
    st.subheader("Export Data")

    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered records (CSV)",
        data=csv_data,
        file_name="olympics_filtered_data.csv",
        mime="text/csv",
        use_container_width=True,
    )


# --------------------------------------------------
# Data note
# --------------------------------------------------
st.divider()

st.caption(
    "Dataset: 120 Years of Olympic History: Athletes and Results "
    "(1896–2016). Medal values represent athlete-event records, "
    "not necessarily distinct medals awarded."
)
