import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


load_dotenv()


def _build_database_url() -> URL | str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("DB_HOST")
    if not host:
        return "sqlite:///./smart_battery.db"

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")
    missing = [
        name
        for name, value in (
            ("DB_USER", user),
            ("DB_PASSWORD", password),
            ("DB_NAME", database),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Missing required database environment variable(s): "
            + ", ".join(missing)
        )

    try:
        port = int(os.getenv("DB_PORT", "3306"))
    except ValueError as exc:
        raise RuntimeError("DB_PORT must be a valid integer") from exc
    if not 1 <= port <= 65535:
        raise RuntimeError("DB_PORT must be between 1 and 65535")

    return URL.create(
        drivername="mysql+pymysql",
        username=user,
        password=password,
        host=host.removeprefix("https://").removeprefix("http://").rstrip("/"),
        port=port,
        database=database,
    )


def _create_engine() -> Engine:
    database_url = _build_database_url()
    if isinstance(database_url, str) and database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )

    connect_args = {}
    ssl_ca = os.getenv("DB_SSL_CA")
    if ssl_ca:
        connect_args["ssl"] = {"ca": ssl_ca}

    return create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


engine = _create_engine()
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
