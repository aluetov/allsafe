from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from .db import Base


class Domain(Base):
    __tablename__ = "domains"
    id: Mapped[int] = mapped_column(primary_key=True)
    qname: Mapped[str]
    canonical_name: Mapped[str]
    record_type: Mapped[str]
    record_class: Mapped[str]
    expiration: Mapped[float]
    records: Mapped[list[str]] = mapped_column(JSON)
