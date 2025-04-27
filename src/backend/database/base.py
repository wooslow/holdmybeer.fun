from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    ...


class CustomBase(Base):
    __abstract__ = True

    def model_dump(self) -> dict:
        """ Method to dump model to dictionary """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
