from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class SmartHomeReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    light = Column(Integer)
    gas = Column(Integer)
    steam = Column(Integer)
    motion = Column(Integer)
    # Added tracking for door and window states[cite: 7]
    door_state = Column(Integer)  # 0 for closed, 1 for open
    window_state = Column(Integer)  # 0 for closed, 1 for open


engine = create_engine("sqlite:///smarthome_data.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()

print("✅ Database initialized: smarthome_data.db")
