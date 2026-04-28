from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


# This is the "Blueprint" for your data
class SmartHomeReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    light = Column(Integer)
    gas = Column(Integer)
    steam = Column(Integer)
    motion = Column(Integer)


# Create the database file
engine = create_engine("sqlite:///smarthome_data.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()

print("✅ Database initialized: smarthome_data.db")
