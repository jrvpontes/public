#!/usr/bin/env python3

import json
import subprocess
import sys
import time

import pywinctl as pwc

WORKSPACE_FILE = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "/wks/paimon/wks-workspace.json"
)


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

    end_time = time.time() + timeout

    while time.time() < end_time:

        try:

            for window in pwc.getAllWindows():

                try:

                    handle = hex(window.getHandle())

                    output = subprocess.check_output(
                        [
                            "xprop",
                            "-id",
                            handle,
                            "WM_CLASS"
                        ],
                        stderr=subprocess.DEVNULL,
                        text=True
                    )

                    if "=" not in output:
                        continue

                    current = output.split(
                        "=",
                        1
                    )[1].strip()

                    found = {
                        x.strip().strip('"').lower()
                        for x in current.split(",")
                    }

                    if expected.intersection(found):
                        return window

                except Exception:
                    pass

        except Exception:
            pass

        time.sleep(1)

    return None


def restore_window(window, spec):

    try:

        if spec.get("minimized"):
            try:
                window.minimize()
            except Exception:
                pass
            return

        try:
            window.restore()
        except Exception:
            pass

        try:
            window.resizeTo(
                spec["width"],
                spec["height"]
            )
        except Exception:
            pass

        try:
            window.moveTo(
                spec["left"],
                spec["top"]
            )
        except Exception:
            pass

        if spec.get("maximized"):

            try:
                window.maximize()
            except Exception:
                pass

        if spec.get("active"):

            try:
                window.activate()
            except Exception:
                pass

    except Exception as e:

        print(
            f"restore failed "
            f"[{spec.get('title')}] -> {e}"
        )


def main():

    with open(
        WORKSPACE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    windows = data.get("windows", [])

    print(f"loaded windows: {len(windows)}")

    #
    # ABRE CADA APLICAÇÃO APENAS UMA VEZ
    #

    started_commands = set()

    for spec in windows:

        cmd = spec.get("launch_command")

        if not cmd:
            continue

        if cmd in started_commands:
            continue

        if start_window(spec):
            started_commands.add(cmd)

    #
    # TEMPO PARA AS APLICAÇÕES SUBIREM
    #

    print("waiting applications...")

    time.sleep(10)

    #
    # RESTAURA TODAS AS JANELAS
    #

    restored = 0

    for spec in windows:

        wm_class = spec.get("wm_class")

        if not wm_class:
            continue

        window = find_window_by_wm_class(
            wm_class,
            timeout=20
        )

        if not window:

            print(
                f"window not found: "
                f"{spec.get('title')}"
            )

            continue

        restore_window(
            window,
            spec
        )

        restored += 1

        print(
            f"restored: "
            f"{spec.get('title')}"
        )

        time.sleep(0.5)

    print()
    print(f"restored windows: {restored}")


if __name__ == "__main__":
    main()