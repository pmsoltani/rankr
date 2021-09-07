from rankr.schemas.core import OrmBase
from rankr.schemas.institution import InstitutionOut
from rankr.schemas.ranking import RankingBase


class RankingTableRow(OrmBase, RankingBase):
    institution: InstitutionOut
