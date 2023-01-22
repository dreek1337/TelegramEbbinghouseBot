from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Подключение и создание сессии
engine = create_engine(DATABASE)
conn = engine.connect()
session = Session(engine)