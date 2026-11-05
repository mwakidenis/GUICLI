"""Compatibility checks for core GUICLI application modules.

These checks run without PyQt6 and verify project identity consistency,
desktop metadata, configuration defaults, and documentation links.
"""

import configparser
import glob
import os
import re
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(name):
    path = os.path.join(ROOT, name)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def check_desktop_metadata():
    errors = []
    parser = configparser.ConfigParser()
    parser.read(os.path.join(ROOT, "noacli.desktop"))
    entry = parser["Desktop Entry"]
    if entry.get("Name") != "GUICLI":
        errors.append("desktop Name is not GUICLI")
    if entry.get("StartupWMClass") != "org.mwakidenis.guicli":
        errors.append("desktop StartupWMClass is not org.mwakidenis.guicli")
    return errors


def check_application_metadata():
    errors = []
    src = read("noacli.py")
    if 'app.setApplicationName("GUICLI")' not in src:
        errors.append('noacli.py does not set application name to GUICLI')
    if 'app.setOrganizationName("mwakidenis")' not in src:
        errors.append('noacli.py does not set organization to mwakidenis')
    if 'app.setDesktopFileName("org.mwakidenis.guicli")' not in src:
        errors.append('noacli.py does not set desktop file name')
    if "setWindowTitle('GUICLI: '+title)" not in src:
        errors.append("window title not GUICLI-branded")
    return errors


def check_ui_metadata():
    errors = []
    ui = read("lib/noacli_ui.ui")
    if '<string>GUICLI</string>' not in ui:
        errors.append("main window UI title not GUICLI")
    return errors


def check_settings_defaults():
    errors = []
    src = read("noacli.py")
    # Preserved compatibility identifier deliberately retained
    if "'HistFile':     [ '.noacli_history'" not in src:
        errors.append(".noacli_history compatibility identifier missing")
    if "__license__   = 'GPL v3'" not in src:
        errors.append("GPL v3 license header missing")
    if "__copyright__ = '2022-2026, Steven Dick <kg4ydw@gmail.com>'" not in src:
        errors.append("original copyright attribution missing")
    return errors


def check_readme_links():
    errors = []
    readme = read("Readme.md")
    for ref in re.findall(r"\((documentation/[^ )\"]+)", readme):
        if not os.path.exists(os.path.join(ROOT, ref)):
            errors.append("README links to missing file: " + ref)
    return errors


def check_no_unintended_old_branding():
    errors = []
    # User-facing application strings must not present the old product name.
    src = read("noacli.py")
    for bad in ["setWindowTitle('noacli", "setApplicationName(\"noacli\")",
                "Quit noacli?", "Don't close noacli"]:
        if bad in src:
            errors.append("unintended old branding in noacli.py: " + bad)
    return errors


def main():
    checks = [
        ("desktop metadata", check_desktop_metadata),
        ("application metadata", check_application_metadata),
        ("UI metadata", check_ui_metadata),
        ("settings defaults", check_settings_defaults),
        ("README links", check_readme_links),
        ("old branding", check_no_unintended_old_branding),
    ]
    failures = 0
    for label, func in checks:
        try:
            errors = func()
        except Exception as exc:  # pragma: no cover - diagnostic
            errors = [str(exc)]
        if errors:
            failures += 1
            print(f"FAIL {label}:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {label}")
    if failures:
        print(f"\n{failures} check(s) failed")
        sys.exit(1)
    print("\nAll compatibility checks passed")


if __name__ == "__main__":
    main()
