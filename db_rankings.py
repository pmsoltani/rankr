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

    files: List[Path] = sorted(list(dir_path.iterdir()))
    for cnt, file in enumerate(files, start=1):
        if file.suffix != ".csv":
            continue

        print(f"Processing file ({cnt}/{len(files)}): {file.stem}")
        try:
            db = SessionLocal()
            institutions_list = ranking_process(db, file)
            if institutions_list:
                db.add_all(institutions_list)
                db.commit()
        finally:
            db.close()
