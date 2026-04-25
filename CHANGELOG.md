# DimensionsPot - BodySize Engine: **Changelog**

All notable changes to the DimensionsPot API are documented in this file.  
This project adheres to [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.4.0] — Dimension Catalog v4.0

### Added

- **Sixth Swagger UI example** — Pediatric child scenario (7-year-old female, CHILD age group, HEAD_FACE bundle) added to the pre-built request example set.
- **Anchor bounds validation** — Input anchors are validated against physiologically derived bounds for 14 named measurements (e.g. `body_height` 400–3000 mm, `foot_length` 80–420 mm). A generic fallback bound (5–3000 mm) applies to all other keys. Returns a descriptive `422` with the offending key and expected range.
- **Extended imperial input coverage** — Imperial-to-metric converter extended to cover `_arc`, `_width`, `_reach` suffix patterns and the standalone `span` key, eliminating edge cases where valid imperial anchor values were incorrectly rejected.

### Changed

- **Dimension catalog locked at 130** — Final pass of the quality review process established at v1.0.0. Each included dimension satisfies all three criteria: (1) distinct commercial application in at least one primary vertical (fashion, ergonomics, medical devices, sports equipment), (2) validated prediction accuracy within the MAE tolerance for its tissue class, (3) no duplication with another catalog entry. Dimensions that did not meet all three criteria were excluded from the public catalog:
  - **Duplicates / aliases (5):** `acromial_height`, `interpupillary_breadth`, `elbow_fingertip_length`, `index_finger_length`, `overall_length_wheelchair`.
  - **No distinct commercial application (6):** `neck_circumference_base`, `tenth_rib_height`, `lateral_femoral_epicondyle_height`, `crotch_length_posterior_omphalion`, `forearm_center_of_grip_length`, `nose_protrusion`.
  - **Below accuracy threshold (6):** `forearm_forearm_breadth`, `abdominal_extension_depth_sitting`, `bitragion_submandibular_arc`, `waist_front_length_sitting`, `hip_breadth_sitting`, `knee_height_mid_patella`.
- **`PRIMARY_RICH` confidence tier finalized at 84** (BONE → 87, FLESH → 80) — based on Track 6 (n=300 ANSUR) and Track 7 (14/14 tiers CALIBRATED) precision validation.
- **`model_version` and `api_version`** in API responses resolve dynamically from server configuration.
- **OpenAPI description** — dimension count updated to `130`; bundle counts corrected (HEAD_FACE 20, HAND_ARM 32, TORSO 29, LEGS_FEET 34); latency claim updated to `under 50 ms (typically under 10 ms on a warmed server)`.
- **`README.md`** — Updated to v1.4.0 API contract: corrected request/response schema examples, bundle counts, version strings.
- **`adult_ridge_v4.0`** training metadata updated to reference Track 6+7 validation results.

---

## [1.3.2] — Engine Calibration & Reliability

### Fixed

- **Hip circumference accuracy** — Fallback derivation updated from theoretical CAESAR population ratios to empirically validated ANSUR II coefficients (`2.959` male / `2.896` female). Residual bias `< ±2 mm`.
- **Head circumference calibration** — Bias corrections updated to `+7.0 mm` (male) / `+8.5 mm` (female) based on expanded ANSUR II holdout validation. Residual bias reduced to `< ±1.5 mm`.
- **Anchor preservation** — User-provided anchor measurements are preserved exactly as supplied and returned in `body_dimensions` with `"type": "MEASURED"` and `confidence_score: 100`. The `calculated_anchors` response header is correctly populated when the Imputation Engine derives missing values.
- **Imputation confidence propagation** — Confidence penalties from anchor imputation are propagated to all output scores, reflecting anchor quality across all imputation scenarios.
- **Pediatric engine boundary handling** — Age values at CDC LMS table boundaries are clamped to the valid interpolation range with a diagnostic warning. The prediction block includes structured exception handling for graceful degradation on all edge inputs.
- **Input flexibility** — `specific_dimensions: []` (empty array) is interpreted as no filter — all available dimensions are returned. Consistent with the principle of least surprise.

### Changed

