#!/usr/bin/env python3

import json
import subprocess
import sys
import time
import pywinctl as pwc

WORKSPACE_FILE = sys.argv[1] if len(sys.argv) > 1 else "/wks/paimon/workspace.json"


def start_window(spec):

    cmd = spec.get("launch_command")

    if not cmd:
        return False

    try:

        print(f"starting: {cmd}")

        subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return True

    except Exception as e:

        print(f"start failed [{cmd}] -> {e}")
        return False


def find_window_by_wm_class(wm_class, timeout=60):

    if not wm_class:
        return None

    expected = {
        x.lower()
        for x in wm_class
        if x
    }

    end = time.time() + timeout

    while time.time() < end:

        for win in pwc.getAllWindows():

            try:

                title = str(win.title).strip()

                if not title:
                    continue

                for attr in (
                    "_hWnd",
                    "_hwnd",
                    "hWnd",
                    "hwnd"
                ):

                    if not hasattr(win, attr):
                        continue

                    try:

                        value = getattr(win, attr)

                        if isinstance(value, int):
                            window_id = hex(value).lower()
                        else:
                            window_id = str(value).lower()

                        output = subprocess.check_output(
                            [
                                "xprop",
                                "-id",
                                window_id,
                                "WM_CLASS"
                            ],
                            text=True,
                            stderr=subprocess.DEVNULL
                        )

                        if "=" not in output:
                            continue

                        current = output.split("=", 1)[1]

                        current = {
                            x.strip().strip('"').lower()
                            for x in current.split(",")
                        }

                        if current & expected:
                            return win

                    except Exception:
                        pass

            except Exception:
                pass

        time.sleep(1)

    return None


def restore_window(win, spec):

    try:

        if spec.get("minimized"):
            win.minimize()
            return

        try:
            win.restore()
        except Exception:
            pass

        win.moveTo(
            spec["left"],
            spec["top"]
        )

        win.resizeTo(
            spec["width"],
            spec["height"]
        )

        if spec.get("maximized"):
            win.maximize()

    except Exception as e:

        print(f"restore failed [{spec['title']}] -> {e}")


with open(WORKSPACE_FILE, encoding="utf-8") as f:
    workspace = json.load(f)

windows = workspace["windows"]

started = []

#
# fase 1
# iniciar aplicações
#

for spec in windows:

    if start_window(spec):
        started.append(spec)

    time.sleep(0.5)

#
# fase 2
# localizar por WM_CLASS
#

for spec in started:

    wm_class = spec.get("wm_class")

    print(
        f"waiting window: "
        f"{wm_class}"
    )

    win = find_window_by_wm_class(
        wm_class,
        timeout=30
    )

    if not win:

        print(
            f"window not found: "
            f"{wm_class}"
        )

        continue

    print(
        f"restoring: "
        f"{spec['title']}"
    )

    restore_window(
        win,
        spec
    )

#
# fase 3
# restaurar foco
#

for spec in windows:

    if not spec.get("active"):
        continue

    win = find_window_by_wm_class(
        spec.get("wm_class"),
        timeout=5
    )

    if not win:
        continue

    try:
        win.activate()
    except Exception:
        pass

    break

print("workspace restored")