from pathlib import Path
from typing import List

from config import DBConfig
from rankr.db_models import Institution, SessionLocal
from utils import csv_export, csv_size, ranking_process


db = SessionLocal()
all_institutions: List[Institution] = db.query(Institution).all()
soup = {}
for inst in all_institutions:
    try:
        soup[inst.country.country][inst.soup] = inst.grid_id
    except KeyError:
        soup[inst.country.country] = {inst.soup: inst.grid_id}
db.close()


not_mached = []
fuzz = []
for ranking_system in list(DBConfig.RANKINGS["metrics"]):
    dir_path: Path = DBConfig.MAIN_DIR / ranking_system
    if not dir_path.exists():
        continue

    files: List[Path] = sorted(
        [f for f in dir_path.iterdir() if f.suffix == ".csv"], reverse=True
    )
    for cnt, file in enumerate(files, start=1):
        print(f"Processing file ({cnt}/{len(files)}): {file.stem}")
        try:
            db = SessionLocal()
            size = csv_size(file)
            institutions_list, not_mached_list, fuzz_list = ranking_process(
                db, file, soup
            )
            if len(institutions_list) + len(not_mached_list) != size:
                raise ValueError("Some institutions may have been lost!")
            not_mached.extend(not_mached_list)
            fuzz.extend(fuzz_list)
            if institutions_list:
                db.add_all(institutions_list)
                db.commit()
        except ValueError as exc:
            print(exc)
        finally:
            db.close()

if not_mached:
    csv_export(DBConfig.MAIN_DIR / "not_mached.csv", not_mached)
    print(f"Saved the list of {len(not_mached)} not matched institutions.")

if fuzz:
    csv_export(DBConfig.MAIN_DIR / "fuzz.csv", fuzz)
    print(f"Saved the list of {len(fuzz)} fuzzy-matched institutions.")
