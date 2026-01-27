#!/bin/bash
# CommodityTrading Tidyup Script (Unix/Mac)
# Follows rules defined in tidyup.md

echo "========================================"
echo "  CommodityTrading Cleanup Utility"
echo "========================================"
echo ""

# Get current date for archive folder
ARCHIVE_DATE=$(date +%Y-%m-%d)

echo "[1/4] Cleaning temp folder..."
if [ -n "$(ls -A temp 2>/dev/null)" ]; then
    rm -f temp/*
    echo "      Temp files deleted."
else
    echo "      Temp folder already clean."
fi

echo ""
echo "[2/4] Cleaning data cache..."
if [ -n "$(ls -A data/cache 2>/dev/null)" ]; then
    # Delete files older than 24 hours
    find data/cache -type f -mtime +0 -delete 2>/dev/null
    echo "      Cache files older than 24h deleted."
else
    echo "      Cache already clean."
fi

echo ""
echo "[3/4] Cleaning raw data (if processed)..."
if [ -n "$(ls -A data/raw 2>/dev/null)" ]; then
    echo "      WARNING: Raw data exists. Check if processed before deleting."
    read -p "      Delete raw data? (y/N): " CONFIRM
    if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
        rm -f data/raw/*
        echo "      Raw data deleted."
    else
        echo "      Skipped."
    fi
else
    echo "      Raw data folder already clean."
fi

echo ""
echo "[4/4] Archive option..."
echo "      Current archive date would be: $ARCHIVE_DATE"
read -p "      Run full archive? (y/N): " ARCHIVE
if [[ "$ARCHIVE" =~ ^[Yy]$ ]]; then
    mkdir -p "archive/$ARCHIVE_DATE"
    echo "      Archive folder created: archive/$ARCHIVE_DATE"
    echo "      NOTE: Manual review required before moving files."
    echo "      Files to consider archiving:"
    echo "        - log.md"
    echo "        - modules/*"
    echo "        - data/processed/*"
else
    echo "      Archive skipped."
fi

echo ""
echo "========================================"
echo "  Cleanup complete!"
echo "========================================"
echo ""
echo "Protected files (never deleted):"
echo "  - brain/blueprint.md"
echo "  - brain/Idea.txt"
echo "  - tidyup.md"
echo "  - output/*.html (latest reports)"
echo ""
