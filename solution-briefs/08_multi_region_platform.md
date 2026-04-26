### Global Retail & Multi-Region Platforms
# **Crossing the Sizing Border, Honestly**

<br>

### **What you're dealing with**

Cross-border expansion looks good on the finance model and terrible on the returns dashboard. The headline problem — US 10 vs. IT 42 vs. JP 11 — is just a labelling issue; a conversion chart solves it. The underlying problem is that populations have measurably different body proportions: limb-to-torso ratios, shoulder-to-hip ratios, head breadth. A garment designed against a European fit block will systematically fit an East Asian customer differently, and no amount of label translation changes that.

The result is a return rate in new markets that your initial business case didn't budget for, a slow trust erosion that shows up first in reviews and then in conversion, and an expansion that lands at a margin well below projection.

<br>

### **Where the money is**

* **Cross-border returns:** International returns cost materially more to process than domestic ones¹. A regionally-calibrated size recommendation compresses the single largest margin leak in new-market expansion.
* **Sourcing validation:** Query the same demographic with different regional settings and get the dimension-by-dimension delta. This is the procurement safeguard you want before signing a bulk contract with a supplier in a different region than your end market — not after.
* **Market entry speed:** You scale into new regions on the same integration, with population-calibrated fit from day one. No local sizing studies required before launch.

<br>

### **What we actually do**

One parameter pair: `input_origin_region` (your customer's population) and `target_region` (the population your size chart was built for). The API handles the translation before inference runs, so the output dimensions are calibrated to the right population — not scaled with a naive offset.

"Double penalty" is the thing that separates us from simpler conversion libraries. Naive regional scaling takes a smaller anchor measurement (say, Asian height) and applies it to a globally-trained model that interprets "shorter" as "smaller overall" — compounding the error across every dependent dimension. We normalize the input to the global ANSUR baseline first (Universal Translator Step A), then calibrate the output to the target region (Step B). Two independent steps, one request.

<br>

### **Where we're upfront**

Our region coverage is not uniform, and we say so in the documentation. We calibrate against 7 regions: GLOBAL (ANSUR II baseline), EUROPE, ASIA_PACIFIC, LATAM — all full coverage; INDIA has a female fallback to ASIA_PACIFIC where source data is thin; AFRICA is male-only Sub-Saharan proxy data; MIDDLE_EAST is male-only. This is the reality of publicly available anthropometric datasets, not a roadmap aspiration.

Here's what that means for your expansion roadmap: in the regions where our calibration is full (which cover the majority of global consumer purchasing power), you get population-accurate fit from the first order in a new market. In the regions where coverage is partial, you get a known-quality floor with documented limitations, not a black box that fails silently. Either way, the cross-border returns line item — the one that quietly erodes every new-market margin projection — compresses from day one of launch.

<br>

---
*¹ Pitney Bowes BOXpoll, "International Returns Study," 2023. ² Regional calibration source data: ANSUR II (DoD, public domain), NHANES (CDC, public domain), published regional anthropometric studies. Coverage notes per region in API reference.*
