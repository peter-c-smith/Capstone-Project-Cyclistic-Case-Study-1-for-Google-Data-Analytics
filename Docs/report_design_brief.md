# Cyclistic Power BI Report — Design Brief

## Theme & Colors
- **Theme:** Executive (built-in)
- **Member color:** #1F77B4 (blue) — apply manually to all visuals
- **Casual color:** #FF7F0E (orange) — apply manually to all visuals
- **Disclaimer text color:** #7F5A00 (amber) — for revenue page warnings
- **Subtitle/secondary text:** #666666 (gray)

---

## Design Principles
- Member/casual colors are applied manually on every visual — never rely on default theme color order
- Every page has a finding-first title, not a topic title
- Each page should be readable as a standalone — a viewer who only sees one page should understand the key point
- Card backgrounds should be turned off or lightened — Executive theme can render them heavy
- All revenue visuals must carry a visible on-page disclaimer label
- Consistent font sizes: page title 20pt, section headers 14pt, body/labels 11pt

---

## Page Titles

| Page | Title |
|------|-------|
| 1 — Executive Summary | "Casual and Member Riders Use Cyclistic in Fundamentally Different Ways" |
| 2 — Ride Behavior | "Casual Riders Take Longer, More Leisurely Rides Than Members" |
| 3 — Temporal Patterns | "Members Ride on Schedule — Casuals Ride for Leisure" |
| 4 — Bike Type & Station | "Members and Casuals Favor Different Bikes and Different Places" |
| 5 — Revenue Opportunity | "Converting Casual Riders to Members Represents Significant Revenue Potential" |

---

## Page-by-Page Visual Plan

### Page 1 — Executive Summary
*"Casual and Member Riders Use Cyclistic in Fundamentally Different Ways"*

- KPI cards: Total Rides, Member Ride %, Avg Ride Duration, Avg Ride Distance
- Donut chart: Member vs Casual ride split
- KPI cards for behavioral ratios: Duration Ratio, Weekend Skew Ratio, Round Trip Ratio
- Small text annotation explaining what values above 1 mean for each ratio
- **Goal:** A stakeholder who only sees this page walks away understanding the core finding

---

### Page 2 — Ride Behavior
*"Casual Riders Take Longer, More Leisurely Rides Than Members"*

**Layout:**

**Row 1 — Duration card pair**
- Card: Avg Duration Member (blue, #1F77B4)
- Card: Avg Duration Casual (orange, #FF7F0E)
- Dynamic callout beneath: Annotation Duration Card Callout measure

**Row 2 — Distance card pair**
- Card: Avg Ride Distance Member (blue, #1F77B4)
- Card: Avg Ride Distance Casual (orange, #FF7F0E)
- Dynamic callout beneath: Annotation Distance Card Callout measure

**Row 3 — Clustered bar chart**
- Category axis: Member / Casual
- Values: Weekend Ride % and Round Trip rate (Casual Round Trips / Casual Rides vs Member Round Trips / Member Rides)
- Member color: #1F77B4, Casual color: #FF7F0E
- Chart title: "Weekend & Round Trip Patterns by Rider Type"
- Y-axis: Percentage (0–100%)
- Note: Round trip values must be expressed as a percentage of each group's total rides, not raw counts, for a fair comparison

**Row 4 — Pace insight callout**
- Dynamic card: Annotation Page 2 Pace Insight measure
- Style: Segoe UI italic, 11pt, #666666, no border, no background
- Spans full width of canvas

**Goal:** Directly answer the core analysis question with behavioral data across four dimensions — duration, distance, weekend concentration, and round trip tendency — and draw the connecting insight that casual riders prioritize the experience of riding over efficient point-to-point travel.

**Notes:**
- Card backgrounds should use --color-background-secondary or be turned off entirely
- Member/casual colors must be manually set on all visuals — do not rely on theme defaults
- The round trip clustered bar requires a calculated percentage rather than raw Round Trip counts — consider adding Round Trip % Member and Round Trip % Casual as measures if not already present
- 
---

### Page 3 — Temporal Patterns
*"Members Ride on Schedule — Casuals Ride for Leisure"*

- Bar chart: Rides by hour of day (Ride Start Hour on axis, member/casual as legend) — the commuter spike should be clearly visible
- Column chart: Seasonal ride counts by member/casual
- Clustered bar: Weekday vs Weekend rides by member/casual
- **Goal:** Show that member usage follows a commuter pattern while casual usage is flatter and weekend-skewed

---

### Page 4 — Bike Type & Station
*"Members and Casuals Favor Different Bikes and Different Places"*

- Stacked bar: Bike type mix by rider type (Classic Bike % and Electric Bike %)
- Map visual: Ride start coordinates with member/casual as legend or slicer
- Bar chart: Top 10 start stations for members
- Bar chart: Top 10 start stations for casuals
- Card: Rides Missing Station Data with explanatory label
- **Goal:** Show geographic and equipment preference differences between rider types

---

### Page 5 — Revenue Opportunity (Illustrative)
*"Converting Casual Riders to Members Represents Significant Revenue Potential"*

- Prominent on-page disclaimer: *"All figures on this page are illustrative. Cyclistic is a fictional company. Pricing is modeled after publicly documented Divvy rates. See pricing_model_rationale.md for details."*
- KPI cards: Total Estimated Casual Revenue, Total Estimated Member Overage Revenue
- Bar or column chart: Estimated casual revenue by season (showing when the opportunity is largest)
- Narrative text box: The conversion argument — framing what it would mean if a portion of casual riders became members
- **Goal:** Translate behavioral findings into a business case for the marketing team

---

## Notes
- Page 5 disclaimer should appear at the top of the page in amber text (#7F5A00), not buried at the bottom
- The map visual on Page 4 requires that coordinate fields are correctly typed as Decimal Number in Power Query
- The hour-of-day chart on Page 3 is the single most compelling visual in the report — give it the most canvas space on that page
- 
### Fleet Utilization Note
True concurrent ride calculations (peak bikes in use simultaneously) are not practical in DAX due to the computational complexity of interval overlap analysis. A rides-per-hour-by-day-of-week visual using the existing Ride Start Hour column serves as a practical proxy for peak demand periods in Power BI. Full concurrency analysis will be performed in the R and Python sections of this project where interval overlap algorithms can be applied properly.

### Conversion Rate Analysis — Intentional Omission
A conversion rate analysis estimating revenue impact if a percentage of casual riders became annual members would typically accompany this section. However, this dataset does not include unique rider identifiers, making it impossible to distinguish individual users from repeat rides. Without that baseline, conversion estimates would require assumptions that compound too heavily to be defensible. This limitation is noted here in the interest of analytical integrity.

A what-if analysis of this type would require:
- Unique rider IDs to establish a true casual rider population
- Repeat ride frequency per rider to model realistic conversion behavior
- A defensible assumption about conversion rate drawn from industry benchmarks

This analysis is flagged as a recommended next step should Cyclistic provide rider-level data in the future.