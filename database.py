from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Database connection string
DATABASE_URL = "sqlite:///data/CNC_DB.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Function to get a new session
def get_session():
    return Session()

# Function to initialize the database (create tables)
def init_db():
    Base.metadata.create_all(engine)