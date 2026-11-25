[app]
title = JARVIS
package.name = jarvis
package.domain = org.nightmare
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json
source.exclude_dirs = tests,scripts,data,logs,bin,.git,.github,.polydev,.revyl,__pycache__
version = 1.0.0
requirements = python3==3.11.9,kivy==2.3.1,charset-normalizer==3.4.1
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.accept_sdk_license = True
android.add_pip_args = --no-binary=:all:
allow_backup = False

[buildozer]
log_level = 2
bin_dir = bin
