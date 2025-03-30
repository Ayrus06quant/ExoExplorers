import streamlit as st
import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap, Geocoder
from streamlit_folium import st_folium
from geopy.distance import geodesic
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------------------
# Configuration
# ----------------------------
st.set_page_config(layout="wide")
st.title("💡 Live Light Pollution Heatmap (2014–2023)")
st.markdown("🛰️ Explore India's light pollution using VIIRS satellite data. Also check observation suitability by location.")

DARK_SKY_THRESHOLD = 3.0  # Radiance above this is considered unsuitable

# ----------------------------
# Year Selector
# ----------------------------
years = list(range(2014, 2024))
year = st.selectbox("📅 Select Year", years, index=len(years) - 1)

# ----------------------------
# Load CSV
# ----------------------------
csv_path = os.path.join(project_root, "src", "data", "viirs", f"VIIRS_India_{year}.csv")
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    st.error(f"CSV file not found: {csv_path}")
    st.stop()

# Extract lat/lon from `.geo`
def extract_coords(geo_str):
    geo_json = json.loads(geo_str)
    lon, lat = geo_json["coordinates"]
    return pd.Series([lat, lon])

df[['Latitude', 'Longitude']] = df['.geo'].apply(extract_coords)

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']),
    crs="EPSG:4326"
)

# Clip to India boundary
india = gpd.read_file(os.path.join(project_root, "src", "data", "boundaries", "india_boundary.geojson"))
gdf = gpd.sjoin(gdf, india, predicate='within')

# Normalize brightness
gdf = gdf[gdf['avg_rad'] > 0].copy()
gdf['norm_rad'] = gdf['avg_rad'] / gdf['avg_rad'].max()

# Prepare heatmap data
heat_data = [[row['Latitude'], row['Longitude'], row['norm_rad']] for idx, row in gdf.iterrows()]
st.write(f"🟢 Heatmap data points: {len(heat_data)}")

# ----------------------------
# Create Base Map
# ----------------------------
# ----------------------------
# Create Base Map First (no render yet)
# ----------------------------
m = folium.Map(location=[22.9734, 78.6569], zoom_start=5, tiles='CartoDB dark_matter')
Geocoder(collapsed=False).add_to(m)

# Add heatmap layer
HeatMap(
    heat_data,
    radius=15,
    blur=10,
    min_opacity=0.3,
    max_zoom=6
).add_to(m)

# ----------------------------
# Suitability Check Block
# ----------------------------
st.markdown("### 🔍 Check Light Pollution Suitability at a Location")

lat = st.number_input("Latitude", value=28.6139, format="%.6f")
lon = st.number_input("Longitude", value=77.2090, format="%.6f")

def get_nearest_viirs_value(lat, lon, gdf):
    from geopy.distance import geodesic
    min_dist = float('inf')
    nearest_value = None
    for _, row in gdf.iterrows():
        dist = geodesic((lat, lon), (row['Latitude'], row['Longitude'])).meters
        if dist < min_dist:
            min_dist = dist
            nearest_value = row['avg_rad']
    return nearest_value, min_dist

# Handle button interaction
if st.button("Check Pollution at Location"):
    nearest_value, dist = get_nearest_viirs_value(lat, lon, gdf)

    if nearest_value is not None:
        st.markdown(f"**📍 Closest Data Point**: {dist:.2f} meters away")
        st.markdown(f"**💡 Radiance (avg_rad)**: `{nearest_value:.2f} nW/cm²/sr`")

        if nearest_value > DARK_SKY_THRESHOLD:
            st.error("❌ This region is **unsuitable** for dark-sky observation.")
        else:
            st.success("✅ This region is **suitable** for dark-sky observation.")

        # ✅ Add marker with color based on suitability
        folium.Marker(
            location=[lat, lon],
            popup=f"avg_rad: {nearest_value:.2f}",
            icon=folium.Icon(color="red" if nearest_value > DARK_SKY_THRESHOLD else "green")
        ).add_to(m)
    else:
        st.warning("⚠️ No VIIRS data found near this location.")

# ----------------------------
# Final: Render the map once at the end
# ----------------------------
st_folium(m, width=1100, height=650)

# python -m streamlit run src/app.py