- `input_unit_system` field added to `InputData`; imperial-to-metric pre-validation converter; `specific_dimensions` validator relaxed.
- Anchor preservation and confidence propagation logic updated in the integration layer.
- Output formatter updated with overwrite logic for user-measured dimensions.
- Pediatric engine extended with boundary clamping and structured exception handling.

---

## [1.3.1] — Automatic Engine Routing & Performance

### Added

- **`AUTO` calculation model** — `calculation_model` now accepts `"AUTO"` as the default value. The engine routes automatically: `exact_age ≤ 20y` → PEDIATRIC; otherwise → ADULT. Eliminates the need for callers to specify the engine explicitly in the common case. Schema pattern updated to `^(AUTO|ADULT|PEDIATRIC)$`.

### Changed

- **`input_origin_region` / `target_region` contract finalised** — The deprecated `region` parameter (announced in 1.3.0) has been removed. The Universal Translator's two-step model is now expressed exclusively via `input_origin_region` (Step A: input normalisation) and `target_region` (Step B: output calibration).
- **Per-request reflection overhead eliminated** — Dynamic dispatch replaced with direct keyword-argument calls throughout the integration layer, removing 6 runtime reflection operations per request.

---

## [1.3.0] — Request Schema Redesign & Deployment Stack

### Added

**Request / Response Contract**
- Restructured `PredictionRequest` into a two-level hierarchy: `input_data` (subject, anchors, input unit system) and `output_settings` (calculation parameters, dimension filters, output format).
- Introduced `input_origin_region` and `target_region` as independent fields, enabling Universal Translator Step A (input normalisation) and Step B (output calibration) to operate on different regional baselines within a single request. The legacy `region` parameter is deprecated and will be removed in the next minor release.
- `age_category: "ADULT"` added as an explicit default value; engine selection logic derived from `age_category` + `calculation_model` combination.
- `system_info` block in every response: `api_version`, `model_version`, `computation_time_ms`.
- `include_range_95` and `include_iso_codes` boolean flags in `output_settings.output_format` for payload size control.
- `description` field on each `MeasurementDetail` entry, sourced from the Master Data Dictionary.

**Pediatric Validation**
- `biological_limits_pediatric_v2.json` — age-banded P1/P99 biological limits derived from CDC Growth Charts 2000 LMS parameters via inverse Box-Cox transform. Supersedes the flat-range `v1` fallback for all requests that include `exact_age`.
- `generate_pediatric_limits.py` — reproducible CLI generator for the v2 limits file from source CDC CSV data.
- Biological limits gate extended with `age_months` / `gender` parameters; linear interpolation between LMS table entries.

**Deployment Stack**
- Multi-stage Dockerfile (builder → slim runtime). Non-root user `appuser` (UID 1001). `HEALTHCHECK` directive; Gunicorn + UvicornWorker process model.
- `docker-compose.yml` with health checks, `env_file` binding, and memory limits.
- `/v1/info` endpoint for capability discovery (available regions, bundles, age groups, model versions).

**Documentation**
- `README.md` — architecture overview, quick-start guide, full request/response reference, Known Limitations.
- `CHANGELOG.md` — this file.
- Swagger UI enriched with five pre-built request examples, per-field descriptions, and a Confidence Score disclaimer per ADR-003.

### Changed

- Validators extended with age-banded interpolation for pediatric biological limits gate.
- Configuration constants established: `VERSION`, `API_V1_STR`, `PEDIATRIC_MODEL_VERSION`.
- `/v1/predict` endpoint wired to the prediction integration layer; Swagger metadata enriched with per-field descriptions.
- `gunicorn 22.0.0` added to production dependencies.

### Architecture Decisions (ADR)

| # | Decision |
|---|----------|
| ADR-003 | Confidence Score is a proprietary heuristic index [0–100]. It is not a frequentist 95% prediction interval. Disclaimer text required in all public-facing documentation. |
| ADR-004 | `input_origin_region` and `target_region` are semantically distinct. Mixing them in a single request generates a `meta_warnings` entry. |
| ADR-005 | Age category takes precedence over `calculation_model` in engine selection. When `age_category` is a pediatric group (`INFANT`–`TEEN`), the Pediatric Engine is selected. |
| ADR-006 | `biological_limits_pediatric_v1.json` (flat limits) is retained as a fallback when `age_months` is unavailable. |

