from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "athlete_events_clean.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the cleaned Olympic athlete-event dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at {DATA_PATH}. "
            "Run the data-cleaning notebook first."
        )

    df = pd.read_csv(DATA_PATH)

    # Ensure numeric fields have numeric types.
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Height"] = pd.to_numeric(df["Height"], errors="coerce")
    df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce")

    return df
