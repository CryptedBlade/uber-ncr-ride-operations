# Uber NCR Dashboard: Requirements and Test Plan

*Retrospective document written after the build. The stakeholder is a fictional persona used for practice.*

## 1. Purpose
Help a ride operations team see where bookings are completed and where they are lost, and why.

## 2. Users
- **Operations Manager (fictional persona):** decides where to add drivers and when to run incentives.
- **Analyst:** checks the figures and drills into cancellations.

## 3. Business questions
| # | Question | Answered on |
|---|---|---|
| 1 | What share of bookings are completed? | Home, Overview |
| 2 | Who causes cancellations, drivers or customers, and why? | Cancellations |
| 3 | When is demand highest and lowest? | Demand |
| 4 | Do vehicle types differ in performance? | Vehicles |
| 5 | How much revenue is at risk from lost bookings? | Overview, Cancellations, Insights |

## 4. KPI definitions
| KPI | Definition | Source |
|---|---|---|
| Completion rate | Completed bookings / total bookings | Rides table |
| Lost bookings | Cancelled by customer or driver, no driver found, or incomplete | Rides table |
| Driver / customer cancellation rate | Cancelled by that party / total bookings | Rides table |
| Driver share of cancellations | Driver cancellations / (driver + customer cancellations) | Rides table |
| Revenue | Sum of fares for completed rides only (incomplete rides excluded) | Rides table |
| Average fare | Revenue / completed rides | Rides table |
| Revenue at risk (estimate) | (Cancelled by driver + cancelled by customer + no driver found) x average fare | Rides table |
| Peak vs quietest | Bookings in the busiest hour / bookings in the quietest hour | Rides and time tables |

Data model: one Rides fact table with DimDate, DimTime and DimVehicle dimensions (`powerbi_data/`).

## 5. Functional requirements
- **FR1:** The dashboard has 7 pages in this order: Home, Overview, Demand, Cancellations, Revenue, Vehicles, Insights. A page navigator appears on every page.
- **FR2:** Date and vehicle-type slicers appear on Overview, Demand, Cancellations and Revenue, and stay in sync across those four pages. Overview also has a Month/Quarter toggle for "Bookings per day" that is not synced.
- **FR3:** KPI cards show the headline figures. Home: total bookings, completion rate, revenue, lost bookings. Overview adds average fare and revenue at risk.
- **FR4:** Home has fleet buttons: All vehicles plus the 7 vehicle types (Auto, Bike, eBike, Go Mini, Go Sedan, Premier Sedan, Uber XL). Selecting one filters the Home page and updates the "Showing:" label.
- **FR5:** Vehicles shows all 7 types side by side (no slicers). Insights states the key findings, recommendations and data notes in plain language.
- **FR6:** Home and Insights state that the dataset is probably synthetic and that findings describe this data, not Uber's real business.

## 6. Non-functional requirements
- Data covers 1 January 2024 to 30 December 2024: 150,000 bookings across 365 distinct days.
- Pages open without visible delay: each page loads in under 1 second in Power BI Desktop (see T18).
- Dark theme with a consistent navigation panel on every page.
- Repeated booking IDs are kept as separate rides (a unique RideKey identifies each ride).

## 7. Out of scope
Live data refresh, driver-level data, forecasting, and any claim about Uber's real business.

## 8. Acceptance criteria
Every test below passes, and every headline figure matches the Python analysis and the data files.

## 9. Test plan
*Method: T1 to T12 were checked by recomputing figures from `powerbi_data/rides.csv` with pandas (`python tests/verify_figures.py` reproduces them) and comparing them with the dashboard screenshots; T13 inspected the report file's structure. T14 to T18 were run by the author in Power BI Desktop.*

