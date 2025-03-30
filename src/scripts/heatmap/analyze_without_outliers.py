import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point
import os
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
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

def load_and_analyze_year(year):
    print_progress(f"Analyzing year {year}")
    print("-" * 40)

    # Load data
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
    
    # Calculate robust statistics for all India
    all_india_stats = calculate_robust_stats(gdf['avg_rad'])
    print("\nAll India Statistics (With Outliers):")
    print_stats(all_india_stats)
    
    # Remove outliers for all India (using IQR method)
    clean_all = remove_outliers(gdf['avg_rad'])
    clean_stats = calculate_robust_stats(clean_all)
    print("\nAll India Statistics (Without Outliers):")
    print_stats(clean_stats)
    
    # Filter for East India (longitude > 85)
    east_data = gdf[gdf['Longitude'] > 85]['avg_rad']
    east_stats = calculate_robust_stats(east_data)
    print("\nEast India Statistics (With Outliers):")
    print_stats(east_stats)
    
    # Remove outliers for East India
    clean_east = remove_outliers(east_data)
    clean_east_stats = calculate_robust_stats(clean_east)
    print("\nEast India Statistics (Without Outliers):")
    print_stats(clean_east_stats)
    
    # Plot distributions before and after outlier removal
    plot_distributions(gdf['avg_rad'], clean_all, east_data, clean_east, year)
    
    return {
        'all_with_outliers': gdf['avg_rad'],
        'all_clean': clean_all,
        'east_with_outliers': east_data,
        'east_clean': clean_east,
        'stats': {
            'all_with_outliers': all_india_stats,
            'all_clean': clean_stats,
            'east_with_outliers': east_stats,
            'east_clean': clean_east_stats
        }
    }

def calculate_robust_stats(data):
    return {
        'mean': data.mean(),
        'median': data.median(),
        'trimmed_mean_5': stats.trim_mean(data, 0.05),  # 5% trimmed mean
        'trimmed_mean_10': stats.trim_mean(data, 0.10),  # 10% trimmed mean
        'std': data.std(),
        'mad': stats.median_abs_deviation(data),  # Median Absolute Deviation
        'q1': data.quantile(0.25),
        'q3': data.quantile(0.75),
        'min': data.min(),
        'max': data.max(),
        'count': len(data)
    }

def print_stats(stats):
    print(f"Count: {stats['count']}")
    print(f"Mean: {stats['mean']:.3f}")
    print(f"Median: {stats['median']:.3f}")
    print(f"5% Trimmed Mean: {stats['trimmed_mean_5']:.3f}")
    print(f"10% Trimmed Mean: {stats['trimmed_mean_10']:.3f}")
    print(f"Standard Deviation: {stats['std']:.3f}")
    print(f"Median Absolute Deviation: {stats['mad']:.3f}")
    print(f"Q1: {stats['q1']:.3f}")
    print(f"Q3: {stats['q3']:.3f}")
    print(f"Min: {stats['min']:.3f}")
    print(f"Max: {stats['max']:.3f}")

def remove_outliers(series):
    # Use IQR method to remove outliers
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return series[(series >= lower_bound) & (series <= upper_bound)]

def plot_distributions(all_data, clean_all, east_data, clean_east, year):
    plt.figure(figsize=(15, 10))
    
    # All India distributions
    plt.subplot(2, 1, 1)
    sns.kdeplot(data=all_data, label='With Outliers', color='blue', alpha=0.5)
    sns.kdeplot(data=clean_all, label='Without Outliers', color='red', alpha=0.5)
    plt.title(f'Distribution of Radiance Values - All India ({year})')
    plt.xlabel('Radiance')
    plt.ylabel('Density')
    plt.legend()
    
    # East India distributions
    plt.subplot(2, 1, 2)
    sns.kdeplot(data=east_data, label='With Outliers', color='blue', alpha=0.5)
    sns.kdeplot(data=clean_east, label='Without Outliers', color='red', alpha=0.5)
    plt.title(f'Distribution of Radiance Values - East India ({year})')
    plt.xlabel('Radiance')
    plt.ylabel('Density')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'distributions_{year}.png'))
    plt.close()

