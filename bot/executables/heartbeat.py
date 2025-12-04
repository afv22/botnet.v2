import os
import json
import signal
import logging
import requests
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from nacl.exceptions import BadSignatureError

from .common import IntervalExecutable
from crypto import crypto_manager

logger = logging.getLogger(__name__)


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
            # Fetch new version
            latest_version = HeartbeatModule._fetch_latest_version()
            if not latest_version:
                return

            local_version = HeartbeatModule._fetch_local_version()
            if local_version == latest_version:
                return

            if local_version > latest_version:
                logger.warning(f"Heartbeat broadcasted stale version: {latest_version}")
                return

            # If new version, fetch manifest
            try:
                manifest, signature = HeartbeatModule._fetch_manifest(local_version)
            except Exception as e:
                logger.error(f"Manifest fetch failed: {e}")
                return

            # Verify manifest signature
            crypto_manager.verify(
                message=json.dumps(manifest, sort_keys=True),
                signature=signature,
            )

            # Verify manifest version
            manifest_version = manifest.get("version", -1)
            if manifest_version != latest_version:
                logger.error(
                    f"Manifest version {manifest_version} does not "
                    f"match broadcasted version {latest_version}"
                )
                return

            # For each file in manifest:
            file_metadata = manifest.get("files", [])
            with tempfile.TemporaryDirectory() as temp_dir:
                tmpfiles: List[Tuple[Path, str]] = []
                tmpdir = Path(temp_dir)
                for file in file_metadata:
                    filename = file.get("name")
                    if not filename:
                        logger.error("File name not found")
                        return

                    if not HeartbeatModule._is_safe_filename(filename):
                        logger.error(f"Unsafe filename: {filename}")
                        return

                    filehash = file.get("hash")
                    if not filehash:
                        logger.error("File hash not found")

                    # Download to temp file
                    tmpfile = HeartbeatModule._download_file(filename, tmpdir)
                    if not tmpfile:
                        return

                    # Verify temp file hash
                    hash = crypto_manager.hash_file(tmpfile)
                    if hash != filehash:
                        logger.error(f"Corrupted file: {filename}")
                        return

                    tmpfiles.append((tmpfile, filename))

                # If all files are valid:
                for tmpfile, filename in tmpfiles:
                    # Save to executables directory
                    target_path = HeartbeatModule.EXECUTABLES_DIR / filename
                    tmpfile.rename(target_path)
                    logger.info(f"Installed: {filename}")

            # Save new version
            HeartbeatModule.VERSION_FILE.write_text(str(manifest_version))

            # Refresh running jobs
            os.kill(os.getppid(), signal.SIGUSR1)

        except BadSignatureError:
            logger.error("Invalid signature")

        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")

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
                return

            return version

        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")

    @staticmethod
    def _fetch_local_version() -> int:
        try:
            # Check if version file is initialized
            if not HeartbeatModule.VERSION_FILE.exists:
                return -1

            version = HeartbeatModule.VERSION_FILE.read_text()

            try:
                return int(version)
            except ValueError:
                logger.error(f"Invalid local version: {version}")
                return -1

        except Exception as e:
            logger.error(f"Local version fetch failed: {e}")
            return -1

    @staticmethod
    def _fetch_manifest(local_version: int) -> Tuple[Dict[str, Any], str]:
        updates_res = requests.get(
            url=f"{HeartbeatModule.DOMAIN}/updates",
            params={"version": local_version},
            timeout=HeartbeatModule.REQUEST_TIMEOUT,
        )
        updates_res.raise_for_status()

        updates_data = updates_res.json()
        manifest = updates_data.get("manifest")
        signature = updates_data.get("signature")

        if not manifest:
            raise RuntimeError("Manifest not found")
        if not signature:
            raise RuntimeError("Signature not found")

        return (manifest, signature)

    @staticmethod
    def _download_file(filename: str, target_dir: Path) -> Optional[Path]:
        try:
            file_res = requests.get(
                url=f"{HeartbeatModule.DOMAIN}/updates/{filename}",
                timeout=HeartbeatModule.REQUEST_TIMEOUT,
            )
            file_res.raise_for_status()

            target_path = target_dir / filename
            target_path.write_bytes(file_res.content)

            return target_path
        except Exception as e:
            logger.error(f"Download failed for {filename}: {e}")

    @staticmethod
    def _is_safe_filename(filename: str) -> bool:
        """Validate filename to prevent path traversal attacks"""
        safe_path = (HeartbeatModule.EXECUTABLES_DIR / filename).resolve()
        return HeartbeatModule.EXECUTABLES_DIR.resolve() in safe_path.parents
