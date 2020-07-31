import enum

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL, Enum, Integer, String

from ranker.db_models.base import Base


class RankingSystemEnum(enum.Enum):
    qs = 1
    shanghai = 2
    the = 3


class MetricEnum(enum.Enum):
    Rank = 1
    NationalRank = 2
    Overall = 3
    Alumni = 4
    Award = 5
    HiCi = 6
    NatureScience = 7
    PUB = 8
    PCP = 9
    FTEStudents = 10
    StudentsPerStaff = 11
    InternationlStudents = 12
    FemaleStudents = 13
    Teaching = 14
    Research = 15
    Citations = 16
    IndustryIncome = 17
    InternationalOutlook = 18
    AcademicReputation = 19
    EmployerReputation = 20
    FacultyStudent = 21
    InternationalFaculty = 22
    InternationalStudents = 23
    CitationsPerFaculty = 24


class ValueTypeEnum(enum.Enum):
    Integer = 1
    Percent = 2
    Decimal = 3


class Ranking(Base):
    __tablename__ = "ranking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    ranking_system = Column(Enum(RankingSystemEnum), nullable=False, index=True)
    year = Column(Integer)
    field = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    metric = Column(Enum(MetricEnum), nullable=False, index=True)
    value = Column(DECIMAL(13, 3), nullable=False)
    value_type = Column(Enum(ValueTypeEnum), nullable=False)

    # Relationships
    institution = relationship("Institution", back_populates="rankings")
