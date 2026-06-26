#!/usr/bin/env python3
"""Unit tests for RAM Optimizer"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the project directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestFormatBytes(unittest.TestCase):
    """Test the _format_bytes static method"""

    def setUp(self):
        from ram_optimizer import RAMOptimizerDashboard

        self.dashboard = RAMOptimizerDashboard()

    def test_bytes(self):
        self.assertEqual(self.dashboard._format_bytes(0), "0 B")
        self.assertEqual(self.dashboard._format_bytes(500), "500 B")
        self.assertEqual(self.dashboard._format_bytes(1023), "1023 B")

    def test_kilobytes(self):
        self.assertEqual(self.dashboard._format_bytes(1024), "1.0 KB")
        self.assertEqual(self.dashboard._format_bytes(1536), "1.5 KB")
        self.assertEqual(self.dashboard._format_bytes(1024 * 512), "512.0 KB")

    def test_megabytes(self):
        self.assertEqual(self.dashboard._format_bytes(1024**2), "1.0 MB")
        self.assertEqual(self.dashboard._format_bytes(1024**2 * 2.5), "2.5 MB")
        self.assertEqual(self.dashboard._format_bytes(1024**2 * 100), "100.0 MB")

    def test_gigabytes(self):
        self.assertEqual(self.dashboard._format_bytes(1024**3), "1.0 GB")
        self.assertEqual(self.dashboard._format_bytes(1024**3 * 5), "5.0 GB")
        self.assertEqual(self.dashboard._format_bytes(1024**3 * 10.3), "10.3 GB")


class TestDashboardSettings(unittest.TestCase):
    """Test load_settings and save_settings for RAMOptimizerDashboard"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        from ram_optimizer import RAMOptimizerDashboard

        self.dashboard = RAMOptimizerDashboard()
        self.dashboard.config_path = self.config_path

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_settings_empty(self):
        """Should return empty dict when config doesn't exist"""
        settings = self.dashboard.load_settings()
        self.assertEqual(settings, {})

    def test_load_settings_valid_json(self):
        """Should return settings from valid JSON file"""
        test_data = {"auto_optimize": True, "auto_optimize_threshold": 90.0}
        with open(self.config_path, "w") as f:
            json.dump(test_data, f)

        settings = self.dashboard.load_settings()
        self.assertEqual(settings["auto_optimize"], True)
        self.assertEqual(settings["auto_optimize_threshold"], 90.0)

    def test_load_settings_corrupt_json(self):
        """Should return empty dict for corrupt JSON"""
        with open(self.config_path, "w") as f:
            f.write("this is not valid json {{{")

        settings = self.dashboard.load_settings()
        self.assertEqual(settings, {})

    def test_load_settings_permission_error(self):
        """Should return empty dict when file can't be read"""
        if os.geteuid() == 0:
            self.skipTest("Running as root, can't test permission errors")
        with open(self.config_path, "w") as f:
            json.dump({"test": True}, f)
        os.chmod(self.config_path, 0o000)
        try:
            settings = self.dashboard.load_settings()
            self.assertEqual(settings, {})
        finally:
            os.chmod(self.config_path, 0o644)

    def test_save_settings_without_gui(self):
        """save_settings should work even before GUI is created (hasattr guards)"""
        self.dashboard.save_settings()
        self.assertTrue(os.path.exists(self.config_path))
        with open(self.config_path) as f:
            saved = json.load(f)
        self.assertEqual(saved["auto_optimize"], False)
        self.assertEqual(saved["auto_optimize_threshold"], 85.0)
        self.assertEqual(saved["dark_mode"], True)

    @patch("tkinter.BooleanVar")
    @patch("tkinter.DoubleVar")
    def test_save_settings_with_gui_vars(self, mock_double, mock_bool):
        """save_settings should persist values from tkinter variables"""
        mock_bool.return_value.get.return_value = True
        mock_double.return_value.get.return_value = 90.0

        self.dashboard.auto_optimize = mock_bool.return_value
        self.dashboard.auto_optimize_threshold_var = mock_double.return_value
        self.dashboard.alert_enabled = mock_bool.return_value
        self.dashboard.alert_threshold_var = mock_double.return_value
        self.dashboard.battery_aware = mock_bool.return_value
        self.dashboard.dark_mode = mock_bool.return_value

        self.dashboard.save_settings()

        with open(self.config_path) as f:
            saved = json.load(f)
        self.assertTrue(saved["auto_optimize"])
        self.assertEqual(saved["auto_optimize_threshold"], 90.0)
        self.assertTrue(saved["alert_enabled"])
        self.assertEqual(saved["alert_threshold"], 90.0)
        self.assertTrue(saved["battery_aware"])
        self.assertTrue(saved["dark_mode"])


