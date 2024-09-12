from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import BLOB, JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.query_models.csv_query_model import CreateCsvQueryModel


from ..models.base import Base


class CsvModel(Base):
    id: Mapped[str] = mapped_column("ID", String(100), primary_key=True, index=True)
    csv_file: Mapped[Optional[bytes]] = mapped_column(
        "csv_file", BLOB, nullable=True
    )  # Column to store the CSV file as binary data
    is_processed: Mapped[bool] = mapped_column(
        "is_processed", Boolean, default=False
    )  # Column to store whether the CSV has been processed

    meta_data: Mapped[Dict[Any, Any]] = mapped_column("METADATA", JSON, nullable=False, default={})

    __tablename__ = "CSV_FILES"

    def __init__(self, create_csv_request_model: CreateCsvQueryModel):
        current_time = datetime.now()

        kw = asdict(create_csv_request_model)

        kwargs = {key: value for key, value in kw.items() if key in self.__annotations__}

        super().__init__(**kwargs, created_at=current_time, updated_at=current_time)

        super().__init__(id=self.compute_and_get_id())

    def token(self) -> str:
        return "csv"

    def get_identifiers(self) -> List[Any]:
        return [self.csv_file]
