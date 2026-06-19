#!/usr/bin/env python3

import json
import sys
import time
import pywinctl as pwc

WORKSPACE_FILE = sys.argv[1] if len(sys.argv) > 1 else "workspace.json"


def find_windows(spec):

    matches = []

    wm_class = spec.get("wm_class")
    title = spec.get("title")

    for win in pwc.getAllWindows():

        try:

            current_title = str(win.title).strip()

            if not current_title:
                continue

            if title and current_title == title:
                matches.append(win)
                continue

            if wm_class:
                for clazz in wm_class:
                    if clazz and clazz.lower() in current_title.lower():
                        matches.append(win)
                        break

        except Exception:
            pass

    return matches


with open(WORKSPACE_FILE, encoding="utf-8") as f:
    workspace = json.load(f)

windows = workspace.get("windows", [])

print(f"windows in workspace: {len(windows)}")

closed = set()

for spec in reversed(windows):

    matches = find_windows(spec)

    for win in matches:

        try:

            wid = id(win)

            if wid in closed:
                continue

            print(f"closing: {win.title}")

            win.close()

            closed.add(wid)

            time.sleep(0.2)

        except Exception as e:
            print(f"error: {e}")

print(f"closed: {len(closed)}")