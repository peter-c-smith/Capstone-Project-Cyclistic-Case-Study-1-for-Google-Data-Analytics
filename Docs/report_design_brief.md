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
- Every page has a finding-first title placed in a text box at the top of the canvas — the page tab name should be a short version (e.g. "Executive Summary") while the full finding-first title appears on the canvas
- Each page should be readable as a standalone — a viewer who only sees one page should understand the key point
- Card backgrounds should be turned off or lightened — Executive theme can render them heavy
- All revenue visuals must carry a visible on-page disclaimer label
- Consistent font sizes: page title 20pt, section headers 14pt, body/labels 11pt, annotation cards 11pt italic
- Annotation card style: Segoe UI italic, 11pt, #666666, no border, no background

---

## Slicer Behavior

A time frame date range slicer is placed on Page 1 and synced across all pages via View → Sync Slicers. The slicer is visible on Page 1 and hidden on all other pages. All measures respond to the slicer as intended — filtering by date updates all pages simultaneously.

**Known limitation:** Seasonal measures (Spring Rides, Summer Rides, Fall Rides, Winter Rides) will return blank for seasons outside the selected date range. This is expected behavior, not a bug. A text box near the slicer on Page 1 reads: *"Adjusting the time frame will update all pages. Seasonal metrics may appear incomplete if a partial year is selected."*

---

## Page Titles

| Page | Canvas Title | Tab Name |
|------|-------------|----------|
| 1 — Executive Summary | "Casual and Member Riders Use Cyclistic in Fundamentally Different Ways" | Executive Summary |
| 2 — Ride Behavior | "Casual Riders Take Longer, More Leisurely Rides Than Members" | Ride Behavior |
| 3 — Temporal Patterns | "Members Ride on Schedule — Casuals Ride for Leisure" | Temporal Patterns |
| 4 — Bike Type & Station | "Members and Casuals Favor Different Bikes and Different Places" | Bike Type & Station |
| 5 — Revenue Opportunity | "Converting Casual Riders to Members Represents Significant Revenue Potential" | Revenue Opportunity |

---

## Page-by-Page Visual Plan

### Page 1 — Executive Summary

**Top row — KPI cards**
- Card: Total Rides
- Card: Member Ride %
- Card: Avg Ride Duration (min)
- Card: Avg Ride Distance (mi)

