@echo off
cd /d "%~dp0"
py -m src.main --config configs/default.toml --vfs src
pause