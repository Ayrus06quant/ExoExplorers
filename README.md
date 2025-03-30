<<<<<<< HEAD
# 🌌 Mapping India’s Light Pollution (2014–2023)
**Team Name:** ExoExplorers
**Hackathon:** Orion Astrathon – Problem Statement 03

---

## 🧠 Problem Overview

Light pollution is a rising environmental concern, especially in rapidly urbanizing countries like India. Our goal is to map and analyze the growth of artificial night lighting over India using satellite-based datasets from 2014 to 2023.

---

## 📦 What We Have Done So Far

### ✅ Data Collection (2014–2023)
- Downloaded monthly VIIRS DNB Nighttime Lights satellite data from **Google Earth Engine**
- Sampled radiance values across India (5000+ points per year)
- Exported cleaned CSVs for each year (2014 to 2023)

### ✅ Geospatial Processing
- Clipped all spatial data to **India's geographic boundary** using a GeoJSON file
- Normalized light intensity (`avg_rad`) values for heatmap scaling

### ✅ Visualization
- Created smooth **heatmaps** for all years using:
  - `folium` for interactive maps
  - `matplotlib` + `scipy` for PNG-based overlays
- Built a pixel-based **radiance scatter map** similar to [lightpollutionmap.info](https://lightpollutionmap.info)


---

## 🔍 Insights So Far

- Significant increase in light pollution intensity around major metro cities (Delhi, Mumbai, Bengaluru) from 2014 to 2023
- Dark zones shrinking year-over-year in the central and eastern regions
- Overall urban glow expanding — strong correlation with known urbanization zones

---

## 🛠️ Tools & Technologies

- 📡 Google Earth Engine (VIIRS DNB imagery)
- 🐍 Python (pandas, geopandas, folium, matplotlib, scipy)
- 🗺️ Leaflet.js (via Folium)
- 🧭 GeoJSON for India's spatial boundary

---

## 🔜 What’s Next

- Add **year-over-year comparison slider** in a Streamlit or Folium dashboard
- Perform **correlation analysis** between light pollution and urban growth/population density
- Identify and visualize **dark sky reserves**
- Explore **ML-based trend prediction**

---

## 👥 Team

- Gaurav – Data & Visualization
- Chirag – Earth Engine & GIS
- Surya – Analysis & Report
- Shreyash – Web/Dashboard (if applicable)

---

=======
# 🌌 Mapping India’s Light Pollution (2014–2023)
**Team Name:** ExoExplorers
**Hackathon:** Orion Astrathon – Problem Statement 03

---

## 🧠 Problem Overview

Light pollution is a rising environmental concern, especially in rapidly urbanizing countries like India. Our goal is to map and analyze the growth of artificial night lighting over India using satellite-based datasets from 2014 to 2023.

---

## 📦 What We Have Done So Far

### ✅ Data Collection (2014–2023)
- Downloaded monthly VIIRS DNB Nighttime Lights satellite data from **Google Earth Engine**
- Sampled radiance values across India (5000+ points per year)
- Exported cleaned CSVs for each year (2014 to 2023)

### ✅ Geospatial Processing
- Clipped all spatial data to **India's geographic boundary** using a GeoJSON file
- Normalized light intensity (`avg_rad`) values for heatmap scaling

### ✅ Visualization
- Created smooth **heatmaps** for all years using:
  - `folium` for interactive maps
  - `matplotlib` + `scipy` for PNG-based overlays
- Built a pixel-based **radiance scatter map** similar to [lightpollutionmap.info](https://lightpollutionmap.info)


---

## 🔍 Insights So Far

- Significant increase in light pollution intensity around major metro cities (Delhi, Mumbai, Bengaluru) from 2014 to 2023
- Dark zones shrinking year-over-year in the central and eastern regions
- Overall urban glow expanding — strong correlation with known urbanization zones

---

## 🛠️ Tools & Technologies

- 📡 Google Earth Engine (VIIRS DNB imagery)
- 🐍 Python (pandas, geopandas, folium, matplotlib, scipy)
- 🗺️ Leaflet.js (via Folium)
- 🧭 GeoJSON for India's spatial boundary

---

## 🔜 What’s Next

- Add **year-over-year comparison slider** in a Streamlit or Folium dashboard
- Perform **correlation analysis** between light pollution and urban growth/population density
- Identify and visualize **dark sky reserves**
- Explore **ML-based trend prediction**

---

## 👥 Team

- Gaurav – Data & Visualization
- Chirag – Earth Engine & GIS
- Surya – Analysis & Report
- Shreyash – Web/Dashboard (if applicable)

---

>>>>>>> c0aff892be7645f07496be9f8c8efd47befef2e2
> ✨ This is a mid-submission summary. We're on track to deliver a powerful visualization and statistical story on how India's night sky is changing over time.