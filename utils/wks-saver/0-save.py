#!/usr/bin/env python3

import json
import os
import subprocess

import pywinctl as pwc

OUTPUT_FILE = "/wks/paimon/wks-workspace.json"

IGNORE_CLASSES = {
    "nemo-desktop",
    "desktop",
    "cinnamon",
    "cinnamon-settings-daemon",
    "xfce4-panel",
    "plasmashell",
    "gnome-shell",
}


def run(cmd):
    try:
        return subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        return ""


def is_internal_process(cmdline):
    return False


def get_pid(window_id):
    out = run(["xprop", "-id", window_id, "_NET_WM_PID"])

    if "=" not in out:
        return None

    try:
        return int(out.split("=")[1].strip())
    except Exception:
        return None


def get_wm_class(window_id):
    out = run(["xprop", "-id", window_id, "WM_CLASS"])

    if "=" not in out:
        return []

    try:
        value = out.split("=", 1)[1].strip()

        classes = []

        for item in value.split(","):
            item = item.strip().strip('"')
            if item:
                classes.append(item)

        return classes

    except Exception:
        return []


def get_process_cmdline(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            data = f.read()

        return data.replace(b"\x00", b" ").decode().strip()

    except Exception:
        return ""


def get_process_exe(pid):
    try:
        return os.readlink(f"/proc/{pid}/exe")
    except Exception:
        return ""


def get_launch_command(exe, cmdline):
    if not exe:
        return cmdline

    if "--gapplication-service" in cmdline:
        return exe

    return cmdline if cmdline else exe


def get_active_window():
    return run(["xdotool", "getactivewindow"])


def get_monitor_name(x, y):
    try:
        output = run(["xrandr", "--listmonitors"])

        lines = output.splitlines()[1:]

        for line in lines:

            parts = line.split()

            if len(parts) < 3:
                continue

            geometry = parts[2]

            if "+" not in geometry:
                continue

            size_part, pos_part = geometry.split("+", 1)

            width = int(size_part.split("/")[0].split("x")[0])
            height = int(size_part.split("/")[1].split("+")[0])

            pos = geometry.split("+")
            mon_x = int(pos[1])
            mon_y = int(pos[2])

            if (
                x >= mon_x
                and x < mon_x + width
                and y >= mon_y
                and y < mon_y + height
            ):
                return parts[-1]

    except Exception:
        pass

    return ""


def is_maximized(window):
    try:
        return window.isMaximized
    except Exception:
        return False


def is_minimized(window):
    try:
        return window.isMinimized
    except Exception:
        return False


def should_ignore_window(title, wm_class):
    if not wm_class:
        return False

    for item in wm_class:

        value = item.lower()

        if value in IGNORE_CLASSES:
            return True

    return False


def save_workspace():

    active_window = get_active_window()

    windows = []

    for window in pwc.getAllWindows():

        try:

            title = window.title

            if not title:
                continue

            window_id = hex(window.getHandle())

            pid = get_pid(window_id)

            if not pid:
                continue

            wm_class = get_wm_class(window_id)

            if should_ignore_window(title, wm_class):
                continue

            process_cmdline = get_process_cmdline(pid)

            if is_internal_process(process_cmdline):
                continue

            process_exe = get_process_exe(pid)

            launch_command = get_launch_command(
                process_exe,
                process_cmdline
            )

            left = window.left
            top = window.top
            width = window.width
            height = window.height

            monitor = get_monitor_name(left, top)

            windows.append(
                {
                    "window_id": window_id,
                    "pid": pid,
                    "wm_class": wm_class,
                    "process_cmdline": process_cmdline,
                    "process_exe": process_exe,
                    "launch_command": launch_command,
                    "title": title,
                    "monitor": monitor,
                    "left": left,
                    "top": top,
                    "width": width,
                    "height": height,
                    "active": window_id == active_window,
                    "maximized": is_maximized(window),
                    "minimized": is_minimized(window),
                }
            )

        except Exception as e:

            print(f"skip window -> {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "windows": windows
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"saved: {OUTPUT_FILE}")
    print(f"windows: {len(windows)}")


if __name__ == "__main__":
    save_workspace()