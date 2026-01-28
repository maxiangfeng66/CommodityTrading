@echo off
echo Starting Commodity Trading Visualizer...
cd /d "%~dp0.."
python visualizer/serve_visualizer.py
pause
