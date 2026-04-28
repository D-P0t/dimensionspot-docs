### Workwear at Scale
# **Your HR Data Already Contains the Sizing Answer**

<br>

### **What you're dealing with**

A uniform rollout for 5,000 employees is not a design problem. It's a data collection problem with a predictable failure pattern: sizing forms go out, half don't come back, the ones that do come back contain guesses, and your procurement team places an order based on a mix of assumptions and buffer stock. Two months later you're re-ordering Mediums while a pallet of XLs sits in the warehouse.

Physical sizing sessions work better — and cost you weeks per site, scheduled around shift patterns, with a clipboard, for a job that should take minutes per person.

<br>

### **Where the money is**

* **Clinic elimination:** The sizing clinic is the most visible time sink and the easiest to cost. Replacing it with an API call against existing HR data removes weeks from uniform rollout timelines. Onboarding can run in parallel with procurement instead of sequentially.
* **Demand modelling:** Aggregate the profiles across the workforce and you have an exact size distribution per garment category before the PO is placed. Order 47 Medium coveralls and 23 Large jackets — not "a mixed pallet, roughly half-and-half." This is the procurement saving that compounds every refresh cycle.
* **Zero-emergency re-orders:** The re-order cycle caused by size guesswork disappears when the initial order is sized against real workforce data.

<br>

### **What we actually do**

Your HRIS already stores height and weight for most employees (safety records, medical surveillance, site access). We take those two fields and return a full 130-point body profile per employee in under 10ms: jacket size inputs, trouser inseam and waist, glove size, boot length, head circumference for helmets and headgear. One API call per employee. A workforce of 1,000 runs in under 10 seconds at moderate concurrency¹.

Multinational workforces get calibrated automatically. If you have operations across EMEA, APAC, and LATAM, setting `target_region` per employee cohort handles the population-level proportion differences in a single integration — no per-market offset tables, no regional spreadsheet hacks.

<br>

### **Where we're upfront**

Confidence for skeletal dimensions (inseam, head circumference, foot length) is ~85/100 with height + weight; circumferences (chest, waist, glove) are ~78. That's the right precision for standard-issue workwear routed to catalog sizes. For bespoke garments or specialized PPE where a physical fit check is part of your safety protocol, we're the starting point that makes the physical session shorter, not a replacement for it.

**A note on data:** The API is stateless and processes only numerical measurements — no names, no IDs, no PII. Your HR integration handles the employee identification layer; we handle the measurement math. GDPR implementation remains yours, but we deliberately don't hold the data that would create a compliance risk for you.

What this delivers: the uniform programme that used to block every new-site launch for six weeks now runs in parallel with onboarding. The procurement order is sized against real workforce data, not a buffer-stock guess. And the employee who would have waited three weeks for the right-size jacket now walks in on day one and finds it waiting.

<br>
<br>

---
*¹ P99 API latency 6.2ms direct / 8.5ms Dockerised; 1,000 employees processed at moderate concurrency in under 10 seconds. ² Procurement cycle estimates based on standard medium-to-large enterprise uniform programmes; actual timelines depend on supplier lead times and HR data completeness.*
