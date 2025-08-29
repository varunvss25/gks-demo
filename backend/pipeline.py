import csv, hashlib, datetime
from typing import Dict, Any, List
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint, select, create_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, declarative_base
from parsers import extract_cfr_codes

# SQLite DB
DB_URL = "sqlite:///gks_demo.db"
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class Letter(Base):
    __tablename__ = "letters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firm: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(String(64), nullable=False)
    issuing_office: Mapped[str] = mapped_column(String(64), nullable=False)
    issue_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    raw_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    fetched_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    citations = relationship("Citation", back_populates="letter", cascade="all, delete-orphan")
    lineage = relationship("Lineage", uselist=False, back_populates="letter", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("firm","issue_date","url", name="uq_letter_dedup"),)

class Citation(Base):
    __tablename__ = "citations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    letter_id: Mapped[int] = mapped_column(ForeignKey("letters.id"), nullable=False)
    cfr_code: Mapped[str] = mapped_column(String(32), nullable=False)
    letter = relationship("Letter", back_populates="citations")

class Lineage(Base):
    __tablename__ = "lineage"
    letter_id: Mapped[int] = mapped_column(ForeignKey("letters.id"), primary_key=True)
    source_url: Mapped[str] = mapped_column(String(512), nullable=False)
    fetched_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    sha256_raw: Mapped[str] = mapped_column(String(64), nullable=False)
    letter = relationship("Letter", back_populates="lineage")

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def run_etl(csv_path: str = "../data/sample_warning_letters.csv") -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as ses, open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            firm = row["firm"].strip()
            product_type = row["product_type"].strip()
            issuing_office = row["issuing_office"].strip()
            issue_date = datetime.date.fromisoformat(row["issue_date"].strip())
            url = row["url"].strip()
            text = row["raw_text"].strip()

            exists = ses.execute(
                select(Letter).where(Letter.firm==firm, Letter.issue_date==issue_date, Letter.url==url)
            ).scalar_one_or_none()
            if exists:
                continue

            letter = Letter(
                firm=firm, product_type=product_type, issuing_office=issuing_office,
                issue_date=issue_date, url=url, raw_sha256=sha256(text),
                fetched_at=datetime.datetime.utcnow()
            )
            ses.add(letter); ses.flush()

            for code in extract_cfr_codes(text):
                ses.add(Citation(letter_id=letter.id, cfr_code=code))

            ses.add(Lineage(
                letter_id=letter.id, source_url=url,
                fetched_at=datetime.datetime.utcnow(), sha256_raw=sha256(text)
            ))
        ses.commit()
    print("ETL complete.")

if __name__ == "__main__":
    run_etl()
