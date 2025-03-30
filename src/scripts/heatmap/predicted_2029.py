import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap, Geocoder
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set paths
data_file = os.path.join(project_root, "src", "future_predictions.csv")
boundary_file = os.path.join(project_root, "src", "data", "boundaries", "india_boundary.geojson")
output_file = os.path.join(project_root, "docs", "visualizations", "heatmaps", "viirs_predicted_heatmap_2029.html")

# ----------------------------------------
# Load the predicted light pollution data
# ----------------------------------------
df = pd.read_csv(data_file)

# ----------------------------------------
# Filter for year 2029
# ----------------------------------------
df = df[df['year'] == 2029].copy()

# Rename columns if needed (make sure names match)
df.rename(columns={'latitude': 'Latitude', 'longitude': 'Longitude'}, inplace=True)

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
    return {
        'fillOpacity': 0,
        'color': '#00000000',
        'weight': 0
    }

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
