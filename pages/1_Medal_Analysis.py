
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_searchbox import st_searchbox
from utils.data_loader import load_data


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Olympics Analysis",
    page_icon="🏅",
    layout="wide",
)

# --------------------------------------------------
# Load data
# --------------------------------------------------
try:
    df = load_data()
except (FileNotFoundError, pd.errors.EmptyDataError) as exc:
    st.error(f"Unable to load the Olympic dataset: {exc}")
    st.stop()

# --------------------------------------------------
# Sidebar: navigation and filters
# --------------------------------------------------
st.sidebar.title("Olympics Analysis")

analysis_mode = st.sidebar.radio(
    "Select an Option",
    [
        "Medal Tally",
        "Overall Analysis",
        "Country-wise Analysis",
        "Athlete-wise Analysis",
    ],
)

st.sidebar.divider()

years = sorted(df["Year"].dropna().astype(int).unique().tolist())

selected_year = st.sidebar.selectbox(
    "Select Year",
    options=["Overall"] + years,
    index=0,
)

regions = sorted(df["Region"].dropna().unique().tolist())

selected_region = st.sidebar.selectbox(
    "Select Country",
    options=["Overall"] + regions,
    index=0,
)

# --------------------------------------------------
# Apply filters
# --------------------------------------------------
filtered_df = df.copy()

if selected_year != "Overall":
    filtered_df = filtered_df[
        filtered_df["Year"] == selected_year
    ]

if selected_region != "Overall":
    filtered_df = filtered_df[
        filtered_df["Region"] == selected_region
    ]

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# --------------------------------------------------
# Medal Tally
# --------------------------------------------------
if analysis_mode == "Medal Tally":
    st.title("Olympic Medal Tally")
    st.caption(
        "Explore medal records by region, ranked by gold, silver, "
        "and bronze records."
    )

    medal_df = filtered_df[filtered_df["Medal"].notna()].copy()

    if medal_df.empty:
        st.info("No medal records match the selected filters.")

    else:
        # Aggregate medal records by region
        medal_tally = (
            medal_df.groupby(["Region", "Medal"])
            .size()
            .unstack(fill_value=0)
            .reindex(
                columns=["Gold", "Silver", "Bronze"],
                fill_value=0
            )
        )

        medal_tally["Total"] = (
            medal_tally["Gold"]
            + medal_tally["Silver"]
            + medal_tally["Bronze"]
        )

        # Rank by gold, then silver, then bronze
        medal_tally = medal_tally.sort_values(
            ["Gold", "Silver", "Bronze"],
            ascending=False
        )

        medal_tally = medal_tally.reset_index()
        medal_tally.insert(
            0,
            "Rank",
            range(1, len(medal_tally) + 1)
        )

        # KPI summary
        st.subheader("Medal Summary")

        total_records = int(medal_df.shape[0])
        gold_total = int((medal_df["Medal"] == "Gold").sum())
        silver_total = int((medal_df["Medal"] == "Silver").sum())
        bronze_total = int((medal_df["Medal"] == "Bronze").sum())

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Medal Records", f"{total_records:,}")
        col2.metric("Gold Records", f"{gold_total:,}")
        col3.metric("Silver Records", f"{silver_total:,}")
        col4.metric("Bronze Records", f"{bronze_total:,}")

        st.divider()

        # Ranking chart
        st.subheader("Top 10 Regions")

        top_10 = (
            medal_tally.sort_values(
                ["Total", "Gold", "Silver", "Bronze"],
                ascending=False
            )
            .head(10)
            .sort_values("Total", ascending=True)
        )

        fig = px.bar(
            top_10,
            x="Total",
            y="Region",
            orientation="h",
            text="Total",
            title="Top 10 Regions by Medal Records",
            labels={
                "Total": "Medal Records",
                "Region": "Region"
            },
            color="Total",
            color_continuous_scale="Blues",
            hover_data=["Gold", "Silver", "Bronze"]
        )

        fig.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            template="plotly_white",
            showlegend=False,
            coloraxis_showscale=False,
            yaxis_title="",
            margin=dict(l=15, r=35, t=65, b=25)
        )

        fig.update_xaxes(
            rangemode="tozero",
            tickformat=","
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displaylogo": False, "responsive": True}
        )

        st.divider()

        # Complete medal tally table
        st.subheader("Complete Medal Rankings")

        display_tally = medal_tally.copy()

        # Add the overall total row only when all regions are selected
        if selected_region == "Overall":
            total_row = {
                "Rank": "-",
                "Region": "Overall Total",
                "Gold": gold_total,
                "Silver": silver_total,
                "Bronze": bronze_total,
                "Total": total_records
            }

            display_tally = pd.concat(
                [
                    display_tally,
                    pd.DataFrame([total_row])
                ],
                ignore_index=True
            )

        st.dataframe(
            display_tally,
            width="stretch",
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn(
                    "Rank",
                    format="%d"
                ),
                "Gold": st.column_config.NumberColumn(
                    "Gold",
                    format="%d"
                ),
                "Silver": st.column_config.NumberColumn(
                    "Silver",
                    format="%d"
                ),
                "Bronze": st.column_config.NumberColumn(
                    "Bronze",
                    format="%d"
                ),
                "Total": st.column_config.NumberColumn(
                    "Total",
                    format="%d"
                )
            }
        )

        st.caption(
            "Rankings are ordered by gold, then silver, then bronze. "
            "Counts represent athlete-event medal records, not "
            "distinct medals awarded."
        )