class TestMenuBarSettings(unittest.TestCase):
    """Test save_settings and toggle_auto_optimize for RAMOptimizerMenuBar"""

    @patch("rumps.notification")
    def setUp(self, mock_notification):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_mb_config.json")
        from ram_optimizer import RAMOptimizerDashboard, RAMOptimizerMenuBar

        # Create a MenuBar without actually running it
        self.menu_bar = object.__new__(RAMOptimizerMenuBar)
        self.menu_bar.config_path = self.config_path
        self.menu_bar.dashboard = RAMOptimizerDashboard()
        self.menu_bar.dashboard.config_path = self.config_path
        self.menu_bar.auto_optimize_enabled = False
        self.menu_bar.auto_optimize_threshold = 85.0
        self.menu_bar.alert_enabled = False
        self.menu_bar.alert_threshold = 80.0
        self.menu_bar.battery_aware = True
        self.menu_bar.schedule_enabled = False
        self.menu_bar.schedule_interval_minutes = 30
        self.mock_notification = mock_notification

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_settings_without_dashboard_opened(self):
        """save_settings should work when dashboard hasn't been opened (no dark_mode attr)"""
        if hasattr(self.menu_bar.dashboard, "dark_mode"):
            delattr(self.menu_bar.dashboard, "dark_mode")
        self.menu_bar.save_settings()

        with open(self.config_path) as f:
            saved = json.load(f)
        self.assertFalse(saved["auto_optimize"])
        self.assertTrue(saved["battery_aware"])
        self.assertTrue(saved["dark_mode"])  # Default True

    def test_save_settings_with_dashboard_dark_mode(self):
        """save_settings should read dark_mode from dashboard when available"""
        self.menu_bar.dashboard.dark_mode = MagicMock()
        self.menu_bar.dashboard.dark_mode.get.return_value = False
        self.menu_bar.save_settings()

        with open(self.config_path) as f:
            saved = json.load(f)
        self.assertFalse(saved["dark_mode"])

    @patch("rumps.notification")
    def test_toggle_auto_optimize_no_dashboard(self, mock_notify):
        """toggle_auto_optimize should not crash when dashboard hasn't been opened"""
        if hasattr(self.menu_bar.dashboard, "auto_optimize"):
            delattr(self.menu_bar.dashboard, "auto_optimize")

        sender = MagicMock()
        self.menu_bar.toggle_auto_optimize(sender)

        self.assertTrue(self.menu_bar.auto_optimize_enabled)
        # Verify settings were saved
        with open(self.config_path) as f:
            saved = json.load(f)
        self.assertTrue(saved["auto_optimize"])

    @patch("tkinter.BooleanVar")
    @patch("rumps.notification")
    def test_toggle_auto_optimize_with_dashboard_opened(self, mock_notify, mock_bool):
        """toggle_auto_optimize should sync to dashboard when it's open"""
        mock_var = mock_bool.return_value
        self.menu_bar.dashboard.auto_optimize = mock_var

        sender = MagicMock()
        self.menu_bar.toggle_auto_optimize(sender)

        self.assertTrue(self.menu_bar.auto_optimize_enabled)
        mock_var.set.assert_called_once_with(True)


class TestLogAction(unittest.TestCase):
    """Test the log_action static method"""

    @patch("psutil.virtual_memory")
    def test_log_action_writes_entry(self, mock_mem):
        """log_action should write a formatted log entry"""
        from ram_optimizer import RAMOptimizerDashboard

        mock_mem.return_value.percent = 45.2

        temp_dir = tempfile.mkdtemp()
        log_path = os.path.join(temp_dir, "ram_optimizer.log")
        try:
            with patch("ram_optimizer.os.path.expanduser", return_value=log_path):
                RAMOptimizerDashboard.log_action("Test Action", "Test Details")

            self.assertTrue(os.path.exists(log_path))
            with open(log_path) as f:
                content = f.read()
            self.assertIn("Test Action", content)
            self.assertIn("Test Details", content)
        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


