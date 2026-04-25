# Business Context — Revised Versions for Integration Cookbooks

Styl sladěn se Solution Briefs v3: upřímný, přímý, bez marketingových superlativů. Členění Problem → Solution → Bonus zachováno. Stručnost zachována (cookbook primárně míří na vývojáře, Business Context slouží jako krátké ukotvení před technickou částí).

Fashion (01) ponechávám beze změny — text už je v nastoleném tónu a funguje.

---

## 01 — Fashion & Apparel E-commerce

*Beze změny. Stávající text je v pořádku a odpovídá stylu Solution Briefs.*

---

## 02 — Sports Equipment Rental

**The Problem:** The rental counter is where your revenue bottlenecks during peak hours. In practice, your staff isn't measuring every customer with a tape — they're pulling boots, helmets, and harnesses off the rack and watching the customer try them on until something fits. That trial-and-error loop burns 7–9 minutes per customer. The ceiling on your Saturday revenue is set not by demand but by how many fitting loops your counter can run in parallel.

**The Solution:** You already collect height and weight at online booking (or you can — it's one extra field). DimensionsPot takes those two numbers and returns a complete, 130-point anthropometric profile in under 10ms. Before the customer walks through the door, your system already knows their foot length, head circumference, chest, and inseam. Check-in becomes a two-minute handover, not a ten-minute trial session.

**The Procurement Edge:** Aggregate the same API calls across a season of bookings and you have a real size distribution for your actual customer base — not a catalog standard. Your procurement team orders 47 Medium boots and 23 Large helmets, not "a mixed pallet, roughly half-and-half." The mid-season emergency re-order cycle is the first line item most operators discover they can cut.

---

## 03 — Online Eyewear & VR/AR

**The Problem:** Frame fit is the single largest return driver in online optical. Customers don't know their face width, bridge size, or whether a temple length will pinch behind the ear — so they bracket-buy across sizes, and the ones who don't bracket tend to return. On the VR/AR side, a strap that's 10mm too tight causes pressure headaches, and a light seal that doesn't match face depth leaks light and breaks immersion. Virtual try-on solves the aesthetic question; it doesn't solve fit.

**The Solution:** Two numbers most customers already know — height and weight — captured at the point of size selection. DimensionsPot takes those two inputs and returns up to 24 precise head and face dimensions in under 10ms. No cameras, no scans, no PII. One API call tells you which frame front width fits the face, which temple length reaches behind the ears, and which headset strap size matches the customer's head circumference. The customer walks away from the product page believing they picked the right size the first time.

**The Customization Edge:** The real margin move happens between order and dispatch. Route the order to the correct temple length SKU, select the Asian-fit or standard rim based on facial proportions, and ship the headset with the matching light-seal cushion already installed. Same checkout, fewer returns, higher fulfilment accuracy — driven by two fields and one API call.

---

## 04 — Gaming, VFX & Metaverse

**The Problem:** A height slider doesn't create a personalized avatar — it just stretches a generic mesh. The underlying skeletal proportions were authored by eye, not measured, which is why your technical artists spend a disproportionate share of their time fixing deformation in the same joints (shoulders, hips, knees, wrists) on every character variant. And when design asks for 50 NPC body variants for an open-world crowd, you're either spending art days per variant or shipping obvious clones.

**The Solution:** You need height and weight. DimensionsPot takes those two inputs and returns a complete, 130-point anthropometric profile in under 10ms. You get exact bone lengths to drive the skeletal rig, and precise circumferences to control the blend shapes. Players building their own avatar get a character that actually matches their physical body — their shoulder breadth, their torso-to-leg ratio, their real build. Not a stretched default.

**The Crowd Multiplier:** For open-world games and VFX, populating backgrounds with diverse, realistic bodies is a resource sink. DimensionsPot lets you generate statistically accurate NPCs programmatically. By adjusting `target_region` and `body_build_type`, you spawn a crowd with accurate Asian skeletal proportions or European civilian body fat distributions in a scripting loop — no manual modeling required.

---

## 05 — Wearables

**The Problem:** Wearable returns share a single root cause: the device didn't fit. S/M/L guidance on a product page doesn't get read. A loose band corrupts the optical signal, and the user blames the sensor. A smart ring that's off by one size ships back by day three. Bracket-ordering is still standard practice in the category, and the reverse logistics bill and the sizing-kit budget are the same problem on different SKUs.

**The Solution:** Replace the sizing kit with a short prompt at size selection. DimensionsPot takes the height and weight your customer will share when there's a clear reason to, and returns wrist, hand, ankle, and finger dimensions — including the PIP joint width that actually determines ring size — in under 10ms. No camera, no PII. The correct size variant drops into the picking list before the order leaves the warehouse.

**The Boundary Safety Net:** Every dimension ships with a 95% prediction interval. When a predicted value lands near a size threshold, both adjacent sizes surface automatically in the UI. The customer chooses based on fit preference ("I like my ring a little loose"), not a blind guess.

---

## 06 — Childrenswear & Children's Products

**The Problem:** "Ages 2–4" isn't a size — it's a population estimate disguised as a label. Designers can't validate their patterns against a known dimensional envelope, parents can't trust the tags, and retailers sourcing globally have no reliable way to verify whether an "Ages 2–4" from one region covers the same children as the same label from another.

**The Solution:** DimensionsPot converts age and gender into a complete, 130-point anthropometric profile in under 10ms. Grounded in CDC-validated population data, the API returns median dimensions for height, weight, chest, waist, and 126 other metrics — plus a 95% prediction interval on every one. You stop relying on vague age brackets and start working with population-calibrated specifications you can verify.

- ***The Designer's Edge:*** Query the API at the boundaries and midpoint of an age bracket to establish the exact dimensional envelope your pattern needs to cover. Your size chart becomes a reflection of the actual target population, not a competitor's guesswork copied forward one more season.

- ***The Parent's Edge:*** Decode labels for your customers. Show exactly what "Ages 2–4" means in centimeters, as a range — chest, height, inseam. Parents with a measured child can compare directly, which eliminates the most common reason for returns in the category.

- ***The Retailer's Edge:*** Validate cross-border fit before the PO goes out. The dimensional envelope behind the same age label varies significantly between an Asian supplier and a European manufacturer. By comparing profiles across `target_region` settings, buyers identify proportional mismatches before the container ships, not after it lands.

**The Longevity Projection:** Power your own growth forecasting. By comparing current age data against a 12 or 18-month projection against CDC median growth curves, your application can estimate when a typical child will outgrow a product. "Fits most children until approximately age 3.5" — a data point that builds parent trust in a category where every competitor is still hiding behind vague brackets.

---

## 07 — Workwear at Scale

**The Problem:** A uniform rollout isn't a design problem — it's a data collection problem with a predictable failure pattern. Sizing forms go out, half don't come back, the ones that do contain guesses, and procurement places an order based on a mix of assumptions and buffer stock. Two months later you're re-ordering Mediums while a pallet of XLs sits in the warehouse. Physical sizing sessions work better and cost you weeks per site.

**The Solution:** Your HRIS already stores height and weight (safety records, medical surveillance, site access). DimensionsPot converts those two fields into a complete, 130-point anthropometric profile in under 10ms. You get the exact chest, waist, inseam, and foot length measurements required to define your order specifications before the first employee walks through the door. You cut the planning cycle from weeks to seconds — a workforce of 1,000 runs in under 10 seconds at moderate concurrency.

**The Procurement Edge:** Turn HR data into a precise demand forecast. By processing your workforce list through the API, logistics knows exactly how many units of each size to stock for the specific group being outfitted. You secure bulk discounts with confidence, accelerate the entire purchasing cycle, and eliminate the emergency re-order cycle that eats your margin every rollout.

---

## 08 — Multi-Region Platform

**The Problem:** Global expansion and cross-border sourcing fail on a single issue: population-level skeletal proportions. 170 cm and 70 kg in Tokyo produces measurably different chest, waist, and shoulder dimensions than the same anchors in Berlin. Whether you serve a global audience or source from Asian factories for European customers, you're guessing your way through systematic population differences — and guessing is what keeps the return rate where it is.

**The Solution:** Fix it with one parameter: `input_origin_region`. The API interprets measurements in their correct proportional context and returns a complete, 130-point anthropometric profile in under 10ms. You see the actual physical dimensions the manufacturer intended, validate them against your target market, and get the ground truth before the bulk order goes out. No manual offset tables, no per-market code hacks.

**The Strategic Edge:** Use `target_region` to master cross-regional validation. Align predictions with your specific brand fit model, or compare the "Sourcing Delta" between two populations by calling the API twice with different regional settings. You identify fit gaps before committing to a bulk order or a new market launch. Which regional "M" fits your audience stops being a guess — it becomes a dimension-by-dimension comparison you can read in the response payload.
