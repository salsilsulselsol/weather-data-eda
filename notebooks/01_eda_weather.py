import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Project Configuration and Imports

    This section initializes the Python environment by importing the necessary libraries for data manipulation (Pandas, NumPy) and interaction (Marimo).

    It also defines the directory structure (`../data/raw` and `../data/processed`) to ensure file path consistency throughout the analysis pipeline.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import os

    # Define project-level constants
    RAW_DATA_PATH = "../data/raw/weather_mock.csv"
    PROCESSED_DATA_PATH = "../data/processed/"

    # Ensure the directory structure exists
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    return RAW_DATA_PATH, mo, os, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Data Acquisition: Seattle Weather Dataset

    Instead of generating synthetic data, we fetch a real-world dataset: **Seattle Weather**.

    **Source**: [Vega Datasets Repository](https://github.com/vega/vega-datasets)
    **Attributes**:
    * `date`: Observation date.
    * `precipitation`: Amount of rain.
    * `temp_max`: Maximum daily temperature.
    * `temp_min`: Minimum daily temperature.
    * `wind`: Wind speed.
    * `weather`: Categorical description (rain, sun, drizzle, etc.).

    The data is downloaded programmatically and cached locally in `../data/raw/` to ensure offline reproducibility.
    """)
    return


@app.cell
def _(RAW_DATA_PATH, os, pd):
    def fetch_weather_data():
        """
        Downloads the Seattle Weather dataset from the remote repository
        if it does not already exist locally.
    
        Returns:
            pd.DataFrame: The raw weather dataset.
        """
        url = "https://raw.githubusercontent.com/vega/vega-datasets/next/data/seattle-weather.csv"
        local_path = os.path.join(os.path.dirname(RAW_DATA_PATH), "seattle-weather.csv")
    
        # Check if data exists locally (Caching)
        if os.path.exists(local_path):
            print(f"Loading data from local cache: {local_path}")
            df = pd.read_csv(local_path)
        else:
            print(f"Downloading data from {url}...")
            df = pd.read_csv(url)
            df.to_csv(local_path, index=False)
            print(f"Data saved to {local_path}")
        
        return df

    # Execute ingestion
    df_weather = fetch_weather_data()
    return (df_weather,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Data Ingestion and Preview

    Loads the generated CSV file into a Pandas DataFrame and performs initial type conversion (String to Datetime).

    The table below provides an interactive view of the raw data structure, allowing for sorting and inspection of values.
    """)
    return


@app.cell
def _(df_weather, mo, pd):
    # Load data into main DataFrame variable
    df = df_weather.copy()

    # Ensure date column is datetime type
    df['date'] = pd.to_datetime(df['date'])

    # Display interactive table
    mo.ui.table(df, selection=None, pagination=True)
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Interactive Analysis: Temperature Range & Precipitation

    This section visualizes the daily weather dynamics using a dual-chart layout:

    1.  **Temperature Range (Top)**: Uses an area chart to display the span between the daily minimum (`temp_min`) and maximum (`temp_max`) temperatures. This helps identify seasonal trends and daily volatility.

    2.  **Precipitation (Bottom)**: Displays daily rainfall (`precipitation`) using a bar chart.

    **Interaction**:
    * **Brush & Filter**: Dragging across the Temperature chart will define a specific time window.
    * **Linked View**: The Precipitation chart automatically updates to show data only for the selected period, allowing for focused analysis of rainy seasons.
    """)
    return


@app.cell
def _(df):
    import altair as alt

    # Create a selection interval for the interaction
    brush = alt.selection_interval()

    # 1. Temperature Range Chart (Top)
    # Visualizes the band between Min and Max temps
    temp_chart = alt.Chart(df).mark_area(opacity=0.6, color='#ff7f0e').encode(
        x=alt.X('date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('temp_max:Q', title='Temperature (°C)'),
        y2='temp_min:Q',
        tooltip=['date', 'temp_max', 'temp_min', 'weather']
    ).properties(
        width='container',
        height=300,
        title='Daily Temperature Range (Min - Max)'
    ).add_params(
        brush
    )

    # 2. Precipitation Chart (Bottom)
    # Visualizes rainfall amount
    precip_chart = alt.Chart(df).mark_bar(color='#1f77b4').encode(
        x=alt.X('date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('precipitation:Q', title='Precipitation (mm)'),
        tooltip=['date', 'precipitation', 'weather'],
        color=alt.condition(
            alt.datum.precipitation > 0, 
            alt.value("#1f77b4"),  # Blue if raining
            alt.value("#e7ba52")   # Yellowish if dry (0 mm)
        )
    ).properties(
        width='container',
        height=150,
        title='Daily Precipitation'
    ).transform_filter(
        brush
    )

    # Vertical Concatenation
    dashboard = alt.vconcat(temp_chart, precip_chart).resolve_scale(
        x='shared'
    )

    dashboard
    return (alt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Advanced Visualization: Temperature Calendar Heatmap

    This visualization moves beyond simple line charts to a **Calendar Heatmap**. This format allows us to visualize daily temperature intensity across the entire year in a grid layout.

    **Visual Encoding:**
    * **X-Axis**: Day of the month.
    * **Y-Axis**: Month of the year.
    * **Color**: Maximum Temperature (`temp_max`). Darker/Redder colors indicate hotter days.
    * **Facet**: Split by `year` to compare year-over-year patterns.

    **Insight**: This view instantly highlights seasonal transitions (e.g., when summer starts) and anomalies (e.g., a hot week in winter).
    """)
    return


