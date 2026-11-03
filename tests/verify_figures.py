"""
Recompute every headline figure on the Uber NCR dashboard from the data file
and compare it with the value shown on the dashboard.

Run from the repository root:
    python tests/verify_figures.py

Needs: pandas  (pip install pandas)
Exit code is 0 when every check passes, 1 otherwise.
"""
import sys
from pathlib import Path

import pandas as pd

RIDES = Path(__file__).resolve().parent.parent / "powerbi_data" / "rides.csv"

rides = pd.read_csv(RIDES)
completed = rides[rides["IsCompleted"] == 1]
n = len(rides)

results = []


def check(test_id, description, actual, expected, tolerance=0.0):
    """Record one check. Numbers are compared within a tolerance."""
    if isinstance(expected, (int, float)):
        passed = abs(actual - expected) <= tolerance
    else:
        passed = actual == expected
    results.append((test_id, description, actual, expected, passed))


# T1 Total bookings
check("T1", "Total bookings", n, 150_000)

# T2 Completion rate
check("T2", "Completed bookings", int(rides["IsCompleted"].sum()), 93_000)
check("T2", "Completion rate (%)", round(rides["IsCompleted"].mean() * 100, 1), 62.0, 0.05)

# T3 Revenue and average fare
revenue = rides["CompletedRevenue"].sum()
avg_fare = completed["BookingValue"].mean()
check("T3", "Revenue (INR million)", round(revenue / 1e6, 2), 47.26, 0.005)
check("T3", "Average fare (INR, rounded)", round(avg_fare), 508)

# T4 Statuses add up to the total
status_counts = rides["BookingStatus"].value_counts()
check("T4", "Sum of all booking statuses", int(status_counts.sum()), 150_000)

# T5 Booking funnel
no_driver = int(rides["IsNoDriverFound"].sum())
driver_cancel = int(rides["IsCancelledByDriver"].sum())
customer_cancel = int(rides["IsCancelledByCustomer"].sum())
check("T5", "Funnel: driver found", n - no_driver, 139_500)
check("T5", "Funnel: ride started", n - no_driver - driver_cancel - customer_cancel, 102_000)
check("T5", "Funnel: completed", int(rides["IsCompleted"].sum()), 93_000)

# T6 Lost bookings and revenue at risk
check("T6", "Lost bookings", int((rides["IsCompleted"] == 0).sum()), 57_000)
at_risk = (driver_cancel + customer_cancel + no_driver) * avg_fare
check("T6", "Revenue at risk (INR million)", round(at_risk / 1e6, 1), 24.4, 0.05)

# T7 Peak hour and peak vs quietest
by_hour = rides["Hour"].value_counts()
check("T7", "Peak hour", int(by_hour.idxmax()), 18)
check("T7", "Peak vs quietest (x)", round(by_hour.max() / by_hour.min(), 1), 9.4, 0.05)

# T8 Cancellation rates and driver share
check("T8", "Driver cancellation rate (%)", round(driver_cancel / n * 100, 1), 18.0, 0.05)
check("T8", "Customer cancellation rate (%)", round(customer_cancel / n * 100, 1), 7.0, 0.05)
check("T8", "Driver share of cancellations (%)",
      round(driver_cancel / (driver_cancel + customer_cancel) * 100, 1), 72.0, 0.05)

# T9 Vehicle table
by_vehicle = rides.groupby("VehicleType").agg(bookings=("RideKey", "count"),
                                              completion=("IsCompleted", "mean"))
check("T9", "Vehicle bookings add up", int(by_vehicle["bookings"].sum()), 150_000)
check("T9", "Lowest vehicle completion (%)", round(by_vehicle["completion"].min() * 100, 1), 61.4, 0.05)
check("T9", "Highest vehicle completion (%)", round(by_vehicle["completion"].max() * 100, 1), 62.6, 0.05)

# T10 Payment shares
by_payment = completed.groupby("PaymentMethod")["CompletedRevenue"].sum()
check("T10", "UPI share of revenue (%)", round(by_payment["UPI"] / by_payment.sum() * 100, 1), 45.0, 0.05)
digital = by_payment.drop("Cash").sum()
check("T10", "Digital share of revenue (%)", round(digital / by_payment.sum() * 100, 1), 75.1, 0.05)

# T11 Other figures quoted on the Insights page
check("T11", "Customer cancellations citing driver behaviour (%)",
      round(rides["CustomerCancelReason"].isin(
          ["Driver is not moving towards pickup location", "Driver asked to cancel"]).sum()
          / customer_cancel * 100, 1), 44.1, 0.05)
check("T11", "Evening Peak share, 15:00 to 20:59 (%)",
      round(rides["Hour"].between(15, 20).mean() * 100, 1), 41.3, 0.05)
check("T11", "Correlation of fare and distance",
      round(completed["BookingValue"].corr(completed["RideDistance"]), 3), 0.006, 0.0005)
check("T11", "Incomplete rides: booking value excluded (INR million)",
      round(rides["IncompleteValue"].sum() / 1e6, 2), 4.59, 0.005)

# T12 Ride keys and repeated booking IDs
check("T12", "RideKey is unique", bool(rides["RideKey"].is_unique), True)
counts = rides["BookingID"].value_counts()
repeated = counts[counts > 1]
check("T12", "Booking IDs that repeat", len(repeated), 1_224)
check("T12", "Extra rides created by repeated IDs", int(repeated.sum() - len(repeated)), 1_233)

# ---- Report ----
width = max(len(r[1]) for r in results)
failures = 0
for test_id, description, actual, expected, passed in results:
    mark = "PASS" if passed else "FAIL"
    if not passed:
        failures += 1
    print(f"{mark}  {test_id:<4} {description:<{width}}  actual={actual}  expected={expected}")

print()
print(f"{len(results) - failures} of {len(results)} checks passed")
sys.exit(1 if failures else 0)
