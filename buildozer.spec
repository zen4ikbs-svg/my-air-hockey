[app]
title = Air Hockey
package.name = airhockey
package.domain = org.game.hockey
source.dir = .
source.include_exts = py,png,jpg,dat
version = 1.0

requirements = python3,pygame

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
