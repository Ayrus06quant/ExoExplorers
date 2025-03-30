import os
import shutil
import re

def create_year_script(year):
    script_content = f'''import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set paths
data_file = os.path.join(project_root, "data", "viirs", "VIIRS_India_{year}.csv")
boundary_file = os.path.join(project_root, "data", "boundaries", "india_boundary.geojson")
output_file = os.path.join(project_root, "docs", "visualizations", "heatmaps", "viirs_heatmap_{year}.html")

# Load your data
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

# Load India boundary
india = gpd.read_file(boundary_file)

# Spatial join: Keep only points within India
gdf = gpd.sjoin(gdf, india, predicate='within')

# Normalize brightness
gdf['norm_rad'] = gdf['avg_rad'] / gdf['avg_rad'].max()

# Prepare data for heatmap
heat_data = [[row['Latitude'], row['Longitude'], row['norm_rad']] for idx, row in gdf.iterrows()]

import folium
from folium.plugins import HeatMap

m = folium.Map(location=[22.9734, 78.6569], zoom_start=5, tiles='CartoDB dark_matter')

# Optional: add only the outer boundary with no stroke inside
def style_function(feature):
    return {{
        'fillOpacity': 0,        # No fill
        'color': '#00000000',    # Transparent stroke
        'weight': 0              # No line width
    }}

folium.GeoJson(
    boundary_file,
    name="India Border",
    style_function=style_function
).add_to(m)

HeatMap(
    heat_data,
    radius=15,
    blur=10,
    min_opacity=0.3,
    max_zoom=6
).add_to(m)

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Save the map
m.save(output_file)
'''
    return script_content

def update_file_paths(file_path):
    # Get the project root directory (two levels up from this script)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update VIIRS data path
    content = re.sub(
        r'df = pd\.read_csv\("VIIRS_India_\d{4}\.csv"\)',
        f'df = pd.read_csv(os.path.join("{project_root}", "src", "data", "viirs", "VIIRS_India_\\1.csv"))',
        content
    )
    
    # Update India boundary path
    content = re.sub(
        r'india = gpd\.read_file\("india_boundary\.geojson"\)',
        f'india = gpd.read_file(os.path.join("{project_root}", "src", "data", "boundaries", "india_boundary.geojson"))',
        content
    )
    
    # Update GeoJson path
    content = re.sub(
        r'folium\.GeoJson\("india_boundary\.geojson"',
        f'folium.GeoJson(os.path.join("{project_root}", "src", "data", "boundaries", "india_boundary.geojson")',
        content
    )
    
    # Update future predictions path
    content = re.sub(
        r'df = pd\.read_csv\("future_predictions\.csv"\)',
        f'df = pd.read_csv(os.path.join("{project_root}", "src", "future_predictions.csv"))',
        content
    )
    
    # Update output HTML path
    content = re.sub(
        r'm\.save\("viirs_(?:predicted_)?heatmap_\d{4}\.html"\)',
        f'm.save(os.path.join("{project_root}", "docs", "visualizations", "heatmaps", "viirs_\\1heatmap_\\2.html"))',
        content
    )
    
    # Add os import if not present
    if 'import os' not in content:
        content = 'import os\n' + content
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create backup directory
    backup_dir = os.path.join(script_dir, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Update scripts for each year
    for year in range(2014, 2024):
        script_path = os.path.join(script_dir, f"{year}.py")
        backup_path = os.path.join(backup_dir, f"{year}.py")
        
        # Backup existing script if it exists
        if os.path.exists(script_path):
            shutil.copy2(script_path, backup_path)
        
        # Create new script
        with open(script_path, 'w') as f:
            f.write(create_year_script(year))
        
        print(f"Updated script for year {year}")
    
    print("\nAll year scripts have been updated.")
    print("Original scripts have been backed up to the 'backup' directory.")

    # Update prediction scripts (2025-2029)
    for year in range(2025, 2030):
        file_path = os.path.join(script_dir, f"predicted_{year}.py")
        if os.path.exists(file_path):
            print(f"Updating predicted_{year}.py...")
            update_file_paths(file_path)
    
    print("All scripts updated successfully!")

if __name__ == "__main__":
    main() 