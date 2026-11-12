from app.database import Base,engine,SessionLocal
from app.seed import seed
from app import models
Base.metadata.create_all(engine)
with SessionLocal() as db:seed(db)
print('Database ready; existing station data preserved.')
