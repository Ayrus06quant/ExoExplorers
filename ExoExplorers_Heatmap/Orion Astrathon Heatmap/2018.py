import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point

# Load your data
df = pd.read_csv("VIIRS_Lights_India_2018.csv")

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
india = gpd.read_file("india_boundary.geojson")

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
    "india_boundary.geojson",
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

# Add boundary overlay (optional for debugging)
# folium.GeoJson("india_boundary.geojson", name="India Border").add_to(m)

m.save("viirs_heatmap_2018.html")