# DimensionsPot | **BodySize Engine**
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![ISO 7250-1](https://img.shields.io/badge/ISO_7250--1-2017_Compliant-E05A00)
![RapidAPI](https://img.shields.io/badge/Available_on-RapidAPI-0055DA)

### [→ Get API Access on RapidAPI](https://rapidapi.com/d-pot-apps/api/dimensionspot-bodysize-engine) <br><br>
<kbd>SOLUTION BRIEFS</kbd> **[&nbsp;READ](https://github.com/D-P0t/dimensionspot-api/tree/main/solution-briefs)**  &emsp;&emsp; <kbd>INTEGRATION COOKBOOKS</kbd> **[&nbsp;READ](https://github.com/D-P0t/dimensionspot-api/tree/main/integration-cookbooks)**

<br>

DimensionsPot is a REST API that **generates a comprehensive anthropometric profile from minimal user input**. It is designed for teams, services, and projects that use body data in any capacity. Trained on the world's most renowned anthropometric surveys, the API returns up to **130 ISO 7250-1 standardized body dimensions**, eliminates the friction of physical measurements or photo uploads, and is **fully stateless**: no user data is stored, logged, or retained between calls.

The engine takes as little as a single known "anchor" measurement and gender to infer a complete profile of 130 body dimensions in under 10ms. It uses statistical regression models to fill the data gap, providing a calibrated **Confidence Score for every output**. Height and weight — the two measurements most users know without a tape — are the strongest anchors, and adding any circumference on top of these anchors pushes precision and Confidence Score even higher. That said, the API works with any single body measurement. This allows you to **automate sizing logic, ergonomic presets, or avatar scaling without specialized hardware**.

### **Privacy-by-Design: Why No Photos?**

DimensionsPot is the only high-fidelity alternative to photogrammetry that requires **zero biometric images** and **stores no user data whatsoever**. The API accepts only numerical measurements — no names, emails, images, or user identifiers ever enter the system.

| | **DimensionsPot** | **Photo-based (3DLook, Bodygram)** |
|---|---|---|
| User input | Gender + any single measurement | 2 full-body photos, specific pose & lighting |
| Data stored | Nothing — fully stateless | Photos retained for model inference |
| Privacy risk | Zero — no PII, no biometric data | Photos = biometric data under GDPR Art. 9 |
| GDPR compliance | ✅ No biometric data collected | Requires explicit consent + legal basis |
| EU AI Act | ✅ No prohibited biometric categorization | Biometric ID systems face strict obligations |
| Integration | REST JSON, <10ms | Camera SDK + image upload pipeline + GPU |
| Pediatric support | ✅ LMS/CDC (ages 0–20), zero measurements needed | Generally limited to adults |

*Any link between a biometric profile and a specific individual exists exclusively in your own infrastructure.*

<br>

### **What You'd Build With This**

Seven integration patterns, one API. Each maps to a full Integration Cookbook in the documentation.

- **Size recommendation on product pages** — fashion, eyewear, workwear, childrenswear. Customer supplies height + weight (or a single known measurement), you surface the right size on the product page before they add to cart. Typical outcome: fewer fit-related returns, lower bracketing rate, higher checkout confidence.

- **Accessory sizing for wearables** — smartwatch bands, smart rings, VR/AR head straps. Predict wrist circumference, PIP joint width, head circumference, and face depth from height + weight. The correct variant drops into the picking list before dispatch. No measuring tape, no customer confusion.

- **Avatar skeletons for games & metaverse** — predict 130 dimensions including bone lengths, joint heights, shoulder and hip breadths. ISO-coded output maps directly to Unity Humanoid, Unreal MetaHuman, or proprietary rigs. Build player avatars that match real bodies — not stretched defaults.

- **Workforce sizing from HR data** — take height and weight from your HRIS, output a full 130-point body profile per employee in under 10ms. A workforce of 1,000 processes in under 10 seconds. Procurement orders exact size distributions, eliminating the sizing clinic.

- **Pre-sized gear for rental operations** — customer books online with height + weight, staff pre-stages boots, helmets, wetsuits before arrival. Counter handover drops from a 7-minute trial loop to a 2-minute transaction.

- **Cross-regional fit validation** — query the same subject with different `input_origin_region` and `target_region` settings. Compare dimension-by-dimension how an Asian-built size chart will fit a European customer before the bulk order ships. Turn sourcing risk into a data-verified decision.

- **Pediatric product design** — CDC/WHO-grounded profiles for ages 0–20 with a 95% prediction interval on every dimension. Translate vague age labels ("Ages 2–4") into verifiable dimensional envelopes for pattern makers and parents.

<br>

### **Bundles**

| Bundle | Dimensions | Key measurements |
|---|---|---|
| `FULL_BODY` | **130** | All available dimensions |
| `HEAD_FACE` | 20 | IPD, head breadth, face length, bridge width, bitragion arcs, neck circumference |
| `HAND_ARM` | 32 | All digit lengths & widths, wrist, forearm, arm length, span, reach |
| `TORSO` | 29 | Chest, waist, hip, shoulder breadth, sitting heights, bust/underbust |
| `LEGS_FEET` | 34 | Full foot geometry, calf, knee, inseam, ankle, trochanterion |

Use `specific_dimensions` to cherry-pick any arbitrary subset across bundles in a single call.

<br>

## The Inference Pipeline

DimensionsPot uses a deterministic **9-step orchestration** to ensure biological validity and mathematical precision:

1. **Input Validation:** Strict Pydantic-based schema verification and unit normalization (Metric/Imperial).
2. **Pre-Imputation Normalization:** The Universal Translator (Step A) converts regional input measurements to a global ANSUR baseline to eliminate the Double Penalty Paradox.
3. **Dynamic Anchor Imputation:** If primary anchors (height/weight) are missing, the Ridge Imputation Engine infers them from available data with a proportional confidence penalty applied to all downstream outputs.
4. **Dual-Core Inference:** Requests are routed to either the Adult Ridge Regression Engine (trained on ANSUR II) or the Pediatric Hybrid Engine — a two-stage system where the LMS Box-Cox method (CDC Growth Charts 2000) provides age-specific body_height and body_mass, which are then used as anchors for a scaled Adult Ridge pass to generate the full-dimensional profile.
5. **Regional Calibration:** The Universal Translator (Step B) applies Z-score matching and coefficient-based calibration to shift proportions toward the target population's specific norms.
6. **Civilian Body Composition:** Application of the Deurenberg equation and NHANES fat distribution slopes to adjust ANSUR military baseline proportions for civilian BMI and regional body composition.
7. **Anatomical Enrichment:** Detail injection for fingers, face, and feet using Greiner-style anatomical ratio models.
8. **Biological Limits Gate:** Every output is cross-checked against NASA-STD-3001 (adults) or CDC P1–P99 (pediatrics) to flag values outside population bounds.
9. **Output Formatting:** Final unit conversion, ISO 7250-1 code mapping, confidence threshold filtering, and response assembly.

<br>

## The Trust Factor: Calibrated Confidence Score

Every one of the 130 output dimensions carries a `confidence_score` — a heuristic reliability index **[0–100]** that reflects prediction uncertainty based on anchor quality and imputation method. The system **never over-promises**: actual 95% prediction interval coverage is always ≥ the reported confidence score.

The score is determined by two factors: the **quality of anchors supplied** (anchor tier) and the **measurement type** (skeletal BONE dimensions are more predictable than soft-tissue FLESH dimensions).

| Anchor Tier | What you supplied | BONE score | FLESH score |
|---|---|---|---|
| `PRIMARY_RICH` | Height + mass + ≥1 precision circumference | ~87 | ~80 |
| `PRIMARY_BOTH` | Height + mass | ~85 | ~78 |
| `PRIMARY_ONE` | Height OR mass (not both) | ~79 | ~62 |
| `SECONDARY` | Foot length, knee height, span, etc. | ~74 | ~67 |
| `TERTIARY` | Any other single measurement | ~69 | ~62 |

Scores decrease further (up to −10 pts) when primary anchors are derived via imputation rather than supplied directly.

**Disclaimer:** `confidence_score` is a **proprietary heuristic reliability index**, not a frequentist p-value or a statistical 95% prediction interval probability.

Use `confidence_score_threshold` to automatically filter out low-confidence dimensions. Every dimension also ships with an optional **95% prediction interval** (`include_range_95`) and its **ISO 7250-1 code** (`include_iso_codes`) — useful for compliance-sensitive integrations.

<br>

## Regional Calibration & Body Build Types

### Universal Translator — 7 Regional Models

`input_origin_region` and `target_region` are **independent fields**, enabling full cross-regional requests (e.g., measure an Asian subject, output for a European manufacturer).

- **`input_origin_region`** — normalizes input measurements to the ANSUR global baseline before prediction (eliminates Double Penalty Paradox)
- **`target_region`** — calibrates output dimensions to the target population after prediction

| Region | Population Source | Coverage |
|---|---|---|
| `GLOBAL` | ANSUR II (US Military) | ✅ Full |
| `EUROPE` | Aggregated European datasets | ✅ Full |
| `ASIA_PACIFIC` | East Asian & Pacific datasets | ✅ Full |
| `LATAM` | Latin American datasets | ✅ Full |
| `INDIA` | South Asian regional data | ⚠️ Female fallback to ASIA_PACIFIC |
| `AFRICA` | Sub-Saharan proxy data | ⚠️ Male-only, SD proxy |
| `MIDDLE_EAST` | Middle Eastern regional data | ⚠️ Male-only |

### Body Build Types

| Type | Description | Use Case |
|---|---|---|
| `CIVILIAN` | NHANES general population morphing | E-commerce, general public |
| `ATHLETIC` | Military/sports baseline (no NHANES shift) | Sportswear, uniforms, PPE |
| `OVERWEIGHT` | BMI-adjusted circumference morphing | Plus-size fashion |

<br>

## The Business Case: Will This Pay For Itself?

The honest answer depends on your category and your baseline return rate. But the math is simple enough to run against your own numbers.

### A worked example — mid-range online fashion store

| Input | Value | Benchmark source |
|---|---|---|
| Monthly orders | 5,000 | Mid-range online fashion store |
| Average order value | $97 | Industry fashion benchmark |
| Return rate | 25% | Fashion category baseline |
| Cost per return | $15–$20 | Reverse logistics + restocking |
| **Current monthly return cost** | **~$20,000–$25,000** | 1,250 returns × $15–$20 |

If fit-driven returns are **reduced by 15–20%**, the saving lands around **$3,000–$5,000 per month** — and scales roughly linearly with order volume.

<br>

### Typical impact ranges across verticals

| Metric | Estimated Impact | Mechanism |
|---|---|---|
| **Fit-driven return rate** | **−15% to −25%** | Eliminates bracket buying and ill-fitting returns |
| **Checkout conversion** | **+5% to +12%** | Fit confidence reduces cart abandonment |
| **Accessory attach rate** (wearables) | **+10% to +20%** | Confident band/ring sizing at the point of decision |
| **Uniform sizing lead time** | **weeks → minutes** | HRIS → API replaces physical sizing clinic |

<br>

## High-ROI Verticals

- **Fashion & Apparel E-commerce** — full body profiles from height/weight → instant size recommendations
- **Sports Equipment & Rental** — helmets, wetsuits, ski boots, bikes pre-sized from self-reported inputs
- **Online Eyewear & VR/AR Headsets** — IPD, face length, head breadth, bridge width without a photo
- **Gaming, VFX & Metaverse** — regionally calibrated skeletal dimensions for Unity Humanoid / Unreal MetaHuman
- **Wearables** — smartwatch bands, fitness trackers, smart rings from height alone
- **Childrenswear & Children's Products** — CDC-calibrated profiles for ages 0–20 (INFANT → TEEN), zero measurements required
- **Workwear at Scale** — workforce sizing from HR data without physical measurement sessions
- **Multi-Region Platform** — accurate body profiles across 7 population regions; cross-regional sourcing validation for global platforms

→ Implementation guides for each vertical: [Integration Cookbooks](https://github.com/D-P0t/dimensionspot-api/tree/main/integration-cookbooks)

<br>

## Performance

| Metric | Value |
|---|---|
| HTTP P99 latency (direct) | 6.2ms |
| HTTP P99 latency (Docker / Cloud Run) | 8.5ms |
| MAE — primary anchors (ANSUR I validation) | 14.14mm (~0.9% of body height) |
| Validation calls — API errors | ~150,000 calls — **0 errors (0.00%)** |
| Output dimensions | **130** across 5 bundles |

<br>

## Pricing & Plans

| Plan | Price/Month | API Calls | Best For |
|---|---|---|---|
| **Free** | $0 | 100 | Proof of concept, testing |
| **Starter** | $79 | 2,000 | Small e-commerce, indie developers |
| **Pro** | $299 | 10,000 | Medium brands, fashion platforms |
| **Business** | $799 | 50,000 | Large retailers, SaaS integrations |
| **Enterprise** | Contact Us | Unlimited | Custom models, on-premise deployment |

→ Subscribe and manage your plan on [RapidAPI](https://rapidapi.com/d-pot-apps/api/dimensionspot-bodysize-engine).

<br>

## Data Ethics & Compliance

- **No PII collected** — API accepts only numerical measurements, never names, emails, images, or user IDs
- **Stateless processing** — data processed in-memory, nothing retained between calls
- **Training data** — ANSUR II (DoD, public domain) + NHANES (CDC, public domain) + CDC/WHO growth tables (public domain)
- **Biological limits** — every dimension validated against NASA-STD-3001 (structural) and CDC P1–P99 (circumferences); status returned as `biological_limit_status` per dimension
- **EU AI Act ready** — no prohibited biometric categorization or social scoring

<br>

## Quick Links

- [Quick Start](https://github.com/D-P0t/dimensionspot-api/blob/main/QUICK_START.md) → First API call in 3 minutes, full response walkthrough
- [Data Dictionary](https://github.com/D-P0t/dimensionspot-api/blob/main/DATA_DICTIONARY.md) → All 130 dimensions with ISO 7250-1 codes
- [Integration Cookbooks](https://github.com/D-P0t/dimensionspot-api/tree/main/integration-cookbooks) → Vertical-specific integration patterns with code examples
- [Solution Briefs](https://github.com/D-P0t/dimensionspot-api/tree/main/solution-briefs) → One-pager business cases per vertical
- [Changelog](https://github.com/D-P0t/dimensionspot-api/blob/main/CHANGELOG.md)
- **Support:** support@dimensionspot.com

<br>

### Disclaimer And Limitation Of Liability

*All outputs of the DimensionsPot API ("Outputs") are statistically derived anthropometric predictions intended to support — not replace — professional judgment. They do not constitute medical, clinical, ergonomic, or professional advice, and must not be used as the sole basis for health decisions, product design, manufacturing tolerances, safety assessments, regulatory submissions, or contractual specifications. The Confidence Score is a proprietary heuristic index — not a statistical confidence interval.*

*To the fullest extent permitted by applicable law, DimensionsPot and its operators disclaim all liability for any direct, indirect, incidental, consequential, or punitive damages — including bodily injury, property damage, financial loss, business interruption, or contractual liability — arising from reliance on Outputs.*

*This disclaimer does not exclude liability where prohibited by mandatory applicable law.*
