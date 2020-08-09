from pathlib import Path
from typing import List

from config import DBConfig
from rankr.db_models import SessionLocal
from utils import ranking_process

ranking_systems = DBConfig.RANKINGS["ranking_systems"]

for system in ranking_systems:
    dir_path: Path = DBConfig.MAIN_DIR / system
    if not dir_path.exists():
        continue

    files: List[Path] = sorted(
        [f for f in dir_path.iterdir() if f.suffix == ".csv"], reverse=True
    )
    for cnt, file in enumerate(files, start=1):
        print(f"Processing file ({cnt}/{len(files)}): {file.stem}")
        try:
            db = SessionLocal()
            institutions_list = ranking_process(db, file)
            if institutions_list:
                db.add_all(institutions_list)
                db.commit()
        finally:
            db.close()
