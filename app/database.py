from sqlalchemy import Column, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text)
    feedback = Column(Text)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def save_user(user_id, username, age, weight, goal, intensity) -> None:
    with SessionLocal() as session:
        existing = session.query(User).filter_by(user_id=user_id).first()
        if existing:
            existing.username = username
            existing.age = age
            existing.weight = weight
            existing.goal = goal
            existing.intensity = intensity
        else:
            session.add(
                User(
                    user_id=user_id,
                    username=username,
                    age=age,
                    weight=weight,
                    goal=goal,
                    intensity=intensity,
                )
            )
        session.commit()


def save_plan(user_id: str, original_plan: str) -> None:
    with SessionLocal() as session:
        existing = session.query(Plan).filter_by(user_id=user_id).first()
        if existing:
            existing.original_plan = original_plan
            existing.updated_plan = None
            existing.feedback = None
        else:
            session.add(Plan(user_id=user_id, original_plan=original_plan))
        session.commit()


def update_plan(user_id: str, updated_plan: str, feedback: str) -> None:
    with SessionLocal() as session:
        plan = session.query(Plan).filter_by(user_id=user_id).first()
        if plan:
            plan.updated_plan = updated_plan
            plan.feedback = feedback
            session.commit()


def get_user(user_id: str):
    with SessionLocal() as session:
        return session.query(User).filter_by(user_id=user_id).first()


def get_original_plan(user_id: str):
    with SessionLocal() as session:
        return session.query(Plan).filter_by(user_id=user_id).first()


def get_all_users():
    with SessionLocal() as session:
        return session.query(User).all()


def get_all_plans():
    with SessionLocal() as session:
        return session.query(Plan).all()


def delete_user(user_id: str) -> None:
    with SessionLocal() as session:
        session.query(User).filter_by(user_id=user_id).delete()
        session.query(Plan).filter_by(user_id=user_id).delete()
        session.commit()
