// Define bounding box for India
var india = ee.Geometry.Rectangle([68, 6, 97, 37]);

// Load VIIRS ImageCollection
var viirsCollection = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")
                       .select('avg_rad');

// Function to export a single year
function exportYearlyVIIRS(year) {
  var start = ee.Date.fromYMD(year, 1, 1);
  var end = start.advance(1, 'year');

  // Get annual average image
  var yearlyImage = viirsCollection
                      .filterDate(start, end)
                      .mean()
                      .clip(india);

  // Sample random points
  var points = ee.FeatureCollection.randomPoints({
    region: india,
    points: 5000,
    seed: year  // Use year as seed for reproducibility
  });

  var samples = yearlyImage.sampleRegions({
    collection: points,
    scale: 500,
    geometries: true
  });

  // Export to Drive
  Export.table.toDrive({
    collection: samples,
    description: 'VIIRS_India_' + year,
    fileFormat: 'CSV'
  });
}

// Loop through years and export
var years = ee.List.sequence(2014, 2023);
years.getInfo().forEach(function(y) {
  exportYearlyVIIRS(y);
});