from setuptools import setup

APP = ["app.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "packages": ["rumps", "speedtest"],
    "includes": ["monitor", "speedtest_runner", "log"],
    "iconfile": "icon.icns",
    "plist": {
        "CFBundleName": "NetMapper",
        "CFBundleDisplayName": "NetMapper",
        "CFBundleIdentifier": "com.netmapper.app",
        "CFBundleVersion": "1.0.0",
        "LSUIElement": True,  # hide from Dock
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
