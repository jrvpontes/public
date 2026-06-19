#!/usr/bin/env python3

import json
import os
import subprocess
import time

WORKSPACE_FILE = "/wks/paimon/wks-workspace.json"


def run(cmd):
    try:
        return subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        return ""


def get_current_window_id():

    #
    # py close.py
    #  └─ bash
    #      └─ terminal
    #

    current_pid = os.getpid()

    pid = current_pid

    for _ in range(10):

        try:

            ppid = int(
                run(
                    [
                        "ps",
                        "-o",
                        "ppid=",
                        "-p",
                        str(pid)
                    ]
                )
            )

            if ppid <= 1:
                break

            pid = ppid

        except Exception:
            break

    output = run(["wmctrl", "-lp"])

    for line in output.splitlines():

        parts = line.split(None, 4)

        if len(parts) < 5:
            continue

        window_id = parts[0]
        window_pid = parts[2]

        if str(pid) == window_pid:
            return window_id

    return None


def get_existing_windows():

    result = set()

    output = run(["wmctrl", "-lp"])

    for line in output.splitlines():

        parts = line.split()

        if not parts:
            continue

        result.add(parts[0].lower())

    return result


def close_window(window_id):

    try:

        subprocess.run(
            ["wmctrl", "-ic", window_id],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return True

    except Exception:

        return False


def main():

    with open(
        WORKSPACE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    windows = data.get("windows", [])

    current_window = get_current_window_id()

    existing_windows = get_existing_windows()

    print()
    print("workspace close")
    print()

    if current_window:
        print(f"current window: {current_window}")
        print()

    closed = 0
    skipped = 0

    #
    # fecha de trás para frente
    #

    for spec in reversed(windows):

        window_id = spec.get("window_id")

        if not window_id:
            continue

        window_id = window_id.lower()

        if window_id not in existing_windows:
            continue

        if current_window and window_id == current_window.lower():

            print(
                f"skip current: "
                f"{spec.get('title', window_id)}"
            )

            skipped += 1
            continue

        print(
            f"closing: "
            f"{spec.get('title', window_id)}"
        )

        close_window(window_id)

        closed += 1

        time.sleep(0.3)

    print()
    print(f"closed : {closed}")
    print(f"skipped: {skipped}")

    #
    # tempo para aplicações encerrarem
    #

    time.sleep(3)


if __name__ == "__main__":
    main()