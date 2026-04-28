### Fashion & Apparel E-commerce
# **A Straight Answer to the Returns Problem**

<br>

### **What you're dealing with**

You already know the numbers on your dashboard. Return rates in online fashion routinely sit above 40%, the majority of them tagged "wrong size or fit"¹. Every returned parcel is a reverse-logistics bill of roughly $20–$30 you've already paid before the refund leaves your account². Bracketing — customers ordering two or three sizes on purpose — is a rational response to size charts they've learned not to trust, and it's baked into your cost structure whether you priced for it or not.

You don't need another plugin that promises to fix this with a photo upload. Most of them don't survive the checkout funnel: camera-based onboarding drops off hard, and your customer isn't going to find a measuring tape on a mobile device.

<br>

### **Where the money is**

* **Returns:** Industry benchmarks for AI-driven sizing sit in the −20% to −30% returns range³. Your actual result depends on your current bracketing rate, your size chart quality, and how aggressively you surface the recommendation. We'd rather you model it against your own return data than take the headline number.
* **Conversion:** When a customer trusts that the size they're ordering is actually the right one, they stop bracketing, they stop hesitating, and they complete the checkout. Fit anxiety is a documented cart-abandonment driver⁴ — removing it tends to lift overall conversion in the low double digits.
* **Integration cost:** One REST endpoint, no model to train, no per-market tuning. If you have a size chart as a lookup table, the mapping is client-side Python (example in the Integration Cookbook).

<br>

### **What we actually do**

We take the two numbers your customer already knows — height and weight — and return the body dimensions you need to route a size: chest, natural waist, hip, shoulder breadth, inseam, thigh. 130 dimensions total, ISO 7250-1 coded, delivered in under 10ms. No photos, no scans, no extra checkout step.

Cross-border fit isn't solved by a conversion table. A customer in Seoul buying from a Berlin-built size chart has different skeletal proportions, not just different label conventions. Our `input_origin_region` / `target_region` pair handles this in one request, across 7 calibrated population regions.

<br>

### **Where we're upfront**

With height + weight (our `PRIMARY_BOTH` tier), skeletal dimensions score around 85/100 on our confidence index and circumferences around 78 — the confidence score ships with every dimension, so you set the threshold. Regional coverage is not uniform (known data gaps are documented in the API reference).

Here's what that means for you: those numbers are good enough to drive a confident size recommendation against your existing size chart, across your existing regions, with your existing checkout. You stop your customers from guessing, bracketing drops, and the returns line item compresses. That's the outcome, and it's delivered through two fields you're already collecting.

<br>
<br>

---
*¹ Statista, Global E-Commerce Returns Rate by Vertical, 2024. ² Narvar Consumer Report, 2024. ³ Industry estimates for fit-tech integrations; results vary by vertical and implementation. ⁴ Baymard Institute, E-Commerce UX research, 2024.*
