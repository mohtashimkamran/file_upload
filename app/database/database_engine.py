from typing import Optional
from sqlalchemy import create_engine, Engine
import os
from dotenv import load_dotenv


class DatabaseEngine:
    engine: Optional[Engine] = None

    @classmethod
    def create_mysql_db_engine(cls) -> Engine:
        if cls.engine is not None:
            return cls.engine

        load_dotenv()

        environment = os.getenv("ENVIRONMENT")

        if environment == "TEST":
            # Use in-memory SQLite for testing environment
            cls.engine = create_engine("sqlite:///:memory:", echo=True)
        else:
            # Ensure the database is in the root of the project
            project_root = os.path.dirname(
                os.path.abspath(__file__)
            )  # Get the current script's directory
            db_file = os.getenv(f"{environment}_DATABASE_PATH", "sqlite.db")
            db_path = os.path.join(project_root, db_file)

            # Use a file-based SQLite database in the root of the project directory
            cls.engine = create_engine(f"sqlite:///{db_path}", echo=True)

        return cls.engine
