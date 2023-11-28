#-*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"build_exe": "driver",
                     "excludes": ["tkinter", "email", "xml", "unittest"],
                     "include_files": ["setting.cfg"]}

if sys.platform == 'darwin':
    build_exe_options["build_exe"] = "driver_mac",
if sys.platform == 'linux2':
    build_exe_options["build_exe"] = "driver_linux",

setup(  name = "OnFitCardReader",
        version = "1.0",
        description = "OnFitCardReader",
        options = {"build_exe": build_exe_options},
        executables = [Executable("OnFitCardReader.py")])