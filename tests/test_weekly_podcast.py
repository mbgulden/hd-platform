import os
import sys
import unittest
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the scripts directory to the path so we can import weekly-podcast
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import modules. Note: we need to import weekly-podcast.py which has a hyphen.
# We will use importlib to import it since it has a hyphen in the filename.
import importlib.util

def load_weekly_podcast_module():
    scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
    module_path = scripts_dir / "weekly-podcast.py"
    spec = importlib.util.spec_from_file_location("weekly_podcast", str(module_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

wp = load_weekly_podcast_module()

class TestWeeklyPodcast(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.old_podcasts_dir = wp.PODCASTS_DIR
        wp.PODCASTS_DIR = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        wp.PODCASTS_DIR = self.old_podcasts_dir

    def test_load_gates_data(self):
        gates = wp.load_gates_data()
        self.assertIsInstance(gates, dict)
        if gates:
            # Check a standard gate exists (e.g., Gate 1)
            self.assertIn("1", gates)
            self.assertIn("name", gates["1"])
            self.assertIn("snippet", gates["1"])

    def test_get_fallback_transit_data(self):
        # Test a few dates for deterministic sun gate calculation
        d1 = datetime(2026, 7, 7)
        data1 = wp.get_fallback_transit_data(d1)
        self.assertIn("sun_gate", data1)
        self.assertIsInstance(data1["sun_gate"], int)
        self.assertTrue(1 <= data1["sun_gate"] <= 64)

        d2 = datetime(2026, 1, 1)
        data2 = wp.get_fallback_transit_data(d2)
        self.assertIn("sun_gate", data2)

    @patch.object(wp, 'get_transit_data')
    def test_generate_script_format(self, mock_get_transit):
        mock_get_transit.side_effect = lambda dt: {
            datetime(2026, 7, 7): {"sun_gate": 53},
            datetime(2026, 7, 8): {"sun_gate": 62},
            datetime(2026, 7, 9): {"sun_gate": 56},
        }.get(datetime(dt.year, dt.month, dt.day), {"sun_gate": 56})

        gates_data = {
            "53": {"name": "Beginnings", "snippet": "Initiating cycles."},
            "62": {"name": "Detail", "snippet": "Factual clarity."},
            "56": {"name": "Stimulation", "snippet": "Storytelling weather."}
        }
        start_date = datetime(2026, 7, 7)
        script = wp.generate_script(start_date, gates_data)
        
        # Verify markdown structure
        self.assertTrue(script.startswith("# Human Design Weekly: July 07, 2026"))
        self.assertIn("**Episode Date:** 2026-07-07", script)
        self.assertIn("## Intro", script)
        self.assertIn("## Transit Highlights", script)
        self.assertIn("### Beginnings (Gate 53)", script)
        self.assertIn("### Detail (Gate 62)", script)
        self.assertIn("### Stimulation (Gate 56)", script)
        self.assertIn("## Practical Experiment", script)
        self.assertIn("## Outro", script)
        self.assertIn("## CTA", script)
        self.assertIn("humandesignengine.com", script)

    @patch.dict('os.environ', {'PODCASTS_DIR': '/tmp/custom_podcasts_env_dir'})
    def test_podcasts_dir_env_var(self):
        # Re-import to trigger environment variable lookup
        wp_temp = load_weekly_podcast_module()
        self.assertEqual(wp_temp.PODCASTS_DIR, '/tmp/custom_podcasts_env_dir')

    @patch('subprocess.run')
    def test_rss_regeneration_triggered(self, mock_run):
        # Mock subprocess.run for RSS regeneration
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")
        
        # Run main with --rss flag
        # Mock sys.argv
        test_args = ["weekly-podcast.py", "--date", "2026-07-07", "--rss"]
        with patch.object(sys, 'argv', test_args):
            wp.main()
            
        # Check that generate_rss_feed.py was called via subprocess.run
        mock_run.assert_called()
        args, kwargs = mock_run.call_args
        self.assertIn("generate_rss_feed.py", str(args[0]))
        self.assertIn("--write", args[0])

if __name__ == '__main__':
    unittest.main()