class TestMemoryHistory(unittest.TestCase):
    """Test deque-based memory history functionality"""

    def setUp(self):
        from ram_optimizer import RAMOptimizerDashboard

        self.dashboard = RAMOptimizerDashboard()

    def test_memory_history_maxlen(self):
        """memory_history should keep at most 60 entries"""
        for i in range(100):
            self.dashboard.memory_history.append(i)
        self.assertEqual(len(self.dashboard.memory_history), 60)
        self.assertEqual(self.dashboard.memory_history[0], 40)

    def test_timestamps_maxlen(self):
        """timestamps should keep at most 60 entries"""
        for i in range(100):
            self.dashboard.timestamps.append(f"time_{i}")
        self.assertEqual(len(self.dashboard.timestamps), 60)
        self.assertEqual(self.dashboard.timestamps[0], "time_40")


class TestUpdateThreshold(unittest.TestCase):
    """Test the update_threshold method"""

    @patch("tkinter.DoubleVar")
    def test_update_threshold_syncs_value(self, mock_double):
        """update_threshold should sync tk variable to instance attribute"""
        from ram_optimizer import RAMOptimizerDashboard

        dashboard = RAMOptimizerDashboard()
        mock_var = mock_double.return_value
        mock_var.get.return_value = 75.0
        dashboard.auto_optimize_threshold_var = mock_var
        dashboard.auto_optimize_threshold = 85.0

        temp_dir = tempfile.mkdtemp()
        dashboard.config_path = os.path.join(temp_dir, "test_config.json")
        try:
            dashboard.update_threshold()
            self.assertEqual(dashboard.auto_optimize_threshold, 75.0)
        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


class TestCacheClearCommands(unittest.TestCase):
    """Test that cache clearing commands use resolved absolute paths"""

    def setUp(self):
        from ram_optimizer import RAMOptimizerDashboard

        self.dashboard = RAMOptimizerDashboard()

    def test_get_user_cache_path_is_absolute(self):
        """_get_user_cache_path should return an absolute path to user caches"""
        from ram_optimizer import RAMOptimizerDashboard

        path = RAMOptimizerDashboard._get_user_cache_path()
        home = os.path.expanduser("~")
        self.assertTrue(os.path.isabs(path))
        self.assertIn(home, path)
        self.assertIn("Library/Caches", path)
        self.assertNotIn("~", path)

    @patch("subprocess.run")
    @patch("tkinter.messagebox.showinfo")
    def test_clear_caches_uses_absolute_paths(self, mock_msg, mock_run):
        """clear_caches should use _get_user_cache_path helper for home directory paths"""
        from ram_optimizer import RAMOptimizerDashboard

        expected_path = f"sudo rm -rf {RAMOptimizerDashboard._get_user_cache_path()}/*"

        self.dashboard.root = MagicMock()
        self.dashboard.status_label = MagicMock()

        self.dashboard.clear_caches()

        all_calls = [str(call) for call in mock_run.call_args_list]
        found = any(expected_path in call for call in all_calls)
        self.assertTrue(found, f"Expected cache command to use _get_user_cache_path, got: {all_calls}")

    @patch("subprocess.run")
    @patch("tkinter.messagebox.showinfo")
    def test_full_optimization_uses_absolute_paths(self, mock_msg, mock_run):
        """full_optimization should use _get_user_cache_path helper"""
        from ram_optimizer import RAMOptimizerDashboard

        expected_path = f"sudo rm -rf {RAMOptimizerDashboard._get_user_cache_path()}/*"

        self.dashboard.root = MagicMock()
        self.dashboard.status_label = MagicMock()

        self.dashboard.full_optimization()

        all_calls = [str(call) for call in mock_run.call_args_list]
        found = any(expected_path in call for call in all_calls)
        self.assertTrue(found, f"Expected cache command to use _get_user_cache_path, got: {all_calls}")


if __name__ == "__main__":
    unittest.main()
