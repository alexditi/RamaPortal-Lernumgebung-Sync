@echo off
set install_to=__dir__
set old_file=__file__
ping localhost -n 2
del %old_file%
move LernumgebungSynchronisation.exe %install_to%
ping localhost -n 2
%old_file%