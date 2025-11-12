import os
import json
import signal
import hashlib
import logging
import requests
import tempfile
from pathlib import Path
from typing import Optional

from .common import IntervalExecutable
from crypto import crypto_manager

logger = logging.getLogger(__name__)


def hash_file(path: Path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class HeartbeatModule(IntervalExecutable):
    """Send a heartbeat and check for updates"""

    interval = 2

    DOMAIN = "http://localhost:8000"
    VERSION_FILE = Path("version.txt")
    EXECUTABLES_DIR = Path("executables")
    REQUEST_TIMEOUT = 10  # seconds

    @staticmethod
    def execute() -> None:
        try:
            latest_version = HeartbeatModule._fetch_latest_version()
            if latest_version is None:
                return

            local_version = HeartbeatModule._get_local_version()

            if local_version is None or latest_version > local_version:
                if HeartbeatModule._download_updates(local_version or -1):
                    HeartbeatModule._save_version(latest_version)
                    os.kill(os.getppid(), signal.SIGUSR1)

        except Exception as e:
            logger.error(f"Heartbeat execution failed: {e}", exc_info=True)

    @staticmethod
    def _fetch_latest_version() -> Optional[int]:
        try:
            response = requests.post(
                url=f"{HeartbeatModule.DOMAIN}/heartbeat",
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
                url=f"{HeartbeatModule.DOMAIN}/updates",
                params={"version": local_version},
                timeout=HeartbeatModule.REQUEST_TIMEOUT,
            )
            updates_res.raise_for_status()

            response_data = updates_res.json()
            manifest = response_data.get("manifest")
            signature = response_data.get("signature")

            # Verify this is a legitimate manifest
            crypto_manager.verify(
                json.dumps(manifest, sort_keys=True),
                signature=signature,
            )

            manifest_version = manifest.get("version")
            if not manifest_version or not isinstance(manifest_version, int):
                logger.error("Invalid version format")
                return False

            # Verify the version is after the local version to prevent replay attacks
            if manifest_version <= local_version:
                logger.error("Manifest version is outdated")
                return False

            files = manifest.get("files")
            if not isinstance(files, list):
                logger.error("Invalid files format")
                return False

            # Create temporary directory for downloads
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Download and validate all files first
                downloaded_files = []
                for f in files:
                    filename = f.get("name")
                    if not HeartbeatModule._is_safe_filename(filename):
                        logger.error(f"Unsafe filename rejected: {filename}")
                        return False

                    filehash = f.get("hash")
                    if not filehash:
                        logger.error(f"Missing hash for {filename}")
                        return False

                    temp_file_path = temp_path / filename
                    if not HeartbeatModule._download_file(filename, temp_file_path):
                        logger.error(f"Download failed for {filename}")
                        return False

                    # Verify hash
                    actual_hash = hash_file(temp_file_path)
                    if actual_hash != filehash:
                        logger.error(
                            f"Hash mismatch for {filename}: "
                            f"expected {filehash}, got {actual_hash}"
                        )
                        return False

                    downloaded_files.append((temp_file_path, filename))
                    logger.info(f"Validated: {filename}")

                # All files downloaded and validated - now commit them atomically
                HeartbeatModule.EXECUTABLES_DIR.mkdir(parents=True, exist_ok=True)

                for temp_file_path, filename in downloaded_files:
                    target_path = HeartbeatModule.EXECUTABLES_DIR / filename
                    # Atomic rename/replace
                    temp_file_path.rename(target_path)
                    logger.info(f"Installed: {filename}")

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
    def _download_file(filename: str, target_path: Path) -> bool:
        """Download file to specified path"""
        try:
            file_res = requests.get(
                url=f"{HeartbeatModule.DOMAIN}/updates/{filename}",
                timeout=HeartbeatModule.REQUEST_TIMEOUT,
            )
            file_res.raise_for_status()

            target_path.write_bytes(file_res.content)
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to download {filename}: {e}")
            return False
        except IOError as e:
            logger.error(f"Failed to write {filename}: {e}")
            return False
