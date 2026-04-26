### Wearables & Smart Accessories
# **Strap, Ring, and Band Sizing Without the Measuring Tape**

<br>

### **What you're dealing with**

Sizing is the highest-friction moment in the wearables purchase journey. A smartwatch band, a fitness tracker strap, a smart ring — each one requires a measurement the customer doesn't have, doesn't know how to take correctly, and won't go find a tool to take accurately. The result is predictable: customers either bracket-buy (a ring in two sizes), guess and return, or abandon the cart entirely because "I don't know my ring size" is exactly the kind of friction that kills a mobile checkout at 11pm.

And unlike an apparel e-commerce flow — where height and weight are sometimes standard profile fields — wearables checkout typically asks for shipping address and payment, and that's it. The customer has never been asked for their physical dimensions on your site before.

<br>

### **Where the money is**

* **Accessory attach rates:** Bands, straps, and ring SKUs that were previously "one size" or "pick from three" can be offered with a confident default preselected. Removing the "do I need to measure?" hesitation at the exact moment the customer is deciding to add the accessory to cart is where the lift shows up.
* **Ring returns in particular:** Smart rings have an outsized return problem driven almost entirely by sizing. A correctly-predicted PIP joint width at checkout replaces the "order two sizes, return one" behavior that's become the category default.
* **Checkout conversion:** Two fields added to the cart flow — "your height" and "your weight (optional)" — in exchange for a confirmed size recommendation. Customers who share the numbers are the same ones who would otherwise have bracketed, returned, or abandoned. The ask is small, the value exchange is clear, and the friction cost is low.

<br>

### **What we actually do**

We predict wrist circumference, wrist breadth, hand dimensions, finger widths (including the PIP joint width that determines ring size), and ankle circumference from height and weight — two numbers customers know by heart and will share when there's a clear reason to. In under 10ms, no additional measurement step.

Ring sizing specifically depends on PIP joint width. Not hand circumference, not finger length — the proximal interphalangeal joint width is the governing dimension. We return it (`hand_digit_4_width_pip`) explicitly, because the common mistake in smart ring sizing is routing on the wrong proxy.

<br>

### **Where we're upfront**

Hand and wrist circumferences are among the stronger dimensions we predict — confidence on wrist circumference and PIP joint width with height + weight anchors sits around 78 on our index (soft-tissue, `PRIMARY_BOTH` tier), and skeletal hand dimensions run higher at ~85. That's the right precision for routing to the correct band size variant or ring size out of a typical 6–10 SKU range.

Here's what that means for your checkout: a customer who didn't know their ring size now gets a confident default, preselected for them, with no tools required. The band that was "one size fits most" becomes a routed SKU. The ring that was returned because "it was loose on my finger" gets sized correctly the first time. Two small fields added to the flow, and the category's worst return-rate reason starts disappearing from your dashboard.

<br>

---
