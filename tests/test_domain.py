import json
import unittest
from pathlib import Path

from rv_logbook.domain import Trip, TravelDay, money, number


class DomainModelTest(unittest.TestCase):
    def test_trip_from_dict_normalizes_travel_days_and_totals(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))

        trip = Trip.from_dict(data)

        self.assertEqual(trip.id, "sample-trip-001")
        self.assertEqual(trip.name, "Sample Blue Ridge Weekend")
        self.assertEqual(len(trip.travel_days), 1)
        self.assertIsInstance(trip.travel_days[0], TravelDay)
        self.assertEqual(trip.total_miles, 210)
        self.assertEqual(trip.campground_count, 1)
        self.assertEqual(trip.total_fuel_cost, 165.75)
        self.assertEqual(trip.total_expense_cost, 28.50)
        self.assertEqual(trip.total_maintenance_cost, 0)
        self.assertEqual(trip.total_cost, 194.25)
        self.assertEqual(trip.highlights, ["Good weather", "Easy check-in"])
        self.assertEqual(trip.lessons_learned, ["Start earlier on Friday travel days."])

    def test_trip_to_template_context_preserves_original_fields_and_derived_values(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))

        context = Trip.from_dict(data).to_template_context()

        self.assertEqual(context["name"], "Sample Blue Ridge Weekend")
        self.assertEqual(context["total_miles"], "210")
        self.assertEqual(context["fuel_cost"], "$165.75")
        self.assertEqual(context["total_cost"], "$194.25")
        self.assertEqual(context["campground_count"], 1)

    def test_travel_day_context_formats_drive_time(self):
        day = TravelDay.from_dict(
            {
                "id": "day-1",
                "trip_id": "trip-1",
                "date": "2026-05-01",
                "drive_time_minutes": 95,
            }
        )

        context = day.to_template_context()

        self.assertEqual(day.drive_time, "1h 35m")
        self.assertEqual(context["drive_time"], "1h 35m")
        self.assertEqual(context["arrival_notes"], "")

    def test_money_and_number_formatting(self):
        self.assertEqual(money(0), "$0.00")
        self.assertEqual(money(12.5), "$12.50")
        self.assertEqual(number(42.5), "42.50")
        self.assertEqual(number(210.0), "210")


if __name__ == "__main__":
    unittest.main()
