@echo off
REM CommodityTrading Tidyup Script (Windows)
REM Follows rules defined in tidyup.md

echo ========================================
echo   CommodityTrading Cleanup Utility
echo ========================================
echo.

REM Get current date for archive folder
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set datetime=%%I
set ARCHIVE_DATE=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

echo [1/4] Cleaning temp folder...
if exist "temp\*" (
    del /q "temp\*" 2>nul
    echo       Temp files deleted.
) else (
    echo       Temp folder already clean.
)

echo.
echo [2/4] Cleaning data cache (files older than 24h would be deleted)...
if exist "data\cache\*" (
    del /q "data\cache\*" 2>nul
    echo       Cache cleared.
) else (
    echo       Cache already clean.
)

echo.
echo [3/4] Cleaning raw data (if processed)...
if exist "data\raw\*" (
    echo       WARNING: Raw data exists. Check if processed before deleting.
    set /p CONFIRM="       Delete raw data? (y/N): "
    if /i "%CONFIRM%"=="y" (
        del /q "data\raw\*" 2>nul
        echo       Raw data deleted.
    ) else (
        echo       Skipped.
    )
) else (
    echo       Raw data folder already clean.
)

echo.
echo [4/4] Archive option...
echo       Current archive date would be: %ARCHIVE_DATE%
set /p ARCHIVE="       Run full archive? (y/N): "
if /i "%ARCHIVE%"=="y" (
    if not exist "archive\%ARCHIVE_DATE%" mkdir "archive\%ARCHIVE_DATE%"
    echo       Archive folder created: archive\%ARCHIVE_DATE%
    echo       NOTE: Manual review required before moving files.
    echo       Files to consider archiving:
    echo         - log.md
    echo         - modules\*
    echo         - data\processed\*
) else (
    echo       Archive skipped.
)

echo.
echo ========================================
echo   Cleanup complete!
echo ========================================
echo.
echo Protected files (never deleted):
echo   - brain\blueprint.md
echo   - brain\Idea.txt
echo   - tidyup.md
echo   - output\*.html (latest reports)
echo.
pause
