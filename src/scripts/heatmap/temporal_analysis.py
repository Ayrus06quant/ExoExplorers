import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from shapely.geometry import Point
import json
import folium
from folium.plugins import HeatMap
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from scipy import stats
from datetime import datetime

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set paths
boundary_file = os.path.join(project_root, "data", "boundaries", "india_boundary.geojson")
output_dir = os.path.join(project_root, "docs", "visualizations", "analysis")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load India boundary
india = gpd.read_file(boundary_file)

def print_progress(message):
    print(f"\n>>> {message}")
    sys.stdout.flush()

# Function to load and process data for a given year
def load_year_data(year):
    try:
        print_progress(f"Loading data for year {year}")
        
        # Load data using absolute path
        data_file = os.path.join(project_root, "data", "viirs", f"VIIRS_India_{year}.csv")
        if not os.path.exists(data_file):
            print(f"Error: Could not find file {data_file}")
            return None
            
        print(f"Reading file: {data_file}")
        df = pd.read_csv(data_file)
        
        # Extract coordinates
        def extract_coords(geo_str):
            geo_json = json.loads(geo_str)
            lon, lat = geo_json["coordinates"]
            return pd.Series([lat, lon])
        
        df[['Latitude', 'Longitude']] = df['.geo'].apply(extract_coords)
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']),
            crs="EPSG:4326"
        )
        
        # Spatial join: Keep only points within India
        gdf = gpd.sjoin(gdf, india, predicate='within')
        
        return gdf
    except Exception as e:
        print(f"Error loading data for year {year}: {str(e)}")
        return None

def create_difference_heatmap(data_2014, data_2023):
    try:
        print_progress("Creating difference heatmap")
        # Create a grid for India
        boundary_path = os.path.join(project_root, "data", "boundaries", "india_boundary.geojson")
        india = gpd.read_file(boundary_path)
        bounds = india.total_bounds
        
        # Create grid points
        x = np.linspace(bounds[0], bounds[2], 100)
        y = np.linspace(bounds[1], bounds[3], 100)
        xx, yy = np.meshgrid(x, y)
        
        # Calculate average radiance for each grid cell
        def get_grid_values(data, xx, yy):
            values = np.zeros_like(xx)
            for i in range(len(xx)):
                for j in range(len(xx[0])):
                    mask = ((data['Longitude'] - xx[i,j])**2 + 
                           (data['Latitude'] - yy[i,j])**2 < 0.1)
                    if mask.any():
                        values[i,j] = data.loc[mask, 'avg_rad'].mean()
            return values
        
        print_progress("Calculating grid values for 2014")
        values_2014 = get_grid_values(data_2014, xx, yy)
        print_progress("Calculating grid values for 2023")
        values_2023 = get_grid_values(data_2023, xx, yy)
        
        # Calculate difference
        diff = values_2023 - values_2014
        
        # Create difference heatmap
        m = folium.Map(location=[22.9734, 78.6569], zoom_start=5,
                       tiles='CartoDB dark_matter')
        
        # Convert difference to heatmap format
        heat_data = []
        for i in range(len(xx)):
            for j in range(len(xx[0])):
                if diff[i,j] != 0:
                    heat_data.append([yy[i,j], xx[i,j], diff[i,j]])
        
        # Add heatmap layer
        HeatMap(
            heat_data,
            radius=15,
            blur=10,
            min_opacity=0.3,
            max_zoom=6,
            gradient={
                '0.4': 'blue',
                '0.6': 'lime',
                '0.8': 'yellow',
                '1.0': 'red'
            }
        ).add_to(m)
        
        # Save with absolute path
        output_path = os.path.join(output_dir, "light_pollution_difference_2014_2023.html")
        print_progress(f"Saving difference heatmap to {output_path}")
        m.save(output_path)
    except Exception as e:
        print(f"Error creating difference heatmap: {str(e)}")

