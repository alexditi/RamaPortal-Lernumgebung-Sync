@echo off
ping localhost -n 2
del old_file /q
move LernumgebungSynchronisation.exe install_to
ping localhost -n 2
old_file