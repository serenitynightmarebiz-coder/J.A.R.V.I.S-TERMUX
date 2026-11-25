[app]
title = JARVIS
package.name = jarvis
package.domain = org.nightmare
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json
source.exclude_dirs = tests,scripts,data,logs,bin,.git,.github,.polydev,.revyl,__pycache__
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.accept_sdk_license = True
allow_backup = False

[buildozer]
log_level = 2
bin_dir = bin
