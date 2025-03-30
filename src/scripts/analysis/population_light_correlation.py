import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os

def load_population_data(csv_file):
    # Read the CSV file, skipping the first 4 rows
    df = pd.read_csv(csv_file, skiprows=4)
    
    # Extract India's data
    india_data = df[df['Country Name'] == 'India'].iloc[0]
    
    # Get years from 2014 to 2023
    years = [str(year) for year in range(2014, 2024)]
    growth_rates = [float(india_data[str(year)]) for year in range(2014, 2024)]
    
    # Create a DataFrame with years and growth rates
    population_df = pd.DataFrame({
        'Year': years,
        'Growth_Rate': growth_rates
    })
    
    return population_df

def load_light_pollution_data(base_path):
    # List to store data for each year
    data_list = []
    
    # Process each year from 2014 to 2023
    for year in range(2014, 2024):
        file_pattern = f"VIIRS_India_{year}.csv"
        file_path = os.path.join(base_path, file_pattern)
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            mean_radiance = df['avg_rad'].mean()
            data_list.append({
                'Year': str(year),
                'Mean_Radiance': mean_radiance
            })
    
    return pd.DataFrame(data_list)

def analyze_correlation(population_df, light_df):
    # Merge the dataframes
    merged_df = pd.merge(population_df, light_df, on='Year')
    
    # Calculate correlation
    correlation = merged_df['Growth_Rate'].corr(merged_df['Mean_Radiance'])
    
    return merged_df, correlation

def create_visualizations(merged_df, correlation, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a subplot with two y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add population growth rate line
    fig.add_trace(
        go.Scatter(x=merged_df['Year'], y=merged_df['Growth_Rate'],
                  name="Population Growth Rate (%)", line=dict(color="blue")),
        secondary_y=False
    )
    
    # Add mean radiance line
    fig.add_trace(
        go.Scatter(x=merged_df['Year'], y=merged_df['Mean_Radiance'],
                  name="Mean Radiance", line=dict(color="red")),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title=f"Population Growth Rate vs Light Pollution (Correlation: {correlation:.3f})",
        xaxis_title="Year",
        hovermode="x unified"
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Population Growth Rate (%)", secondary_y=False)
    fig.update_yaxes(title_text="Mean Radiance", secondary_y=True)
    
    # Save the plot
    fig.write_html(os.path.join(output_dir, "population_light_correlation.html"))
    
    # Create a scatter plot
    scatter_fig = px.scatter(merged_df, x='Growth_Rate', y='Mean_Radiance',
                           trendline="ols",
                           title=f"Population Growth Rate vs Mean Radiance (Correlation: {correlation:.3f})")
    scatter_fig.write_html(os.path.join(output_dir, "correlation_scatter.html"))
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("------------------")
    print(f"Average Population Growth Rate: {merged_df['Growth_Rate'].mean():.3f}%")
    print(f"Average Mean Radiance: {merged_df['Mean_Radiance'].mean():.3f}")
    print(f"Correlation Coefficient: {correlation:.3f}")
    print("\nYearly Data:")
    print(merged_df.to_string(index=False))

def main():
    # Set paths
    base_path = "src/data/viirs"
    population_file = "src/data/population/API_SP.POP.GROW_DS2_en_csv_v2_13638.csv"
    output_dir = "docs/visualizations/analysis"
    
    try:
        # Load data
        population_df = load_population_data(population_file)
        light_df = load_light_pollution_data(base_path)
        
        # Analyze correlation
        merged_df, correlation = analyze_correlation(population_df, light_df)
        
        # Create visualizations
        create_visualizations(merged_df, correlation, output_dir)
        
        print(f"Analysis completed successfully.")
        print(f"Results have been saved to {output_dir}/")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 