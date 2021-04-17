from typing import List, Optional

from sqlalchemy.orm import Session

from rankr import db_models as d, schemas as s
from rankr.repos.base_repo import BaseRepo


class LabelRepo(BaseRepo):
    def __init__(self, db: Session) -> None:
        self.db_model = d.Label
        self.schema = s.LabelDB
        super().__init__(db, self.db_model, self.schema)

    def create_label(self, new_label: s.LabelCreate) -> s.LabelDB:
        return self._create_object(new_label)

    def create_labels(
        self, new_labels: List[s.LabelCreate], log: bool = True
    ) -> List[s.LabelDB]:
        return self._create_objects(new_labels, log=log)

    def get_label(self, label_id: int) -> Optional[s.LabelDB]:
        return self._get_object_by_id(object_id=label_id)

    def get_label_by_name(self, label: str) -> Optional[s.LabelDB]:
        return self._get_object([self.db_model.label == label])

    def get_labels(
        self,
        search_query: str = None,
        offset: int = 0,
        limit: Optional[int] = 25,
    ) -> List[s.LabelDB]:
        return self._get_objects(
            search_query=search_query, offset=offset, limit=limit
        )
