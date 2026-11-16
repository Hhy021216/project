from pathlib import Path
import pandas as pd
from db.models import Faq
from db.session import SessionLocal
from utils.preprocess import preprocess_text
import json

def register(app):
    @app.command("ingest-faq", help="导入 FAQ 数据到 MySQL")
    def ingest_faq():
        csv_path = Path(__file__).parent / "../storage/data/课程咨询FAQ.csv"
        data = pd.read_csv(csv_path, encoding="utf-8")
        write_to_mysql(data)
        print(f'导入成功 {len(data)} 条数据')


def write_to_mysql(data):
    with SessionLocal() as session:

        for row in data.to_dict(orient="records"):

            question = row["问题"]

            if not question or not str(question).strip():
                continue

            has = session.query(Faq).filter(Faq.question == question).first()
            if has:
                continue

            # ensure_ascii 
            tokens = json.dumps(preprocess_text(row["问题"]), ensure_ascii=False)
            faq = Faq(
                category=row["分类"],
                question=question,
                answer=row["答案"],
                tokens=tokens,
            )
            session.add(faq)

        session.commit()

