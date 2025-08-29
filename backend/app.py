import datetime
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func, and_

from db import Base, engine, SessionLocal
from pipeline import Letter, Citation, Lineage

app = FastAPI(title="GKS Demo API", version="0.1.0")

# CORS for local frontend (http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)

@app.get("/health")
def health():
    return {"ok": True, "now": datetime.datetime.utcnow().isoformat()}

def d(s: Optional[str], default: datetime.date) -> datetime.date:
    """Parse YYYY-MM-DD or return default."""
    return default if not s else datetime.date.fromisoformat(s)

@app.get("/top-cfr")
def top_cfr(
    start: Optional[str] = None,
    end: Optional[str] = None,
    product_type: Optional[str] = None,
    limit: int = 10,
):
    s_date, e_date = d(start, datetime.date(2000, 1, 1)), d(end, datetime.date.today())
    with SessionLocal() as ses:
        q = (
            select(Citation.cfr_code, func.count().label("ct"))
            .join(Letter, Citation.letter_id == Letter.id)
            .where(and_(Letter.issue_date >= s_date, Letter.issue_date <= e_date))
        )
        if product_type:
            q = q.where(Letter.product_type == product_type)
        rows = ses.execute(
            q.group_by(Citation.cfr_code).order_by(func.count().desc()).limit(limit)
        ).all()
        return [{"cfr_code": r[0], "count": int(r[1])} for r in rows]

@app.get("/issuing-offices")
def issuing_offices(start: Optional[str] = None, end: Optional[str] = None):
    s_date, e_date = d(start, datetime.date(2000, 1, 1)), d(end, datetime.date.today())
    with SessionLocal() as ses:
        rows = ses.execute(
            select(Letter.issuing_office, func.count().label("ct"))
            .where(and_(Letter.issue_date >= s_date, Letter.issue_date <= e_date))
            .group_by(Letter.issuing_office)
            .order_by(func.count().desc())
        ).all()
        return [{"issuing_office": r[0], "count": int(r[1])} for r in rows]

@app.get("/letters")
def letters(
    start: Optional[str] = None,
    end: Optional[str] = None,
    product_type: Optional[str] = None,
    limit: int = 50,
):
    s_date, e_date = d(start, datetime.date(2000, 1, 1)), d(end, datetime.date.today())
    with SessionLocal() as ses:
        q = (
            select(Letter)
            .where(and_(Letter.issue_date >= s_date, Letter.issue_date <= e_date))
            .order_by(Letter.issue_date.desc())
            .limit(limit)
        )
        if product_type:
            q = q.where(Letter.product_type == product_type)
        rows = ses.execute(q).scalars().all()
        out = []
        for l in rows:
            out.append(
                {
                    "id": l.id,
                    "firm": l.firm,
                    "product_type": l.product_type,
                    "issuing_office": l.issuing_office,
                    "issue_date": l.issue_date.isoformat(),
                    "url": l.url,
                }
            )
        return out

@app.get("/lineage")
def lineage(limit: int = 20):
    with SessionLocal() as ses:
        rows = ses.execute(select(Lineage).limit(limit)).scalars().all()
        return [
            {
                "letter_id": r.letter_id,
                "source_url": r.source_url,
                "fetched_at": r.fetched_at.isoformat(),
                "sha256_raw": r.sha256_raw,
            }
            for r in rows
        ]

@app.get("/top-cfr-trend")
def top_cfr_trend(
    start: Optional[str] = None,
    end: Optional[str] = None,
    product_type: Optional[str] = None,
    limit: int = 5,
):
    """Monthly counts for the top-N CFR codes within the window."""
    s_date, e_date = d(start, datetime.date(2000, 1, 1)), d(end, datetime.date.today())
    with SessionLocal() as ses:
        # 1) get top-N codes
        base = (
            select(Citation.cfr_code, func.count().label("ct"))
            .join(Letter, Citation.letter_id == Letter.id)
            .where(and_(Letter.issue_date >= s_date, Letter.issue_date <= e_date))
        )
        if product_type:
            base = base.where(Letter.product_type == product_type)

        q_top = base.group_by(Citation.cfr_code).order_by(func.count().desc()).limit(limit)
        res = ses.execute(q_top).all()
        top_codes = [row[0] for row in res]
        if not top_codes:
            return {"codes": [], "series": []}

        # 2) monthly buckets (SQLite)
        from collections import defaultdict
        counts = defaultdict(lambda: {code: 0 for code in top_codes})

        month = func.strftime("%Y-%m", Letter.issue_date).label("period")
        q = (
            select(month, Citation.cfr_code, func.count())
            .join(Letter, Citation.letter_id == Letter.id)
            .where(
                and_(
                    Letter.issue_date >= s_date,
                    Letter.issue_date <= e_date,
                    Citation.cfr_code.in_(top_codes),
                )
            )
        )
        if product_type:
            q = q.where(Letter.product_type == product_type)

        q = q.group_by(month, Citation.cfr_code).order_by(month.asc())

        for period, code, ct in ses.execute(q).all():
            counts[period][code] = int(ct)

        series = [{"period": p, **counts[p]} for p in sorted(counts.keys())]
        return {"codes": top_codes, "series": series}
