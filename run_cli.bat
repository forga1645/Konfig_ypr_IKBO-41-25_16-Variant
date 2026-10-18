@echo off
cd /d "%~dp0"
py -m src.main --vfs tests/data/vfs_minimal --script scripts/start.txt