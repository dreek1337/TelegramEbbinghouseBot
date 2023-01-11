from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Подключение и создание сессии
engine = create_engine('postgresql://postgres:danil2555danil@localhost/ebbinghouse')
conn = engine.connect()
session = Session(engine)