---

## [1.2.0] — Hardening & Calibration

### Fixed

- **`interpupillary_distance` precision** — Training data precision audit corrected the unit scale of `interpupillary_distance` measurements. Models retrained on corrected data. Post-correction MAE: 2.94 mm — within the 5 mm clinical accuracy threshold.
- **Civilian waist accuracy for high-BMI subjects** — NHANES morphing slope replaced with a staged dampening schedule (BMI ≤ 25 → 1.00×, 25–30 → 0.70×, 30–35 → 0.40×, > 35 → 0.15×), eliminating double-counting of the obesity signal already encoded in `body_mass`. Waist prediction accuracy for subjects at the upper end of the anthropometric range significantly improved.
- **`upper_arm_length` / `chest_breadth` systematic bias** — Methodological difference between ANSUR II (training) and ANSUR I (validation) measurement protocols introduced consistent negative bias. Post-processing bias corrections applied per gender. `upper_arm_length` residual bias: −0.69 mm.
- **Confidence Score calibration** — Confidence tier 81–87 was undershooting empirical 95% prediction interval coverage. Root cause: the tier was dominated by `body_height + wrist_circumference` requests where wrist provides no meaningful signal for circumference predictions. `PRIMARY_ONE FLESH` confidence adjusted from 85 to 78 (TERTIARY bucket). `chest_breadth` SEE scaled by 1.08×.
- **Bundle key contamination** — `TORSO`, `HEAD_FACE`, `HAND_ARM`, and `LEGS_FEET` bundles returned keys from adjacent segments. Fixed via explicit `BUNDLE_KEYS` dispatch table in the output formatter.

### Changed

- Training data corrected and models retrained for `interpupillary_distance`.
- Modifier pipeline: staged BMI dampening schedule; Deurenberg BMI offsets for `INDIA` (+1.5) and `AFRICA` (−1.0) added alongside existing `ASIA_PACIFIC` (+2.0).
- Adult engine: per-gender bias corrections and SEE adjustments updated per validation results.

### Precision Validation v2.0 Results (23,856 calls, ANSUR I + NHANES holdout)

| Metric | Result | Target |
|--------|--------|--------|
| Scenario A avg MAE | 14.1 mm | ≤ 16 mm ✓ |
| `interpupillary_distance` MAE | 2.9 mm | < 5 mm ✓ |
| NHANES 95PI coverage | 77–79 % | > 75 % ✓ |
| `upper_arm_length` bias | −0.7 mm | < ±5 mm ✓ |
| `chest_breadth` 95PI coverage | 85.1 % | > 85 % ✓ |

---

## [1.1.0] — Confidence Recalibration

### Changed

- **Confidence Score v3** — Three-phase recalibration cycle validated against ANSUR I holdout data. Confidence bracket 60–69 effectively eliminated. Bracket 80–89 now dominant at 62.6%. Final tier base values: `PRIMARY_BOTH` 95, `PRIMARY_ONE` 91, `SECONDARY` 88, `TERTIARY` 86.
- Adult engine confidence adjustment overrides updated to v3 values. No changes to Ridge regression models; Δ MAE v1→v3 ≤ 0.15 mm (within statistical noise).

### Philosophy

The API is calibrated to never overpromise. The Confidence Score gap (stated confidence vs. empirical coverage) is always ≥ 0. Users receive results that are as good as or better than advertised.

---

## [1.0.0] — Initial Release

### Added

**Dual-Core Prediction Engine**
- **Adult Engine** — Ridge Regression hybrid (36 BONE + 14 FLESH log-log models per gender). Trained on ANSUR II (3,404 male / 1,626 female samples post IQR cleaning). Duan's Smearing Factor for FLESH back-transformation. StandardScaler fitted on `body_height` + `body_mass` anchors.
- **Pediatric Engine** — LMS Box-Cox methodology per WHO/CDC Growth Charts 2000. CDC precision: ±0.01 mm (height), ±0.001 kg (mass). Covers ages 0–20 years with linear interpolation between table entries.

