from typing import List

from sqlalchemy import Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from db import db


class Version(db.Model):
    __tablename__ = "versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filenames: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    @classmethod
    def register_new_vesion(cls, updated_modules: List[str]) -> int:
        new_version = Version(filenames=updated_modules)  # type: ignore
        db.session.add(new_version)
        db.session.commit()
        return new_version.id

    @classmethod
    def list_modified_files(cls, last_seen: int) -> List[str]:
        versions = db.session.query(cls).where(cls.id > last_seen)

        modified_files = set()
        for version in versions:
            for filename in version.filenames:
                modified_files.add(filename)

        return list(modified_files)
