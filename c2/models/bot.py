from typing import Sequence
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db import db


class Bot(db.Model):
    __tablename__ = "bots"

    ip: Mapped[str] = mapped_column(String(255), primary_key=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()

        super().__init__()

    @classmethod
    def all(cls) -> Sequence["Bot"]:
        return db.session.query(cls).all()

    @classmethod
    def heartbeat(cls, ip: str) -> None:
        bot = db.session.query(cls).where(cls.ip == ip).one_or_none()

        if bot:
            bot.last_seen = datetime.now()
        else:
            bot = Bot(ip=ip)

        db.session.add(bot)
        db.session.commit()

    def json(self):
        return {
            "ip": self.ip,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }
