import os
import shutil

def create_prediction_script(year):
    script_content = f'''import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap, Geocoder
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set paths
data_file = os.path.join(project_root, "src", "future_predictions.csv")
boundary_file = os.path.join(project_root, "src", "data", "boundaries", "india_boundary.geojson")
output_file = os.path.join(project_root, "docs", "visualizations", "heatmaps", "viirs_predicted_heatmap_{year}.html")

# ----------------------------------------
# Load the predicted light pollution data
# ----------------------------------------
df = pd.read_csv(data_file)

# ----------------------------------------
# Filter for year {year}
# ----------------------------------------
df = df[df['year'] == {year}].copy()

# Rename columns if needed (make sure names match)
df.rename(columns={{'latitude': 'Latitude', 'longitude': 'Longitude'}}, inplace=True)

# ----------------------------------------
# Create GeoDataFrame from points
# ----------------------------------------
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']),
    crs="EPSG:4326"
)

# ----------------------------------------
# Clip to India boundary
# ----------------------------------------
india = gpd.read_file(boundary_file)
gdf = gpd.sjoin(gdf, india, predicate='within')

# ----------------------------------------
# Normalize the predicted pollution values
# ----------------------------------------
gdf['norm_pred'] = gdf['predicted_light_pollution'] / gdf['predicted_light_pollution'].max()

# ----------------------------------------
# Prepare heatmap data (latitude, longitude, intensity)
# ----------------------------------------
heat_data = [[row['Latitude'], row['Longitude'], row['norm_pred']] for idx, row in gdf.iterrows()]

# ----------------------------------------
# Create the Folium map
# ----------------------------------------
m = folium.Map(location=[22.9734, 78.6569], zoom_start=5, tiles='CartoDB dark_matter')

# Add geocoder/search bar
Geocoder(collapsed=False, add_marker=True).add_to(m)

# Optional: transparent boundary style
def style_function(feature):
    return {{
        'fillOpacity': 0,
        'color': '#00000000',
        'weight': 0
    }}

folium.GeoJson(boundary_file, name="India Border", style_function=style_function).add_to(m)

# Add the heatmap layer
HeatMap(
    heat_data,
    radius=15,
    blur=10,
    min_opacity=0.3,
    max_zoom=6
).add_to(m)

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Save the final map
m.save(output_file)
'''
    return script_content

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create backup directory
    backup_dir = os.path.join(script_dir, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Update prediction scripts for each year
    for year in range(2025, 2030):
        script_path = os.path.join(script_dir, f"predicted_{year}.py")
        backup_path = os.path.join(backup_dir, f"predicted_{year}.py")
        
        # Backup existing script if it exists
        if os.path.exists(script_path):
            shutil.copy2(script_path, backup_path)
        
        # Create new script
        with open(script_path, 'w') as f:
            f.write(create_prediction_script(year))
        
        print(f"Updated prediction script for year {year}")
    
    print("\nAll prediction scripts have been updated.")
    print("Original scripts have been backed up to the 'backup' directory.")

if __name__ == "__main__":
    main() 