**Middle row — Donut chart and Time Frame slicer**
- Donut chart: Member Rides vs Casual Rides (member blue #1F77B4, casual orange #FF7F0E)
- Time frame date range slicer (right side)
- Slicer note text box beneath slicer: *"Adjusting the time frame will update all pages. Seasonal metrics may appear incomplete if a partial year is selected."* Style: Segoe UI italic, 10pt, #666666

**Bottom row — Behavioral ratio cards**
- Card: Duration Ratio Casual to Member
- Card: Weekend Skew Ratio
- Card: Round Trip Ratio Casual to Member
- Card: Distance Ratio Casual to Member
- Annotation card beneath each: Annotation Duration Ratio, Annotation Weekend Skew, Annotation Round Trip Ratio, Annotation Distance Ratio

**Full width callout at bottom**
- Dynamic card: Annotation Pace Insight
- Spans full canvas width beneath the four ratio cards

**Goal:** A stakeholder who only sees this page walks away understanding the core finding — casual and member riders use Cyclistic in fundamentally different ways across duration, distance, weekend concentration, and round trip behavior.

---

### Page 2 — Ride Behavior

**Row 1 — Duration card pair**
- Card: Avg Duration Member Display (blue value, #1F77B4)
- Card: Avg Duration Casual Display (orange value, #FF7F0E)
- Dynamic callout spanning full width beneath: Annotation Duration Card Callout

**Row 2 — Distance card pair**
- Card: Avg Ride Distance Member Display (blue value, #1F77B4)
- Card: Avg Ride Distance Casual Display (orange value, #FF7F0E)
- Dynamic callout spanning full width beneath: Annotation Distance Card Callout

**Row 3 — Clustered column chart**
- X-axis: Metric Groups[Metric] (two categories: "Weekend %" and "Round Trip %")
- Y-axis series 1: Member % by Metric (color #1F77B4)
- Y-axis series 2: Casual % by Metric (color #FF7F0E)
- Y-axis label: Percentage of Rides
- Chart title: "Weekend & Round Trip Patterns by Rider Type"
- Note: Uses the Metric Groups calculated table and SWITCH measures to drive two clusters in a single chart

**Row 4 — Pace insight callout**
- Dynamic card: Annotation Page 2 Pace Insight
- Spans full canvas width

**Goal:** Directly answer the core analysis question with behavioral data across four dimensions — duration, distance, weekend concentration, and round trip tendency — and draw the connecting insight that casual riders prioritize the experience of riding over efficient point-to-point travel.

**Notes:**
- Card values colored manually: member #1F77B4, casual #FF7F0E
- Card titles set manually — do not use auto-generated measure names
- Display measures (Avg Duration Member Display etc.) used in cards — not the raw numeric measures

---

### Page 3 — Temporal Patterns

**Top — Hour of day chart (largest visual on page)**
- Bar chart: Rides by hour of day
- X-axis: Ride Start Hour Label (sorted by Ride Start Hour)
- Y-axis: Total Rides
- Legend: member_casual field (member #1F77B4, casual #FF7F0E)
- The member commuter spike at 8 AM and 5 PM vs the flatter casual midday distribution is the key story

**Bottom left — Seasonal ride counts**
- Clustered column chart
- X-axis: Season from Date table (sorted by Season Sort column)
- Y-axis: Member Rides and Casual Rides
- Colors: member #1F77B4, casual #FF7F0E

**Bottom right — Weekday vs Weekend rides**
- Clustered column chart
- X-axis: Day Type Groups[Day Type] (two categories: "Weekday" and "Weekend")
- Y-axis series 1: Member Rides by Day Type (color #1F77B4)
- Y-axis series 2: Casual Rides by Day Type (color #FF7F0E)
- Note: Uses the Day Type Groups calculated table and SWITCH measures to drive clean category labels

**Full width callout at bottom**
- Dynamic card: Annotation Page 3 Temporal Insight

**Goal:** Show that member usage follows a commuter pattern — peaking at rush hours and concentrated on weekdays — while casual usage is flatter, weekend-skewed, and seasonally concentrated in summer.

---

### Page 4 — Bike Type & Station

**Top left — Bike type mix**
- Stacked bar chart: Bike type mix by rider type
- X-axis: member_casual
- Y-axis: Classic Bike % and Electric Bike %
- Note: Bike type colors are intentionally different from member/casual colors since they represent bike types not rider types

**Top right — Map**
- Map visual using start_lat and start_lng coordinate fields
- member_casual as legend (member #1F77B4, casual #FF7F0E)
- Coordinate fields must be typed as Decimal Number in Power Query
- Rider Type filter/legend slicer on the right

**Bottom left — Top 10 member start stations**
- Horizontal bar chart
- Y-axis: start_station_name (filtered to top 10 by ride count, empty strings excluded)
- X-axis: Member Rides with Start Station
- Color: #1F77B4
- Title: "Top Ten Member Start Locations (minus missing)"

**Bottom right — Top 10 casual start stations**
- Horizontal bar chart
- Y-axis: start_station_name (filtered to top 10 by ride count, empty strings excluded)
- X-axis: Casual Rides with Start Station
- Color: #FF7F0E
- Title: "Top 10 Casual Start Stations (minus missing)"

**Bottom — Missing station data**
- Card: Rides Missing Station Data
- Dynamic annotation card: Annotation Missing Station Data
- Note: Station name fields contain empty strings ("") rather than true blanks — visual filters use "is not empty" rather than "is not blank"

**Goal:** Show geographic and equipment preference differences between rider types. Casual stations cluster at tourist/lakefront locations (DuSable Lake Shore, Navy Pier, Millennium Park) while member stations cluster near transit hubs and offices.

---

### Page 5 — Revenue Opportunity (Illustrative)

**Top — Prominent disclaimer**
- Text box spanning full canvas width
- *"All figures on this page are illustrative. Cyclistic is a fictional company. Pricing is modeled after publicly documented Divvy rates. See pricing_model_rationale.md for details."*
- Style: Segoe UI italic, 11pt, #7F5A00 (amber)

**KPI cards row**
- Card: Total Estimated Casual Revenue (orange value, #FF7F0E)
- Card: Total Estimated Member Overage Revenue (blue value, #1F77B4)
- Card: Estimated Casual Revenue per Ride (orange value, #FF7F0E)

**Seasonal revenue chart**
- Clustered column chart
- X-axis: Season from Date table
- Y-axis: Total Estimated Casual Revenue
- Color: #FF7F0E
- Title: "Total Estimated Casual Revenue by Season"

**Narrative text box**
- Bold header: "The Conversion Opportunity"
- Body text explaining the business case for converting casual riders to members
- Bold header: "Note on Conversion Rate Modeling"
- Body text documenting the intentional omission of conversion rate analysis
- Style: Segoe UI, 11pt, #444444 body, bold headers 12pt

**Goal:** Translate behavioral findings into a business case for the marketing team using illustrative revenue figures modeled after documented Divvy pricing.

---

## Notes
- Page 5 disclaimer should appear at the top of the page in amber text (#7F5A00), not buried at the bottom
- The map visual on Page 4 requires that coordinate fields are correctly typed as Decimal Number in Power Query
- The hour-of-day chart on Page 3 is the single most compelling visual in the report — give it the most canvas space on that page
- The time frame slicer on Page 1 is synced to all pages via View → Sync Slicers — visible on Page 1 only

---

## Fleet Utilization Note
True concurrent ride calculations (peak bikes in use simultaneously) are not practical in DAX due to the computational complexity of interval overlap analysis. A rides-per-hour-by-day-of-week visual using the existing Ride Start Hour column serves as a practical proxy for peak demand periods in Power BI. Full concurrency analysis will be performed in the R and Python sections of this project where interval overlap algorithms can be applied properly.

---

## Conversion Rate Analysis — Intentional Omission
A conversion rate analysis estimating revenue impact if a percentage of casual riders became annual members would typically accompany this section. However, this dataset does not include unique rider identifiers, making it impossible to distinguish individual users from repeat rides. Without that baseline, conversion estimates would require assumptions that compound too heavily to be defensible. This limitation is noted here in the interest of analytical integrity.

A what-if analysis of this type would require:
- Unique rider IDs to establish a true casual rider population
- Repeat ride frequency per rider to model realistic conversion behavior
- A defensible assumption about conversion rate drawn from industry benchmarks

This analysis is flagged as a recommended next step should Cyclistic provide rider-level data in the future.