**Dynamic Anchor Imputation**
- Ridge-based imputation engine with 277 models per gender (50 single-anchor + 105 double-anchor + 120 triple-anchor + 2 cross-target). Confidence penalty normalised as `RMSE / SD(body_height)`, bounded [0.0, 1.0]. Adjusted SEE formula: `base_SEE × (1 + penalty × 0.5)`.

**Modifier Pipeline**
- Regional calibration for 7 macro-regions (GLOBAL, EUROPE, ASIA_PACIFIC, AFRICA, LATAM, INDIA, MIDDLE_EAST). Dual-path implementation: Z-Score matching for CAESAR reference keys; coefficient-direct path for all others.
- Universal Translator: Step A normalises input anchors to the ANSUR II reference frame; Step B calibrates output to the target regional distribution. Eliminates double-penalty artefacts for non-US subjects.
- Civilian Body Composition Engine: Deurenberg (1991) equation + NHANES population slopes. Regional BMI offsets per WHO / Gallagher et al. evidence base.
- BMI-stratified civilian morphing (14 FLESH measurements); NASA-STD-3001 microgravity elongation modifier.
- Anatomical enrichment via validated skeletal proportion constants (Greiner): direct Ridge predictions extended with anatomically derived measurements, expanding body surface coverage without additional model complexity.

**Dimension Catalog**
- Catalog quality criteria established at v1.0.0: each dimension must satisfy (1) distinct commercial application in at least one primary vertical, (2) validated prediction accuracy within tissue-class MAE tolerance, (3) no duplication. Dimensions are classified as BONE (skeletal landmarks) or FLESH (soft tissue) and carry ISO 7250-1:2017 codes where applicable.

**Validation & Safety**
- Biological Limits Gate: NASA-STD-3001 for adults; CDC P1/P99 age-banded limits for pediatric subjects.
- Input validation: whitelist for `region`, `bundle`, `age_group`; path-traversal protection; cross-field validators.
- Fail-fast startup: API refuses to start with missing data or model artefacts; returns `HTTP 503` from `/health` rather than false-positive `200 OK`.

**API Surface**
- `POST /v1/predict` — primary prediction endpoint.
- `GET /health` — active dependency check (data directory, model artefacts, NASA limits).
- `GET /v1/info` — capability discovery.
- `GET /docs` / `GET /redoc` — interactive Swagger UI and ReDoc documentation.

### Known Limitations

| Area | Detail |
|------|--------|
| MIDDLE_EAST female | Regional coefficients derived from the global baseline dataset; dedicated local anthropometric study not yet available. |
| AFRICA confidence intervals | Standard deviations proxied from ANSUR II global values with a conservative penalty applied. |
| INDIA female | Body measurements use ASIA_PACIFIC fallback coefficients; HEAD_FACE bundle uses GLOBAL baseline. |
| `head_circumference` (pediatric) | CDC LMS table covers 0–36 months. Values for older children clamped to 36-month boundary with warning. |
| Multi-anchor imputation | Imputer selects the single strongest anchor. Providing multiple weak anchors does not compound accuracy. |
| `wrist_circumference` as sole anchor | Produces systematic bias on large circumference predictions (waist, hip). Confidence correctly reduced to TERTIARY tier. |

---

*DimensionsPot API is developed and maintained by the DimensionsPot engineering team.*  
*For support: support@dimensionspot.com*
<br>
<br> 
<br>
<br>

> <br>
>
> ### **Disclaimer And Limitation Of Liability**
>
> All outputs of the DimensionsPot API ("Outputs") are statistically derived anthropometric predictions intended to support — not replace — professional judgment. They do not constitute medical, clinical, ergonomic, or professional advice, and must not be used as the sole basis for health decisions, product design, manufacturing tolerances, safety assessments, regulatory submissions, or contractual specifications. The Confidence Score is a proprietary heuristic index — not a statistical confidence interval.
>
> To the fullest extent permitted by applicable law, DimensionsPot and its operators disclaim all liability for any direct, indirect, incidental, consequential, or punitive damages — including bodily injury, property damage, financial loss, business interruption, or contractual liability — arising from reliance on Outputs.
>
> *This disclaimer does not exclude liability where prohibited by mandatory applicable law.*
>
> <br> 
