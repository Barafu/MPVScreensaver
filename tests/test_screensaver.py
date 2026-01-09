#!/usr/bin/env python3

"""
Tests for MPVScreensaver
"""

import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent))
import screensaver


class TestAdjustMpvConf:
    """Test adjust_mpv_conf function."""

    def test_adjust_mpv_conf_zero_videos(self):
        """When video_count != 1, MPV_CONF should stay unchanged."""
        result = screensaver.adjust_mpv_conf(0)
        # loop-playlist=inf should remain
        assert "loop-playlist=inf" in result
        assert "loop=inf" not in result
        # Ensure original MPV_CONF is returned (except possible whitespace)
        # Since MPV_CONF is a constant, we can compare
        expected = screensaver.MPV_CONF
        assert result == expected

    def test_adjust_mpv_conf_one_video(self):
        """When video_count == 1, loop-playlist should be replaced with loop."""
        result = screensaver.adjust_mpv_conf(1)
        # loop-playlist=inf should be replaced
        assert "loop-playlist=inf" not in result
        assert "loop=inf" in result
        # Ensure other parts unchanged
        assert "image-display-duration=7" in result

    def test_adjust_mpv_conf_many_videos(self):
        """When video_count > 1, loop-playlist should stay."""
        result = screensaver.adjust_mpv_conf(5)
        assert "loop-playlist=inf" in result
        assert "loop=inf" not in result


class TestParseArguments:
    """Test parse_arguments function."""

    def setup_method(self):
        """Reset mock counters."""
        self.mock_notify = patch("screensaver.send_notification").start()
        self.mock_exists = patch("os.path.exists").start()

    def teardown_method(self):
        """Stop patches."""
        patch.stopall()

    def test_parse_arguments_no_missing_files(self):
        """All files exist, no notifications sent."""
        # Simulate existing files
        self.mock_exists.side_effect = lambda x: True
        with patch("sys.argv", ["screensaver.py", "video1.mp4", "video2.mp4"]):
            args, video_list = screensaver.parse_arguments()
        assert args.videos == ["video1.mp4", "video2.mp4"]
        assert video_list == ["video1.mp4", "video2.mp4"]
        self.mock_notify.assert_not_called()

    def test_parse_arguments_missing_files_limit_notifications(self):
        """
        Missing files trigger notifications, but at most 3 notifications.
        """
        # Create a temporary directory with some files and some missing
        with tempfile.TemporaryDirectory() as tmpdir:
            existing = []
            missing = []
            for i in range(5):
                if i < 2:
                    # create real file
                    p = Path(tmpdir) / f"video{i}.mp4"
                    p.touch()
                    existing.append(str(p))
                else:
                    missing.append(str(Path(tmpdir) / f"video{i}.mp4"))
            all_files = existing + missing

            # Mock os.path.exists to return True only for existing files
            def exists_mock(path):
                return path in existing

            self.mock_exists.side_effect = exists_mock

            # Parse arguments with these files
            with patch("sys.argv", ["screensaver.py"] + all_files):
                args, video_list = screensaver.parse_arguments()

            # Only existing files should be in video_list
            assert set(video_list) == set(existing)
            # Notifications should have been sent for missing files, but max 3
            # Because we have 3 missing files (indices 2,3,4) -> 3 notifications
            # Let's verify that send_notification was called exactly 3 times
            assert self.mock_notify.call_count == 3
            # Verify each call contains appropriate message
            for i, call_args in enumerate(self.mock_notify.call_args_list):
                args, kwargs = call_args
                assert args[0].startswith("File not found:")
                assert kwargs.get("urgent") == False

    def test_parse_arguments_default_video_path(self):
        """When no arguments given, VIDEO_PATH is used."""
        # Mock VIDEO_PATH constant? Actually it's defined as ["/dev/null"]
        # We'll just check that video_list equals VIDEO_PATH if no args and /dev/null exists
        # /dev/null exists on Unix, but we can mock os.path.exists to return True
        self.mock_exists.return_value = True
        with patch("sys.argv", ["screensaver.py"]):
            args, video_list = screensaver.parse_arguments()
        assert args.videos == []
        assert video_list == screensaver.VIDEO_PATH
        self.mock_notify.assert_not_called()

    def test_parse_arguments_dry_run_flag(self):
        """dry-run flag should be captured."""
        self.mock_exists.return_value = True
        with patch("sys.argv", ["screensaver.py", "--dry-run", "video.mp4"]):
            args, video_list = screensaver.parse_arguments()
        assert args.dry_run is True
        assert video_list == ["video.mp4"]


if __name__ == "__main__":
    pytest.main([__file__])
