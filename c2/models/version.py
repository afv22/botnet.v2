import hashlib
from typing import Any, Dict, List

from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db


_latest_version: int = -1


def hash_file(path: str):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class Version(db.Model):
    __tablename__ = "versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    files: Mapped[List["VersionFile"]] = relationship(
        "VersionFile", back_populates="version", cascade="all, delete-orphan"
    )

    @classmethod
    def register(cls, filenames: List[str]) -> int:
        global _latest_version

        files = []
        for fn in filenames:
            file_hash = hash_file("executables/" + fn)
            files.append(VersionFile(filename=str(fn), file_hash=file_hash))  # type: ignore

        new_version = Version(files=files)  # type: ignore
        db.session.add(new_version)
        db.session.commit()

        _latest_version = new_version.id
        return new_version.id

    @classmethod
    def list_modified_files(cls, last_seen: int) -> List[str]:
        versions = db.session.query(cls).where(cls.id > last_seen)

        modified_files = {}
        for version in versions:
            for file in version.files:
                if file.id not in modified_files:
                    modified_files[file.id] = file.json()

        return list(modified_files.values())

    @classmethod
    def latest_version(cls) -> int:
        global _latest_version
        if _latest_version == -1:
            _latest_version = db.session.query(func.max(cls.id)).scalar() or -1
        return _latest_version


class VersionFile(db.Model):
    from .version import Version

    __tablename__ = "version_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("versions.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    version: Mapped[Version] = relationship("Version", back_populates="files")

    __table_args__ = (db.Index("idx_version_filename", "version_id", "filename"),)

    def json(self) -> Dict[str, Any]:
        return {
            "name": self.filename,
            "hash": self.file_hash,
        }
