"""
HOUSEKEEPER Agent
Enforces folder management rules from tidyup.md
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import json


class Housekeeper:
    """
    Housekeeper Agent
    Enforces tidyup.md rules after each run
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.temp_dir = project_root / "temp"
        self.cache_dir = project_root / "data" / "cache"
        self.raw_dir = project_root / "data" / "raw"
        self.archive_dir = project_root / "archive"
        self.log_path = project_root / "log.md"

    def run(self) -> Dict:
        """
        Execute housekeeping tasks.
        Called after each analysis run.
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "actions": [],
            "errors": [],
        }

        # 1. Clean temp directory
        temp_result = self._clean_temp()
        results["actions"].append(temp_result)

        # 2. Clean old cache files (>24h)
        cache_result = self._clean_cache()
        results["actions"].append(cache_result)

        # 3. Verify protected files exist
        protected_result = self._verify_protected_files()
        results["actions"].append(protected_result)

        # 4. Log the cleanup
        self._log_cleanup(results)

        return results

    def _clean_temp(self) -> Dict:
        """Clean temporary files"""
        if not self.temp_dir.exists():
            return {"action": "clean_temp", "status": "skipped", "reason": "temp dir not found"}

        files_deleted = 0
        for item in self.temp_dir.iterdir():
            if item.is_file() and item.name != ".gitkeep":
                try:
                    item.unlink()
                    files_deleted += 1
                except Exception as e:
                    pass

        return {
            "action": "clean_temp",
            "status": "complete",
            "files_deleted": files_deleted,
        }

    def _clean_cache(self) -> Dict:
        """Clean cache files older than 24 hours"""
        if not self.cache_dir.exists():
            return {"action": "clean_cache", "status": "skipped", "reason": "cache dir not found"}

        cutoff = datetime.now() - timedelta(hours=24)
        files_deleted = 0

        for item in self.cache_dir.iterdir():
            if item.is_file() and item.name != ".gitkeep":
                try:
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if mtime < cutoff:
                        item.unlink()
                        files_deleted += 1
                except Exception as e:
                    pass

        return {
            "action": "clean_cache",
            "status": "complete",
            "files_deleted": files_deleted,
            "cutoff": "24 hours",
        }

    def _verify_protected_files(self) -> Dict:
        """Verify protected files exist"""
        protected_files = [
            self.project_root / "brain" / "blueprint.md",
            self.project_root / "brain" / "Idea.txt",
            self.project_root / "tidyup.md",
        ]

        missing = []
        for filepath in protected_files:
            if not filepath.exists():
                missing.append(str(filepath.relative_to(self.project_root)))

        return {
            "action": "verify_protected",
            "status": "complete" if not missing else "warning",
            "protected_files_checked": len(protected_files),
            "missing": missing,
        }

    def _log_cleanup(self, results: Dict):
        """Log cleanup actions to log.md"""
        if not self.log_path.exists():
            return

        timestamp = datetime.now().strftime("%H:%M")
        date = datetime.now().strftime("%Y-%m-%d")

        log_entry = f"\n### [{timestamp}] HOUSEKEEPER Cleanup\n"
        log_entry += f"- **Agent:** HOUSEKEEPER\n"
        log_entry += f"- **Action:** Automated cleanup\n"
        log_entry += f"- **Status:** Complete\n"

        for action in results.get("actions", []):
            log_entry += f"- **{action.get('action')}:** {action.get('status')}\n"

        try:
            with open(self.log_path, 'a') as f:
                f.write(log_entry)
        except Exception:
            pass

    def archive_session(self, commodity: str) -> Dict:
        """
        Archive a completed analysis session.
        Called manually or after session completion.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        archive_path = self.archive_dir / f"{date_str}_{commodity}"

        if archive_path.exists():
            # Add timestamp to make unique
            timestamp = datetime.now().strftime("%H%M")
            archive_path = self.archive_dir / f"{date_str}_{commodity}_{timestamp}"

        archive_path.mkdir(parents=True, exist_ok=True)

        # Move module outputs
        commodity_key = commodity.lower().replace(" ", "_")
        modules_path = self.project_root / "modules" / commodity_key

        if modules_path.exists():
            target = archive_path / "modules" / commodity_key
            target.mkdir(parents=True, exist_ok=True)

            for item in modules_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, target / item.name)

        return {
            "action": "archive_session",
            "commodity": commodity,
            "archive_path": str(archive_path),
            "status": "complete",
        }

    def get_status(self) -> Dict:
        """Get current housekeeping status"""
        temp_files = len(list(self.temp_dir.glob("*"))) if self.temp_dir.exists() else 0
        cache_files = len(list(self.cache_dir.glob("*"))) if self.cache_dir.exists() else 0
        archive_count = len(list(self.archive_dir.glob("*"))) if self.archive_dir.exists() else 0

        return {
            "temp_files": temp_files,
            "cache_files": cache_files,
            "archive_sessions": archive_count,
            "last_check": datetime.now().isoformat(),
        }