if __name__ == "__main__":
    print(f"Project root: {project_root}")
    try:
        # Analyze years 2014-2023
        years = range(2014, 2024)
        yearly_data = {}
        
        for year in years:
            yearly_data[year] = load_and_analyze_year(year)
        
        # Calculate year-over-year changes using different metrics
        metrics = ['mean', 'median', 'trimmed_mean_5', 'trimmed_mean_10']
        regions = ['all_clean', 'east_clean']
        
        print("\nYear-over-Year Changes (Without Outliers):")
        print("-" * 50)
        
        for region in regions:
            print(f"\n{region.replace('_', ' ').title()}:")
            for metric in metrics:
                print(f"\n{metric.replace('_', ' ').title()}:")
                for i in range(len(years)-1):
                    year1, year2 = years[i], years[i+1]
                    val1 = yearly_data[year1]['stats'][region][metric]
                    val2 = yearly_data[year2]['stats'][region][metric]
                    change = ((val2 / val1) - 1) * 100
                    print(f"{year1}-{year2}: {change:.2f}%")
        
        # Create trend plots
        plt.figure(figsize=(15, 10))
        
        # Plot for All India
        plt.subplot(2, 1, 1)
        for metric in metrics:
            values = [yearly_data[year]['stats']['all_clean'][metric] for year in years]
            plt.plot(years, values, marker='o', label=metric.replace('_', ' ').title())
        plt.title('Trends in All India (Without Outliers)')
        plt.xlabel('Year')
        plt.ylabel('Radiance')
        plt.legend()
        
        # Plot for East India
        plt.subplot(2, 1, 2)
        for metric in metrics:
            values = [yearly_data[year]['stats']['east_clean'][metric] for year in years]
            plt.plot(years, values, marker='o', label=metric.replace('_', ' ').title())
        plt.title('Trends in East India (Without Outliers)')
        plt.xlabel('Year')
        plt.ylabel('Radiance')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'robust_trends.png'))
        plt.close()
        
        # Create a summary table
        summary_data = []
        for year in years:
            row = {
                'Year': year,
                'All India Mean (Clean)': yearly_data[year]['stats']['all_clean']['mean'],
                'All India Median (Clean)': yearly_data[year]['stats']['all_clean']['median'],
                'All India 5% Trimmed Mean': yearly_data[year]['stats']['all_clean']['trimmed_mean_5'],
                'East Mean (Clean)': yearly_data[year]['stats']['east_clean']['mean'],
                'East Median (Clean)': yearly_data[year]['stats']['east_clean']['median'],
                'East 5% Trimmed Mean': yearly_data[year]['stats']['east_clean']['trimmed_mean_5'],
                'All Points Count': yearly_data[year]['stats']['all_with_outliers']['count'],
                'Clean Points Count': yearly_data[year]['stats']['all_clean']['count'],
                'Outliers Removed': (yearly_data[year]['stats']['all_with_outliers']['count'] - 
                                   yearly_data[year]['stats']['all_clean']['count'])
            }
            summary_data.append(row)
        
        summary_df = pd.DataFrame(summary_data)
        print("\nSummary Statistics:")
        print(summary_df.to_string(index=False))
        
        # Save summary to CSV
        summary_df.to_csv(os.path.join(output_dir, 'outlier_analysis_summary.csv'), index=False)
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Light Pollution Analysis (Without Outliers)</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .plot {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Light Pollution Analysis (Without Outliers)</h1>
                <div class="plot">
                    <h2>Trends in All India and East India</h2>
                    <img src="robust_trends.png" alt="Robust Trends">
                </div>
                <div class="plot">
                    <h2>Summary Statistics</h2>
                    {summary_df.to_html()}
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(os.path.join(output_dir, 'outlier_analysis.html'), 'w') as f:
            f.write(html_content)
            
        print("\nAnalysis completed successfully!")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise 