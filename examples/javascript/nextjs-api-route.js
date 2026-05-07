// Next.js API route — server-side only, keeps API key out of the browser bundle
// File location: pages/api/body-dimensions.js (Pages Router)
//                app/api/body-dimensions/route.js (App Router — see comment at bottom)
//
// Replace YOUR_API_KEY with your RapidAPI key, stored in .env.local:
//   RAPIDAPI_KEY=YOUR_API_KEY

const RAPIDAPI_URL = "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict";

// Pages Router handler
export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { gender, height_cm, weight_kg, age, region = "GLOBAL" } = req.body;

  if (!gender || !height_cm || !weight_kg) {
    return res.status(400).json({ error: "gender, height_cm, and weight_kg are required" });
  }

  const payload = {
    input_data: {
      input_unit_system: "metric",
      subject: {
        gender,
        exact_age: age ?? null,
        age_category: "ADULT",
        input_origin_region: region,
      },
      anchors: {
        body_height: Math.round(height_cm * 10), // convert cm → mm
        body_mass: weight_kg,
      },
    },
    output_settings: {
      calculation: {
        calculation_model: "AUTO",
        target_region: region,
        body_build_type: "CIVILIAN",
      },
      requested_dimensions: { bundle: "TORSO" }, // clothing-relevant dimensions
      output_format: {
        unit_system: "metric",
        confidence_score_threshold: 75,
        include_range_95: false,
        include_iso_codes: false,
      },
    },
  };

  try {
    const upstream = await fetch(RAPIDAPI_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": process.env.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "dimensionspot-bodysize-engine.p.rapidapi.com",
      },
      body: JSON.stringify(payload),
    });

    if (!upstream.ok) {
      const error = await upstream.json();
      return res.status(upstream.status).json({ error });
    }

    const data = await upstream.json();
    return res.status(200).json(data);
  } catch (err) {
    return res.status(500).json({ error: "Upstream request failed", detail: err.message });
  }
}

// --- App Router variant ---
// File: app/api/body-dimensions/route.js
//
// import { NextResponse } from "next/server";
//
// export async function POST(request) {
//   const body = await request.json();
//   // ... same payload construction as above ...
//   const upstream = await fetch(RAPIDAPI_URL, { ... });
//   const data = await upstream.json();
//   return NextResponse.json(data);
// }
