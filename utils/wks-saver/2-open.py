#!/usr/bin/env python3

import json
import subprocess
import sys
import time

WORKSPACE_FILE = sys.argv[1] if len(sys.argv) > 1 else "workspace.json"


def launch(spec):

    cmd = spec.get("process_cmdline")

    if not cmd:
        return None

    try:
        print(f"starting: {cmd}")

        return subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except Exception as e:
        print(f"error starting [{cmd}] => {e}")
        return None


def find_window(title, timeout=60):

    end = time.time() + timeout

    while time.time() < end:

        try:

            import pywinctl as pwc

            for win in pwc.getAllWindows():

                try:
                    if win.title.strip() == title:
                        return win
                except Exception:
                    pass

        except Exception:
            pass

        time.sleep(1)

    return None


def restore_geometry(win, spec):

    try:

        if spec.get("minimized"):
            win.minimize()
            return

        if spec.get("maximized"):
            win.maximize()
            return

        win.restore()

    except Exception:
        pass

    try:
        win.moveTo(
            spec["left"],
            spec["top"]
        )
    except Exception:
        pass

    try:
        win.resizeTo(
            spec["width"],
            spec["height"]
        )
    except Exception:
        pass


with open(WORKSPACE_FILE, encoding="utf-8") as f:
    workspace = json.load(f)

windows = workspace["windows"]

started = []

print(f"windows in workspace: {len(windows)}")

#
# fase 1 - iniciar processos
#

for spec in windows:

    proc = launch(spec)

    if proc:
        started.append(spec)

    time.sleep(1)

#
# fase 2 - aguardar janelas e restaurar layout
#

for spec in started:

    title = spec["title"]

    print(f"waiting window: {title}")

    win = find_window(title)

    if not win:
        print(f"not found: {title}")
        continue

    print(f"restoring: {title}")

    restore_geometry(win, spec)

#
# fase 3 - ativar janela originalmente ativa
#

for spec in windows:

    if not spec.get("active"):
        continue

    win = find_window(spec["title"], timeout=5)

    if not win:
        continue

    try:
        win.activate()
    except Exception:
        pass

    break

print("workspace restored")