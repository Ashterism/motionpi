import json
import tempfile
import time
import unittest
from pathlib import Path

from motionpi.process.pir_diagnostics import PIRDiagnostics


class TemporaryStorage:
    def __init__(self, root):
        self.meta_dir = Path(root)

    def read_json(self, filepath):
        if not filepath.exists():
            return None
        with open(filepath, "r") as handle:
            return json.load(handle)


class PIRDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.diagnostics = PIRDiagnostics(
            TemporaryStorage(self.temp_directory.name)
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_records_only_actual_pir_transitions(self):
        self.diagnostics.record_reading(0)
        self.diagnostics.record_reading(0)
        self.diagnostics.record_reading(1)

        snapshot = self.diagnostics.snapshot()

        self.assertEqual(snapshot["pir_state"], "HIGH")
        self.assertEqual(snapshot["transitions_last_60_seconds"], 1)
        self.assertEqual(snapshot["events"][0]["message"], "PIR LOW → HIGH")

    def test_capture_trigger_is_reported(self):
        self.diagnostics.set_capture_state("capturing", triggered=True)
        self.diagnostics.set_capture_state("cooldown")

        snapshot = self.diagnostics.snapshot()

        self.assertEqual(snapshot["capture_state"], "cooldown")
        self.assertIsNotNone(snapshot["last_capture_trigger"])
        self.assertTrue(
            any(event["type"] == "capture" for event in snapshot["events"])
        )

    def test_test_summary_measures_high_duration_and_gap(self):
        self.diagnostics.record_reading(0)
        self.diagnostics.start_test(60)
        self.diagnostics.record_reading(1, source="test")
        time.sleep(0.01)
        self.diagnostics.record_reading(0, source="test")
        time.sleep(0.01)
        self.diagnostics.record_reading(1, source="test")
        self.diagnostics.complete_test()

        summary = self.diagnostics.snapshot()["test"]["summary"]

        self.assertEqual(summary["motion_events"], 2)
        self.assertEqual(summary["transition_count"], 3)
        self.assertEqual(summary["sensor_state"], "HIGH")
        self.assertEqual(len(summary["high_durations_seconds"]), 2)
        self.assertIsNotNone(summary["shortest_gap_seconds"])


if __name__ == "__main__":
    unittest.main()
