import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

host = os.getenv('HOST')
dbname = os.getenv('DB_NAME')
dbuser = os.getenv('DB_USERNAME')
dbpassw = os.getenv('DB_PASSWORD')

engine = create_engine(f'postgresql://{dbuser}:{dbpassw}@{host}/{dbname}')

Session = sessionmaker(bind=engine)
session = Session()
session.close()