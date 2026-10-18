@echo off
cd /d "%~dp0"
py -m src.main --vfs tests/data/vfs_small --script scripts/start.txt
pause