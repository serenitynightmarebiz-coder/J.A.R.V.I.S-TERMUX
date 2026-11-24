[buildozer]
title = JARVIS
package.name = jarvis
package.domain = org.nightmare
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json
source.exclude_exts = spec
version = 1.0.0
allow_backup = False

[app]
name = JARVIS
source.dir = .
requirements = python3,kivy
android.archs = armeabi-v7a arm64-v8a
android.gradle_version = 3.5.0
android.add_compile_flags = -Wno-error
p4a.source_path = .
android.fulltrace = True