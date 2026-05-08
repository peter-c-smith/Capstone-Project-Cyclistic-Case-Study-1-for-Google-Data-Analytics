# Illustrative Pricing Model — Rationale & Assumptions

*Cyclistic Capstone Project — Phase 5 Revenue Proxy*

> **Important:** The revenue figures produced by this model are entirely illustrative. Cyclistic is a fictional company and no actual pricing or revenue data exists. The pricing assumptions below are modeled after publicly documented rates from a comparable real-world system and are used solely to demonstrate analytical technique.

---

## Why Divvy Pricing Was Used as the Reference Model

The Cyclistic dataset is provided by Motivate International Inc., which operated Divvy — Chicago's public bike-share system — before Lyft acquired the company in 2018. Lyft continues to operate Divvy today. Because the underlying data structure, station geography, and ride patterns are consistent with the Divvy system, Divvy's publicly documented pricing structure was selected as the most credible real-world reference for building an illustrative revenue model.

---

## Assumed Pricing Structure

The model uses a hybrid pricing structure that mirrors Divvy's documented approach: annual members pay a flat fee covering rides up to a time threshold, while casual riders pay per ride with per-minute overage fees beyond the included time.

**Member Pricing**
- Annual membership fee: $120/year (amortized across rides — not calculated per ride in this model)
- Rides up to 45 minutes: included at no per-ride charge
- Overage beyond 45 minutes: $0.18 per minute

**Casual Rider Pricing**
- Unlock fee per ride: $3.30
- Rides up to 30 minutes: included in unlock fee
- Overage beyond 30 minutes: $0.18 per minute

---

## Mapping to Documented Divvy Rates

The assumed rates correspond directly to publicly available Divvy pricing as of 2024–2026:

- **Annual membership ($120 assumed):** Divvy annual membership has ranged from $99 to $143.90 depending on membership status and year. $120 represents a reasonable midpoint for the 2025–2026 period.
- **Casual unlock fee ($3.30 assumed):** Divvy's documented single-ride price is $3.30, which includes up to 30 minutes of ride time.
- **Per-minute overage ($0.18 assumed):** Divvy's documented overage rate for classic bikes is $0.18 per minute for both members and non-members beyond the included time threshold.

---

## Limitations of This Model

- The annual membership fee is not amortized per ride in the DAX measures. The model focuses on per-ride variable revenue only.
- Electric bike surcharges are not included. Divvy charges additional per-minute fees for e-bikes; this model applies a single rate regardless of rideable type.
- Day pass pricing is not modeled. Some casual riders may purchase day passes rather than single-ride passes; this model assumes single-ride pricing for all casual trips.
- These simplifications are intentional — the goal is to illustrate the revenue potential of converting casual riders to members, not to produce auditable financial projections.


*Sources: Divvy pricing pages, City of Chicago press releases (2024–2026), Streetsblog Chicago reporting on Divvy fare changes.*