@app.cell
def _(alt, df):
    # Base chart configuration
    base = alt.Chart(df).mark_rect().encode(
        x=alt.X('date(date):O', title='Day'),
        y=alt.Y('month(date):O', title='Month'),
        color=alt.Color('temp_max:Q', scale=alt.Scale(scheme='inferno'), title='Max Temp (°C)'),
        tooltip=[
            alt.Tooltip('date:T', title='Date'),
            alt.Tooltip('temp_max:Q', title='Max Temp'),
            alt.Tooltip('weather:N', title='Condition')
        ]
    ).properties(
        width=300,
        height=300
    )

    # Facet by year to separate the grids
    heatmap = base.facet(
        column=alt.Column('year(date):O', title=None)
    ).resolve_scale(
        x='independent'
    ).properties(
        title='Daily Maximum Temperature Heatmap (Yearly View)'
    )

    heatmap
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Multivariate Analysis: Wind vs. Rain vs. Temperature

    This **Bubble Chart** visualizes the relationship between three different weather variables simultaneously:

    1.  **X-Axis**: Wind Speed.
    2.  **Y-Axis**: Precipitation (Rainfall).
    3.  **Size**: Maximum Temperature (Larger bubbles = Hotter).
    4.  **Color**: Weather Condition (e.g., Sun, Rain, Fog).

    **Objective**: To detect correlations, such as:
    * *"Does high wind speed usually accompany heavy rain?"*
    * *"Are rainy days generally colder (smaller bubbles)?"*
    """)
    return


@app.cell
def _(alt, df):
    # Create a selection for interactivity (Click on legend to filter)
    selection = alt.selection_point(fields=['weather'], bind='legend')

    bubble_chart = alt.Chart(df).mark_circle().encode(
        x=alt.X('wind:Q', title='Wind Speed'),
        y=alt.Y('precipitation:Q', title='Precipitation'),
        size=alt.Size('temp_max:Q', scale=alt.Scale(range=[10, 200]), title='Temp Max'),
        color=alt.Color('weather:N', scale=alt.Scale(scheme='category10')),
        opacity=alt.condition(selection, alt.value(0.8), alt.value(0.2)),
        tooltip=['date', 'weather', 'wind', 'precipitation', 'temp_max']
    ).properties(
        width='container',
        height=400,
        title='Multivariate Correlation: Wind, Rain, and Temperature'
    ).add_params(
        selection
    ).interactive() # Allows zooming and panning

    bubble_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Analysis Summary & Conclusion

    Based on the comprehensive visual analysis (Heatmap, Time Series, and Multivariate Plot), here are the verified patterns:

    1.  **Temperature Trend (Heatmap)**:
        * **Hot Season**: The brightest yellow blocks confirm that **July and August** are consistently the hottest months.
        * **Cold Season**: The darkest areas indicate that **December, January, and February** are the coldest.

    2.  **Precipitation Seasonality (Time Series)**:
        * Seattle follows a distinct **"Wet Winter, Dry Summer"** pattern.
        * Rainfall peaks significantly in **Q4 and Q1** (October–March), while the middle of the year (June–August) sees almost zero precipitation.

    3.  **Weather Dynamics (Bubble Plot)**:
        * **Heavy Rain Profile**: Heavy rainfall events (>20mm) are exclusively categorized as **"Rain" (Green bubbles)** and typically coincide with moderate-to-high wind speeds (3.0 - 7.0).
        * **Low Intensity Events**: **"Snow" (Red)** and **"Drizzle" (Blue)** are clustered at low precipitation levels (<10mm), suggesting they rarely bring heavy water accumulation compared to rain storms.
        * **Data Integrity**: "Sun" (Purple) remains flat at 0 precipitation, confirming consistent data labeling.

    **Actionable Insight for Modeling**:
    * **Feature Importance**: `Month` will be the strongest predictor for temperature.
    * **Interaction Effect**: High `Wind` speed combined with specific months (Winter) is a strong indicator of heavy rainfall intensity.
    """)
    return


if __name__ == "__main__":
    app.run()
