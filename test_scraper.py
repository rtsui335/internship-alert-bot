import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scraper


SAMPLE_TABLE = """
<table>
  <tr><th>Company</th><th>Role</th><th>Location</th><th>Application</th></tr>
  <tr>
    <td><strong>Acme</strong></td><td>Software Engineer Intern</td>
    <td>New York<br>Remote</td><td><a href="https://example.com/one">Apply</a></td>
  </tr>
  <tr>
    <td>\u21b3</td><td>Data Scientist Intern</td><td>Boston</td>
    <td><a href="https://example.com/two">Apply</a></td>
  </tr>
</table>
"""


class ScraperTests(unittest.TestCase):
    def test_parse_jobs_inherits_company_and_formats_locations(self):
        jobs = scraper.parse_jobs(SAMPLE_TABLE)

        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["location"], "New York, Remote")
        self.assertEqual(jobs[1]["company"], "Acme")
        self.assertEqual(jobs[1]["link"], "https://example.com/two")

    def test_parse_jobs_skips_orphaned_continuation(self):
        html = '<table><tr><td>\u21b3</td><td>Software Engineer</td><td>Remote</td>' \
               '<td><a href="https://example.com/job">Apply</a></td></tr></table>'
        self.assertEqual(scraper.parse_jobs(html), [])

    def test_load_seen_rejects_invalid_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            seen_file = Path(directory) / "seen.json"
            seen_file.write_text(json.dumps({"unexpected": "object"}), encoding="utf-8")
            with patch.object(scraper, "SEEN_FILE", seen_file):
                with self.assertRaisesRegex(RuntimeError, "JSON list"):
                    scraper.load_seen()

    def test_save_seen_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            seen_file = Path(directory) / "seen.json"
            with patch.object(scraper, "SEEN_FILE", seen_file):
                scraper.save_seen({"second", "first"})
                self.assertEqual(scraper.load_seen(), {"first", "second"})


if __name__ == "__main__":
    unittest.main()
