// Replace YOUR_API_KEY with your RapidAPI key
// Get your key at: https://rapidapi.com/d-pot-apps/api/dimensionspot-bodysize-engine
// Requires Node.js 18+ (native fetch) or install node-fetch: npm install node-fetch

const URL = "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict";
const API_KEY = "YOUR_API_KEY";

const payload = {
  input_data: {
    input_unit_system: "metric",
    subject: {
      gender: "male",
      exact_age: 35.0,
      age_category: "ADULT",
      input_origin_region: "EUROPE",
    },
    anchors: {
      body_height: 1780, // millimeters — NOT centimeters (178 cm × 10)
      body_mass: 82.0,   // kilograms
    },
  },
  output_settings: {
    calculation: {
      calculation_model: "AUTO",
      target_region: "EUROPE",
      body_build_type: "CIVILIAN",
    },
    requested_dimensions: { bundle: "FULL_BODY" },
    output_format: {
      unit_system: "metric",
      confidence_score_threshold: 0,
      include_range_95: true,
      include_iso_codes: true,
    },
  },
};

async function predict() {
  const response = await fetch(URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-RapidAPI-Key": API_KEY,
      "X-RapidAPI-Host": "dimensionspot-bodysize-engine.p.rapidapi.com",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API error ${response.status}: ${JSON.stringify(error)}`);
  }

  const data = await response.json();
  const dimensions = data.body_dimensions;

  console.log(`Engine used: ${data.header.calculation_model_used}`);
  console.log(`Dimensions returned: ${Object.keys(dimensions).length}\n`);

  // Sample key dimensions
  for (const key of ["shoulder_height", "chest_circumference", "hip_circumference"]) {
    if (dimensions[key]) {
      const dim = dimensions[key];
      console.log(
        `${dim.label}: ${dim.value} ${dim.unit} (confidence: ${dim.confidence_score})`
      );
    }
  }
}

predict().catch(console.error);
