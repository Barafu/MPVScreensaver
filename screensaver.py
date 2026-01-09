#!/usr/bin/env python3

"""
This script will launch MPV with configured parameters
"""

# ====================================================
# CONFIG SECTION
# Feel free to edit to fit your needs
# ====================================================

# What screens to show video on, for example [0] or [0,1]
DISPLAYS = [0]

# Here you can write video files to play and not have to provide them as CLI arguments.
VIDEO_PATH = []

# These are mpv playback configs. See: https://mpv.io/manual/stable/#options
# ---
# hwdec - enable hardware video decoding, which reduces power consumption, but may bring glitches.
# supported values are no, auto, nvdec (for nvidia), vaapi, vulkan.
# More info here: https://mpv.io/manual/stable/#options-hwdec
# ---
# Replace ao=null with volume=100 to enable sound.
MPV_CONF = """
hwdec=no
loop-playlist=inf
image-display-duration=7
ao=null
fullscreen=yes
ontop
osc=no
osd-level=0
vo=gpu-next
input-default-bindings=no
cursor-autohide=always
title="MPVScreensaver"
stop-screensaver=no
"""

# This teaches MPV to quit on any button pressed, but not on mouse move.
INPUT_CONF = """
MOUSE_MOVE ignore
MOUSE_ENTER ignore
MOUSE_LEAVE ignore
MBTN_LEFT quit
MBTN_RIGHT quit
UNMAPPED keybind UNMAPPED quit
"""

# ====================================================
# CODE SECTION
# No user serviceable components inside
# ====================================================

import tempfile
import subprocess
import os
import argparse
import shutil
import time
from pathlib import Path


def adjust_mpv_conf(video_count: int) -> str:
    """
    Return MPV_CONF with loop-playlist replaced by loop if only one video.
    """
    if video_count == 1:
        return MPV_CONF.replace("loop-playlist=inf", "loop=inf")
    return MPV_CONF


def send_notification(message: str, urgent: bool) -> None:
    """
    Send a desktop notification using notify-send.

    Args:
        message: Notification text
        urgent: If True, send as critical urgency; otherwise normal.
    """
    app_name = "MPVScreensaver"
    urgency = "critical" if urgent else "normal"
    subprocess.run(["notify-send", "-a", app_name, "-u", urgency, message])


def parse_arguments():
    """
    Parse command line arguments and determine video list.
    Returns a tuple (args, video_list).
    """
    parser = argparse.ArgumentParser(description="Launch MPV screensaver")
    parser.add_argument("videos", nargs="*", help="Video files to play (optional)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print commands without executing"
    )
    args = parser.parse_args()

    if args.videos:
        video_list = args.videos
    else:
        video_list = VIDEO_PATH

    # Filter out missing files and notify user (max 3 notifications)
    valid_videos = []
    notifications_sent = 0
    for file in video_list:
        if os.path.exists(file):
            valid_videos.append(file)
        else:
            if notifications_sent < 3:
                send_notification(f"File not found: {file}", urgent=False)
                notifications_sent += 1
            # do not add missing file

    return args, valid_videos


def create_temp_config_dir(video_count: int) -> Path:
    """
    Create a temporary directory containing mpv.conf and input.conf.
    Returns the Path to the directory.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="mpvconfig_"))
    adjusted_conf = adjust_mpv_conf(video_count)
    (temp_dir / "mpv.conf").write_text(adjusted_conf)
    (temp_dir / "input.conf").write_text(INPUT_CONF)
    return temp_dir


def main():
    args, video_list = parse_arguments()

    if not video_list:
        send_notification("No videos to play", urgent=True)
        print("No videos to play")
        return

    # create temporary config directory
    config_dir = create_temp_config_dir(len(video_list))
    print(f"Temporary config directory: {config_dir}")

    # launch mpv for each display
    processes = []
    for i, display in enumerate(DISPLAYS):
        cmd = [
            "mpv",
            f"--config-dir={config_dir}",
            f"--fs-screen={display}",
        ] + video_list
        if args.dry_run:
            print(
                f"Would launch mpv for display {display} with {len(video_list)} videos"
            )
            print("Command:", " ".join(cmd))
        else:
            proc = subprocess.Popen(cmd)
            processes.append(proc)
            print(f"Launched mpv for display {display} with {len(video_list)} videos")

    # wait for any process to finish; when one finishes, stop all others
    if processes:
        try:
            while True:
                for proc in processes:
                    if proc.poll() is not None:
                        raise StopIteration
                time.sleep(0.1)
        except StopIteration:
            pass
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            # terminate all remaining processes
            for proc in processes:
                if proc.poll() is None:
                    proc.terminate()
            # wait for termination
            for proc in processes:
                proc.wait()

    # delete temporary config directory
    shutil.rmtree(config_dir)


if __name__ == "__main__":
    main()