if __name__ == "__main__":
    print(f"Script directory: {project_root}")
    try:
        # Load data for all years
        print_progress("Starting data loading for all years")
        years = range(2014, 2024)
        yearly_data = {}
        
        for year in years:
            data = load_year_data(year)
            if data is not None:
                yearly_data[year] = data
            else:
                print(f"Skipping year {year} due to missing or invalid data")
        
        if len(yearly_data) == 0:
            print("No data could be loaded. Please check file paths.")
            exit(1)
        
        # Calculate yearly statistics
        print_progress("Calculating yearly statistics")
        yearly_stats = pd.DataFrame({
            'Year': list(yearly_data.keys()),
            'Mean_Radiance': [data['avg_rad'].mean() for data in yearly_data.values()],
            'Median_Radiance': [data['avg_rad'].median() for data in yearly_data.values()],
            'Max_Radiance': [data['avg_rad'].max() for data in yearly_data.values()],
            'Total_Radiance': [data['avg_rad'].sum() for data in yearly_data.values()]
        })

        # 1. Time Series Plot
        print_progress("Creating time series plot")
        fig = make_subplots(rows=2, cols=1,
                           subplot_titles=('Mean Light Pollution Over Time',
                                         'Year-over-Year Change (%)'))

        # Add mean radiance trace
        fig.add_trace(
            go.Scatter(x=yearly_stats['Year'], y=yearly_stats['Mean_Radiance'],
                      mode='lines+markers', name='Mean Radiance',
                      line=dict(color='cyan')),
            row=1, col=1
        )

        # Calculate and plot year-over-year change
        yoy_change = yearly_stats['Mean_Radiance'].pct_change() * 100
        fig.add_trace(
            go.Bar(x=yearly_stats['Year'][1:], y=yoy_change[1:],
                   name='YoY Change %',
                   marker_color=['red' if x < 0 else 'green' for x in yoy_change[1:]]),
            row=2, col=1
        )

        fig.update_layout(height=800, title_text="Light Pollution Trends in India (2014-2023)",
                         showlegend=True)
        
        # Save with absolute path
        trends_path = os.path.join(output_dir, "temporal_analysis_trends.html")
        print_progress(f"Saving time series plot to {trends_path}")
        fig.write_html(trends_path)

        # 2. Create difference heatmap between 2014 and 2023
        if 2014 in yearly_data and 2023 in yearly_data:
            create_difference_heatmap(yearly_data[2014], yearly_data[2023])
        else:
            print("Cannot create difference heatmap: missing data for 2014 or 2023")

        # 3. Regional Analysis
        print_progress("Performing regional analysis")
        def assign_region(row):
            lat, lon = row['Latitude'], row['Longitude']
            if lat > 28:
                return 'North'
            elif lat < 18:
                return 'South'
            elif lon < 78:
                return 'West'
            elif lon > 85:
                return 'East'
            else:
                return 'Central'

        # Calculate regional statistics for each year
        regional_stats = []
        for year, data in yearly_data.items():
            data['Region'] = data.apply(assign_region, axis=1)
            stats = data.groupby('Region')['avg_rad'].mean().reset_index()
            stats['Year'] = year
            regional_stats.append(stats)

        regional_df = pd.concat(regional_stats)

        # Create regional trends plot
        print_progress("Creating regional trends plot")
        fig = px.line(regional_df, x='Year', y='avg_rad', color='Region',
                      title='Regional Light Pollution Trends (2014-2023)',
                      labels={'avg_rad': 'Average Radiance', 'Year': 'Year'})
        
        # Save with absolute path
        regional_path = os.path.join(output_dir, "regional_trends.html")
        print_progress(f"Saving regional trends plot to {regional_path}")
        fig.write_html(regional_path)

        # Print summary statistics
        print_progress("Calculating final statistics")
        print("\nSummary of Changes (2014 to 2023):")
        if 2014 in yearly_data and 2023 in yearly_data:
            overall_change = ((yearly_stats['Mean_Radiance'].iloc[-1] / yearly_stats['Mean_Radiance'].iloc[0]) - 1) * 100
            print("Overall change in mean radiance: {:.2f}%".format(overall_change))

            # Calculate regional changes
            regional_changes = []
            for region in regional_df['Region'].unique():
                region_data = regional_df[regional_df['Region'] == region]
                change = ((region_data[region_data['Year'] == 2023]['avg_rad'].values[0] /
                          region_data[region_data['Year'] == 2014]['avg_rad'].values[0]) - 1) * 100
                regional_changes.append({'Region': region, 'Change': change})

            regional_changes_df = pd.DataFrame(regional_changes)
            print("\nRegional Changes (2014 to 2023):")
            for _, row in regional_changes_df.iterrows():
                print(f"{row['Region']}: {row['Change']:.2f}%")
        else:
            print("Cannot calculate changes: missing data for 2014 or 2023")

        print_progress("Analysis completed successfully!")

    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        raise 