# --------------------------------------------------
# Overall Analysis
# --------------------------------------------------

elif analysis_mode == "Overall Analysis":
    st.title("Overall Olympic Analysis")

    # KPI metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Athlete Records",
        f"{len(filtered_df):,}"
    )

    col2.metric(
        "Unique Athletes",
        f"{filtered_df['ID'].nunique():,}"
    )

    col3.metric(
        "Regions",
        f"{filtered_df['Region'].nunique():,}"
    )

    col4.metric(
        "Sports",
        f"{filtered_df['Sport'].nunique():,}"
    )

    st.divider()

    # Participation by season and year
    st.subheader("Olympic Participation Over Time")

    participation = (
        filtered_df.groupby(["Year", "Season"])
        .agg(
            Unique_Athletes=("ID", "nunique"),
            Athlete_Entries=("ID", "size")
        )
        .reset_index()
    )

    fig = px.line(
        participation,
        x="Year",
        y="Unique_Athletes",
        color="Season",
        markers=True,
        title="Unique Athletes by Olympic Year",
        labels={
            "Year": "Olympic Year",
            "Unique_Athletes": "Unique Athletes",
            "Season": "Season"
        },
        hover_data=["Athlete_Entries"]
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Male vs female athlete-event records
    st.subheader("Participation by Sex")

    sex_data = (
        filtered_df.groupby("Sex")
        .size()
        .reset_index(name="Athlete Records")
    )

    col1, col2 = st.columns(2)

    with col1:
        fig_sex = px.pie(
            sex_data,
            names="Sex",
            values="Athlete Records",
            hole=0.45,
            title="Athlete Records by Sex"
        )

        fig_sex.update_layout(template="plotly_white")
        st.plotly_chart(fig_sex, use_container_width=True)

    with col2:
        # Sports and events represented in each Olympic year
        program_data = (
            filtered_df.groupby(["Year", "Season"])
            .agg(
                Sports=("Sport", "nunique"),
                Events=("Event", "nunique")
            )
            .reset_index()
        )

        fig_program = px.line(
            program_data,
            x="Year",
            y="Sports",
            color="Season",
            markers=True,
            title="Number of Sports Over Time",
            labels={
                "Year": "Olympic Year",
                "Sports": "Number of Sports",
                "Season": "Season"
            }
        )

        fig_program.update_layout(template="plotly_white")
        st.plotly_chart(fig_program, use_container_width=True)

    # Event count trend
    st.subheader("Olympic Events Over Time")

    fig_events = px.line(
        program_data,
        x="Year",
        y="Events",
        color="Season",
        markers=True,
        title="Number of Events Over Time",
        labels={
            "Year": "Olympic Year",
            "Events": "Number of Events",
            "Season": "Season"
        }
    )

    fig_events.update_layout(
        template="plotly_white",
        hovermode="x unified"
    )

    st.plotly_chart(fig_events, use_container_width=True)


# --------------------------------------------------
# Country-wise Analysis
# --------------------------------------------------

elif analysis_mode == "Country-wise Analysis":
    st.title("Country-wise Olympic Analysis")

    # Choose a region for analysis
    available_regions = sorted(
        df["Region"].dropna().unique().tolist()
    )

    default_region = (
        selected_region
        if selected_region != "Overall"
        else "USA" if "USA" in available_regions
        else available_regions[0]
    )

    chosen_region = st.selectbox(
        "Choose a region to analyze",
        options=available_regions,
        index=available_regions.index(default_region)
    )

    country_df = filtered_df[
        filtered_df["Region"] == chosen_region
    ]

    if country_df.empty:
        st.info(
            "No records match this region and the selected year filter."
        )
    else:
        country_medals = country_df[
            country_df["Medal"].notna()
        ]

        gold = int((country_medals["Medal"] == "Gold").sum())
        silver = int((country_medals["Medal"] == "Silver").sum())
        bronze = int((country_medals["Medal"] == "Bronze").sum())
        total = gold + silver + bronze

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Gold Records", f"{gold:,}")
        col2.metric("Silver Records", f"{silver:,}")
        col3.metric("Bronze Records", f"{bronze:,}")
        col4.metric("Total Medal Records", f"{total:,}")

        st.divider()

        # Medal records by Olympic year
        st.subheader(f"{chosen_region}: Medal Records Over Time")

        if country_medals.empty:
            st.info(
                "No medal records are available for this region "
                "under the selected filters."
            )
        else:
            yearly_medals = (
                country_medals.groupby(["Year", "Medal"])
                .size()
                .reset_index(name="Medal Records")
            )

            fig = px.line(
                yearly_medals,
                x="Year",
                y="Medal Records",
                color="Medal",
                markers=True,
                title=f"Medal Records by Year: {chosen_region}",
                color_discrete_map={
                    "Gold": "#E3B341",
                    "Silver": "#A7ADB4",
                    "Bronze": "#B87333"
                }
            )

            fig.update_layout(
                template="plotly_white",
                hovermode="x unified"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # Medal type composition
        if not country_medals.empty:
            medal_distribution = (
                country_medals["Medal"]
                .value_counts()
                .reindex(
                    ["Gold", "Silver", "Bronze"],
                    fill_value=0
                )
                .rename_axis("Medal")
                .reset_index(name="Medal Records")
            )

            fig = px.pie(
                medal_distribution,
                names="Medal",
                values="Medal Records",
                hole=0.45,
                title=f"Medal Record Distribution: {chosen_region}",
                color="Medal",
                color_discrete_map={
                    "Gold": "#E3B341",
                    "Silver": "#A7ADB4",
                    "Bronze": "#B87333"
                }
            )

            fig.update_layout(template="plotly_white")

            st.plotly_chart(
                fig,
                use_container_width=True
            )



#
# --------------------------------------------------
# Athlete-wise Analysis
# --------------------------------------------------
elif analysis_mode == "Athlete-wise Analysis":
    st.title("Athlete Analysis")
    st.write(
        "Search for an athlete or browse the list to explore "
        "their Olympic history."
    )

    # Build a unique athlete directory
    @st.cache_data
    def get_athlete_directory(data):
        return (
            data[["ID", "Name", "Region"]]
            .drop_duplicates(subset=["ID", "Name"])
            .sort_values("Name", key=lambda s: s.str.casefold())
            .reset_index(drop=True)
        )

    all_athletes = get_athlete_directory(df)

    # Update the selected athlete when a suggestion is clicked
    def choose_athlete(athlete_id):
        st.session_state["athlete_dropdown"] = athlete_id

    # Native Streamlit input with live updates
    search_text = st.text_input(
        "Search athlete by name",
        placeholder="Start typing, e.g. ab",
        key="athlete_search",
        live="300ms"
    ).strip()

    # Filter matches as the user types
    if search_text:
        matches = all_athletes[
            all_athletes["Name"].str.contains(
                search_text,
                case=False,
                na=False,
                regex=False
            )
        ].head(50)
    else:
        matches = all_athletes.head(50)

    if matches.empty:
        st.warning("No matching athletes found. Try another name.")

    else:
        athlete_options = {
            int(row["ID"]): (
                f"{row['Name']} | {row['Region']} | ID: {row['ID']}"
            )
            for _, row in matches.iterrows()
        }

        option_ids = list(athlete_options.keys())

        # Display clickable suggestions while searching
        if search_text:
            st.markdown("#### Suggestions")

            suggestion_rows = matches.head(10)
            suggestion_cols = st.columns(2)

            for i, (_, row) in enumerate(suggestion_rows.iterrows()):
                athlete_id = int(row["ID"])
                label = f"{row['Name']} | {row['Region']}"

                with suggestion_cols[i % 2]:
                    st.button(
                        label,
                        key=f"athlete_suggestion_{athlete_id}",
                        on_click=choose_athlete,
                        args=(athlete_id,),
                        use_container_width=True
                    )

        # Keep the selected value valid when search results change
        if (
            "athlete_dropdown" not in st.session_state
            or st.session_state["athlete_dropdown"] not in option_ids
        ):
            st.session_state["athlete_dropdown"] = option_ids[0]

        # Browseable dropdown remains available
        selected_id = st.selectbox(
            "Browse or select an athlete",
            options=option_ids,
            format_func=lambda athlete_id: athlete_options[athlete_id],
            key="athlete_dropdown"
        )

        # Retrieve the selected athlete's full Olympic history
        athlete_history = df[df["ID"] == selected_id].copy()

        if not athlete_history.empty:
            athlete_name = athlete_history["Name"].iloc[0]
            athlete_region = athlete_history["Region"].iloc[0]

            st.divider()
            st.subheader(f"Olympic History: {athlete_name}")
            st.caption(f"Represented region: {athlete_region}")

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Olympic Games",
                athlete_history["Games"].nunique()
            )
            col2.metric(
                "Sports",
                athlete_history["Sport"].nunique()
            )
            col3.metric(
                "Events",
                athlete_history["Event"].nunique()
            )
            col4.metric(
                "Medal Records",
                int(athlete_history["Medal"].notna().sum())
            )

            # Medal summary
            st.divider()
            st.subheader("Medal Summary")

            medal_counts = (
                athlete_history["Medal"]
                .value_counts()
                .reindex(
                    ["Gold", "Silver", "Bronze"],
                    fill_value=0
                )
            )

            medal_col1, medal_col2, medal_col3 = st.columns(3)

            medal_col1.metric("Gold", int(medal_counts["Gold"]))
            medal_col2.metric("Silver", int(medal_counts["Silver"]))
            medal_col3.metric("Bronze", int(medal_counts["Bronze"]))

            # Participation history
            st.subheader("Participation Details")

            history_display = athlete_history[
                ["Year", "Season", "Team", "Sport", "Event", "Medal"]
            ].sort_values(
                ["Year", "Season", "Sport", "Event"]
            )

            st.dataframe(
                history_display,
                width="stretch",
                hide_index=True
            )
