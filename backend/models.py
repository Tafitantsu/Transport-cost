from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from database import Base  # Assure-toi d’avoir Base depuis ton engine SQLAlchemy

class TransportTask(Base):
    __tablename__ = "transport_tasks"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    offres = Column(JSON, nullable=False)
    demandes = Column(JSON, nullable=False)
    couts = Column(JSON, nullable=False)
    algo_utilise = Column(String, nullable=False)  # "coin" ou "hammer"

    # result stores the current active solution (can be initial or optimized)
    resultat = Column(JSON, nullable=True)  # allocation + cout_total
    # cout_total is deprecated here, should be part of 'resultat' to keep things consistent.
    # For now, I will keep it to minimize immediate breaking changes, but it should be refactored.
    cout_total = Column(Float, nullable=True)

    initial_result = Column(JSON, nullable=True) # Stores the result from CNO/Hammer
    optimized_result = Column(JSON, nullable=True) # Stores the result from Stepping Stone
    is_optimized = Column(Boolean, default=False, nullable=False)

    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_derniere_maj = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
