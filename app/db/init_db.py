from sqlalchemy.orm import Session

from app.db.session import engine
from app.db.base import Base


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations. But if you don't want to use migrations, create the tables un-commenting the next line
    Base.metadata.create_all(bind=engine)