| ID | Requirement | Steps | Expected | Actual | Pass/Fail |
|---|---|---|---|---|---|
| T1 | FR3 | Read total bookings on Home and Overview | 150,000 | 150K on both pages | Pass |
| T2 | FR3 | Read completion rate and the "Completed" funnel bar | 62.0% (93,000) | 62.0%; funnel 93.0K | Pass |
| T3 | FR3 | Read revenue and average fare | ₹47.26M and ₹508 | ₹47.26M and ₹508 (data: ₹47.26M, ₹508.2) | Pass |
| T4 | Data | Add all booking statuses | Equals total bookings | 93,000 + 27,000 + 10,500 + 10,500 + 9,000 = 150,000 | Pass |
| T5 | FR3 | Read the booking funnel | 150.0K, 139.5K, 102.0K, 93.0K | 150.0K, 139.5K, 102.0K, 93.0K | Pass |
| T6 | FR3 | Read lost bookings and revenue at risk | 57K and ₹24.4M | 57K and ₹24.4M (data: 57,000; 48,000 x ₹508.2 = ₹24.39M) | Pass |
| T7 | Demand | Read peak hour and peak vs quietest | 18:00 and 9.4x | 18:00 and 9.4x (data: 12,397 vs 1,321 = 9.38) | Pass |
| T8 | Cancellations | Read driver and customer cancellation rates; read the driver share on Insights | 18.0%, 7.0%, 72% | 18.0%, 7.0%, 72% (data: 27,000 / 10,500 / 37,500) | Pass |
| T9 | FR5 | Add the 7 vehicle booking counts; read completion range | Sum 150,000; 61.4% to 62.6% | 150,000; 61.4% to 62.6% | Pass |
| T10 | Revenue | Read UPI and digital shares | 45.0% and 75.1% | 45.0% and 75.1% | Pass |
| T11 | FR5 | Compare Insights text with recomputed data (62%, 72%, ₹24.4M, 44%, 18:00 and 9.4x, 41%, 2%, 407 to 416 per day, 0.6 and 1.2 points, 45% and 75%, 0.006) | All match | All match (note: Insights text is static, so update it by hand if the data changes) | Pass |
| T12 | Data | Check RideKey uniqueness and repeated booking IDs | RideKey unique; repeats kept | RideKey unique (150,000 of 150,000); 1,224 booking IDs repeat on 1,233 extra rides, all kept | Pass |
| T13 | FR1 | Inspect page order and navigators | 7 pages in the stated order; navigator on each | Order confirmed; one navigator on each of the 7 pages | Pass |
| T14 | FR2 | Change the date slicer on Overview, then open Demand, Cancellations and Revenue | Same date range on all four pages | Run in Power BI Desktop: behaved as expected on all four pages | Pass |
| T15 | FR4 | On Home, click each fleet button in turn | "Showing:" label and Home KPI cards change for each type | Run in Power BI Desktop: behaved as expected for every button | Pass |
| T16 | FR4 | After selecting a vehicle, click All vehicles | Cards return to 150K, 62.0%, ₹47.26M, 57K | Run in Power BI Desktop: cards returned to the full figures | Pass |
| T17 | FR1 | From every page, click each item in the navigator | Each opens the correct page | Run in Power BI Desktop: every item opened the correct page | Pass |
| T18 | NFR | Open each page and time how long it takes to fully load | No visible delay; each page under 1 second | Run in Power BI Desktop: every page loaded in under 1 second, smoothly (author's observation, not a stopwatch measurement) | Pass |

## 10. Defects and corrections
1. **Wording on Insights (fixed).** The "Definitions and data notes" box said "1,233 booking IDs repeat on different rides." The data shows 1,224 booking IDs that appear more than once, producing 1,233 extra rides. The author corrected the wording in Power BI, and the note now matches the data.
2. **Requirements did not match the build (fixed in this version).** The first draft listed the pages in the wrong order (Revenue comes before Vehicles), said filters apply to every page (Vehicles and Insights have no slicers), described the vehicle selector as filtering every visual (it filters the Home page), expected a "72%" card (the 72% appears on Insights; the Cancellations cards show 18.0% and 7.0%), and expected no duplicate booking IDs (repeated IDs are kept on purpose).
3. **Data range note.** The last booking date is 30 December 2024, so the date slicers end at 30-12-2024.

## 11. UAT sign-off
- [x] All tests passed (T1 to T18)
- [x] Known limits listed (synthetic data; Insights text is static; revenue at risk is an estimate)
- Signed off by: Harshvardhan Singh, 03/11/2026
