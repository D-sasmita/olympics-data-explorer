## Live Demo

Explore the deployed dashboard:

[**Launch Olympics Data Explorer**](https://olympics-data-explorer-dznxkcahqebghbhaiuhmjm.streamlit.app/)

[View Source Code on GitHub](https://github.com/D-sasmita/olympics-data-explorer)

# Olympics Data Explorer

An interactive dashboard for exploring Olympic history, athlete participation, and medal statistics using Python, Pandas, Plotly, and Streamlit.

## Features

- **Olympics Dashboard:** Explore participation trends, medal distributions, and top-performing regions.
- **Medal Analysis:** Analyze medal tallies, overall statistics, country-wise performance, and athlete-level results.
- **Country Comparison:** Compare multiple countries or regions across medal counts and historical trends.
- **Data Explorer:** Filter Olympic records by athlete, year, season, region, sport, gender, and medal type.
- **Interactive Visualizations:** Explore historical data through interactive charts and tables.
- **Data Analysis:** Use Jupyter notebooks to document exploratory data analysis and data cleaning.

## Tech Stack

- Python
- Pandas and NumPy
- Streamlit
- Plotly
- Jupyter Notebook

## Dataset

This project uses the **120 Years of Olympic History: Athletes and Results** dataset, covering Olympic athlete events from 1896 to 2016.

The dataset includes athlete information, participating teams, sports, events, Olympic editions, and medal results.

## Project Structure

```text
olympics-data-explorer/
├── analysis/
│   ├── eda.ipynb
│   └── olympics_data_analysis.ipynb
├── data/
│   ├── raw/
│   └── processed/
├── pages/
│   ├── 1_Medal_Analysis.py
│   ├── 3_Country_Comparison.py
│   └── 4_Data_Explorer.py
├── utils/
│   └── data_loader.py
├── app.py
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/D-sasmita/olympics-data-explorer.git
cd olympics-data-explorer
```

### 2. Create and activate a Conda environment

```bash
conda create -n olympics python=3.11
conda activate olympics
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the dataset

Download the dataset and place the files in the expected locations:

- `data/raw/athlete_events.csv`
- `data/raw/noc_regions.csv`

Ensure the cleaned dataset is available at:

- `data/processed/athlete_events_clean.csv`

The raw and processed CSV files are excluded from Git, so you must obtain or generate them locally before running the application.

### 5. Launch the dashboard

```bash
streamlit run app.py
```

Streamlit will provide a local URL where you can explore the dashboard.

## Exploratory Data Analysis

The `analysis/` directory contains Jupyter notebooks documenting the exploratory analysis and cleaning stages of the project.

## Future Improvements
- Add more historical comparisons and insights.
- Improve data storytelling with additional visualizations.

## Author

**Sasmita Das**

- GitHub: [D-sasmita](https://github.com/D-sasmita)
