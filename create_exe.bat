@echo off
pyinstaller %1 -n "Inventory Manager" -F -i images/cargo.ico main_window.py