#!/usr/bin/env python3

import json
import subprocess
import pywinctl as pwc

OUTPUT_FILE = "/wks/paimon/workspace.json"


def run(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def get_monitors():
    monitors = []

    output = run(["xrandr", "--query"])

    for line in output.splitlines():

        if " connected " not in line:
            continue

        parts = line.split()

        name = parts[0]

        geom = None
        for token in parts:
            if "+" in token and "x" in token:
                geom = token
                break

        if not geom:
            continue

        size, pos = geom.split("+", 1)

        width, height = map(int, size.split("x"))
        x, y = map(int, pos.split("+"))

        monitors.append({
            "name": name,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        })

    return monitors


def find_monitor(monitors, left, top, width, height):

    center_x = left + width // 2
    center_y = top + height // 2

    for m in monitors:

        if (
            center_x >= m["x"]
            and center_x < (m["x"] + m["width"])
            and center_y >= m["y"]
            and center_y < (m["y"] + m["height"])
        ):
            return m["name"]

    return None


def get_wmctrl_data():

    result = {}

    output = run(["wmctrl", "-lp"])

    for line in output.splitlines():

        parts = line.split(None, 4)

        if len(parts) < 5:
            continue

        wid = parts[0].lower()
        pid = parts[2]

        result[wid] = {
            "window_id": wid,
            "pid": int(pid)
        }

    return result


def get_wm_class(window_id):

    try:

        output = run([
            "xprop",
            "-id",
            window_id,
            "WM_CLASS"
        ])

        if "=" not in output:
            return None

        value = output.split("=", 1)[1].strip()

        classes = [
            x.strip().strip('"')
            for x in value.split(",")
        ]

        return classes

    except Exception:
        return None


def get_pid(win):

    for attr in ("pid", "_pid"):

        if hasattr(win, attr):
            try:
                return int(getattr(win, attr))
            except Exception:
                pass

    for method in ("getPID",):

        if hasattr(win, method):
            try:
                return int(getattr(win, method)())
            except Exception:
                pass

    return None


def get_window_id(win):

    for attr in (
        "_hWnd",
        "_hwnd",
        "hWnd",
        "hwnd"
    ):

        if hasattr(win, attr):
            try:
                value = getattr(win, attr)

                if isinstance(value, int):
                    return hex(value).lower()

                return str(value).lower()

            except Exception:
                pass

    return None


def get_process_cmdline(pid):

    if not pid:
        return None

    output = run([
        "ps",
        "-p",
        str(pid),
        "-o",
        "args="
    ])

    output = output.strip()

    return output if output else None


def get_process_exe(pid):

    if not pid:
        return None

    output = run([
        "readlink",
        "-f",
        f"/proc/{pid}/exe"
    ])

    output = output.strip()

    return output if output else None


def is_active(win):

    try:
        return bool(win.isActive)
    except Exception:
        return False


def is_maximized(win):

    try:
        return bool(win.isMaximized)
    except Exception:
        return False


def is_minimized(win):

    try:
        return bool(win.isMinimized)
    except Exception:
        return False


monitors = get_monitors()
wmctrl_data = get_wmctrl_data()

windows = []

for win in pwc.getAllWindows():

    try:

        title = str(win.title).strip()

        if not title:
            continue

        left = int(win.left)
        top = int(win.top)
        width = int(win.width)
        height = int(win.height)

        pid = get_pid(win)
        window_id = get_window_id(win)

        if window_id and window_id in wmctrl_data:
            pid = wmctrl_data[window_id]["pid"]

        windows.append({

            "window_id": window_id,

            "pid": pid,

            "wm_class": get_wm_class(window_id)
            if window_id else None,

            "process_cmdline": get_process_cmdline(pid),

            "process_exe": get_process_exe(pid),

            "title": title,

            "monitor": find_monitor(
                monitors,
                left,
                top,
                width,
                height
            ),

            "left": left,
            "top": top,
            "width": width,
            "height": height,

            "active": is_active(win),
            "maximized": is_maximized(win),
            "minimized": is_minimized(win)

        })

    except Exception as e:
        print(f"ignored: {e}")

workspace = {
    "monitors": monitors,
    "windows": windows
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        workspace,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"workspace saved: {OUTPUT_FILE}")
print(f"monitors: {len(monitors)}")
print(f"windows: {len(windows)}")