import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools/fex/plan.py"
PLAN = runpy.run_path(str(SCRIPT))


class FexPlanTest(unittest.TestCase):
    def test_the_build_number_grows_across_releases(self):
        self.assertEqual("2610-r7", PLAN["next_version"]("2610-r6", "FEX-2610"))
        self.assertEqual("2611-r7", PLAN["next_version"]("2610-r6", "FEX-2611"))

    def test_a_first_build_is_r1(self):
        self.assertEqual("2610-r1", PLAN["next_version"](None, "FEX-2610"))

    def test_only_release_tags_are_built(self):
        with self.assertRaises(ValueError):
            PLAN["next_version"]("2610-r6", "main")

    def test_a_new_release_or_source_commit_asks_for_a_build(self):
        recorded = {"version": "2610-r7", "fex": "FEX-2610", "source": "a" * 40}
        self.assertEqual([], PLAN["reasons"](recorded, "FEX-2610", "a" * 40))
        self.assertEqual(["FEX FEX-2610 -> FEX-2611"], PLAN["reasons"](recorded, "FEX-2611", "a" * 40))
        self.assertEqual(["tools/fex aaaaaaaaaaaa -> bbbbbbbbbbbb"], PLAN["reasons"](recorded, "FEX-2610", "b" * 40))

    def test_a_build_from_before_the_record_is_rebuilt(self):
        self.assertEqual(2, len(PLAN["reasons"]({"version": "2610-r6"}, "FEX-2610", "c" * 40)))

    def test_the_command_line(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fex.json"
            path.write_text(json.dumps({"version": "2610-r6", "fex": "FEX-2610", "source": "d" * 40}))
            self.assertEqual("2610-r7", subprocess.run([sys.executable, str(SCRIPT), "next-version", str(path), "FEX-2610"],
                                                       capture_output=True, text=True, check=True).stdout.strip())
            self.assertEqual("", subprocess.run([sys.executable, str(SCRIPT), "changed", str(path), "FEX-2610", "d" * 40],
                                                capture_output=True, text=True, check=True).stdout.strip())


if __name__ == "__main__":
    unittest.main()
