import os
import sqlalchemy
from dotenv import load_dotenv
load_dotenv()

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@" \
         f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = sqlalchemy.create_engine(DB_URL, pool_pre_ping=True)        
