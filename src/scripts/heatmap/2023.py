import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set paths
data_file = os.path.join(project_root, "data", "viirs", "VIIRS_India_2023.csv")
boundary_file = os.path.join(project_root, "data", "boundaries", "india_boundary.geojson")
output_file = os.path.join(project_root, "docs", "visualizations", "heatmaps", "viirs_heatmap_2023.html")

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
    return {
        'fillOpacity': 0,        # No fill
        'color': '#00000000',    # Transparent stroke
        'weight': 0              # No line width
    }

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
