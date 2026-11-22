import json
from pathlib import Path
import unittest

from project import analyze


def example():
    return json.loads(Path(__file__).with_name("example.json").read_text(encoding="utf-8"))


class ProjectTests(unittest.TestCase):
    def test_real_timing(self):
        report = analyze(example())
        self.assertEqual(report["metrics"]["First gameplay (s)"], 7)
        self.assertEqual(report["metrics"]["Opening gameplay (s)"], 3)
        self.assertAlmostEqual(report["metrics"]["Gameplay share (%)"], 58.3)
        self.assertEqual(len(report["rows"]), 6)

    def test_unlogged_windows_stay_empty(self):
        report = analyze({"duration_seconds": 12, "shots": []})
        self.assertEqual(report["metrics"]["First gameplay (s)"], "Absent")
        self.assertTrue(all(r["Length (s)"] == 0 for r in report["rows"]))

    def test_shorter_than_one_second_samples(self):
        data = {"duration_seconds": 3, "shots": [{"start": 0, "end": 3,
                "type": "gameplay", "description": "Move"}]}
        self.assertTrue(all(r["Length (s)"] == .5 for r in analyze(data)["rows"]))

    def test_rejects_overlaps(self):
        data = example()
        data["shots"][1]["start"] = 1
        with self.assertRaises(ValueError):
            analyze(data)


if __name__ == "__main__":
    unittest.main()
