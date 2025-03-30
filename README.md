# ExoExplorers Orion - Light Pollution Analysis Project

This repository contains a comprehensive analysis of light pollution trends in India using VIIRS satellite data and population growth statistics. The project includes interactive visualizations, temporal analysis, and future predictions.

## Project Structure

```
ExoExplorers_Orion/
├── src/
│   ├── data/
│   │   ├── viirs/         # VIIRS satellite data (2014-2023)
│   │   ├── population/    # World Bank population growth data
│   │   └── boundaries/    # India boundary GeoJSON
│   ├── scripts/
│   │   ├── heatmap/       # Heatmap generation and analysis scripts
│   │   │   ├── 2014.py - 2023.py    # Year-specific heatmap scripts
│   │   │   ├── predicted_2025.py - predicted_2029.py  # Future predictions
│   │   │   ├── temporal_analysis.py  # Basic temporal analysis
│   │   │   ├── temporal_analysis_robust.py  # Advanced temporal analysis
│   │   │   ├── analyze_without_outliers.py  # Outlier analysis
│   │   │   └── update_year_scripts.py  # Script updater
│   │   └── analysis/
│   │       └── population_light_correlation.py  # Population correlation analysis
│   ├── app.py            # Streamlit web application
│   └── future_predictions.csv  # Generated future predictions
├── docs/
│   └── visualizations/
│       ├── heatmaps/      # Generated heatmap visualizations
│       └── analysis/      # Analysis results and plots
└── requirements.txt       # Project dependencies
```

## Data Sources

1. VIIRS Satellite Data (2014-2023)
   - Annual light pollution measurements for India
   - Resolution: 15 arc-second (approximately 500m)
   - Source: NASA VIIRS Day-Night Band
   - Format: CSV with lat/lon coordinates and radiance values

2. Population Growth Data
   - World Bank population growth statistics
   - Annual percentage growth rates
   - Period: 2014-2023
   - Source: World Bank Open Data

3. Geographic Data
   - India boundary GeoJSON
   - Used for spatial analysis and visualization

## Analysis Components

1. Light Pollution Analysis
   - Temporal analysis of light pollution trends
   - Regional variation studies
   - Outlier detection and management
   - Future predictions (2025-2029)

2. Population Correlation
   - Population growth trends
   - Correlation with light pollution
   - Statistical significance testing
   - Regional analysis

3. Interactive Visualization
   - Web-based heatmap interface
   - Location-specific light pollution checking
   - Dark sky suitability assessment

## Key Findings

1. Light Pollution Trends
   - Overall increase of 146% from 2014 to 2023
   - Significant spike observed in 2018 (75.09% increase)
   - Regional variations identified between All India and East India
   - Outlier removal significantly improved data quality

2. Population Growth Correlation
   - Average population growth rate: 1.042%
   - Strong negative correlation (-0.800) with light pollution
   - Indicates inverse relationship between population growth and light pollution
   - Regional variations in correlation patterns

3. Future Predictions
   - Projected light pollution trends for 2025-2029
   - Based on historical patterns and statistical models
   - Includes confidence intervals and uncertainty measures

## Setup and Usage

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the web application:
   ```bash
   python -m streamlit run src/app.py
   ```
5. Run analysis scripts:
   ```bash
   python src/scripts/heatmap/temporal_analysis_robust.py
   python src/scripts/analysis/population_light_correlation.py
   ```

## Dependencies

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- plotly
- statsmodels
- streamlit
- folium
- geopandas
- shapely
- geopy

## Features

1. Interactive Web Interface
   - Year selection (2014-2023)
   - Location-specific light pollution checking
   - Dark sky suitability assessment
   - Customizable visualization parameters

2. Analysis Tools
   - Robust statistical analysis
   - Outlier detection and removal
   - Temporal trend analysis
   - Population correlation studies
   - Future predictions

3. Visualization Options
   - Heatmap generation
   - Trend plots
   - Distribution analysis
   - Correlation scatter plots
   - Regional comparisons

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.