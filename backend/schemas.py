from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime

class TransportTaskBase(BaseModel):
    nom: str
    offres: List[int]
    demandes: List[int]
    couts: List[List[int]]
    algo_utilise: Literal["cno", "hammer"]

class TransportTaskCreate(TransportTaskBase):
    pass

class TransportTaskResult(BaseModel):
    allocation: List[List[Optional[float]]] # Epsilon can be float
    cout_total: float

class TransportTaskOut(TransportTaskBase):
    id: int
    resultat: Optional[TransportTaskResult] = None # Current active result
    # cout_total is part of resultat now, but keeping for compatibility if old model has it
    cout_total: Optional[float] = None

    initial_result: Optional[TransportTaskResult] = None
    optimized_result: Optional[TransportTaskResult] = None
    is_optimized: bool = False

    date_creation: datetime
    date_derniere_maj: Optional[datetime] = None

    class Config:
        model_config = ConfigDict(from_attributes=True)


class TransportTaskSummary(BaseModel):
    id: int
    nom: str
    algo_utilise: str
    # This cout_total should reflect the one in 'resultat'
    cout_total: Optional[float] = None
    is_optimized: bool = False
    date_creation: datetime
    date_derniere_maj: Optional[datetime] = None

    class Config:
        model_config = ConfigDict(from_attributes=True)

class TransportTaskUpdate(BaseModel):
    nom: Optional[str] = None # Allow updating name
    offres: Optional[List[int]] = None
    demandes: Optional[List[int]] = None
    couts: Optional[List[List[int]]] = None
    algo_utilise: Optional[str] = None  # facultatif
