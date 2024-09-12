from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.query_models.product_query_model import CreateProductQueryModel


from ..models.base import Base


class ProductModel(Base):
    id: Mapped[str] = mapped_column("ID", String(100), primary_key=True, index=True)
    csv_file_id: Mapped[str] = mapped_column(
        "CSV_FILE_ID", String(100), ForeignKey("CSV_FILES.ID"), nullable=False, index=True
    )

    s_no: Mapped[str] = mapped_column(
        "PRODUCT_SL_NO",
        String(255),
        nullable=False,
    )

    product_name: Mapped[str] = mapped_column(
        "PRODUCT_NAME",
        String(255),
        nullable=False,
    )
    input_image_urls: Mapped[List[str]] = mapped_column(
        "INPUT_PRODUCT_IMAGE_URLS",
        JSON,
        nullable=False,
    )
    output_image_urls: Mapped[List[str]] = mapped_column(
        "OUTPUT_PRODUCT_IMAGE_URLS",
        JSON,
        nullable=False,
    )

    meta_data: Mapped[Dict[Any, Any]] = mapped_column("METADATA", JSON, nullable=False, default={})

    __tablename__ = "PRODUCTS"

    def __init__(self, create_product_request_model: CreateProductQueryModel):
        current_time = datetime.now()

        kw = asdict(create_product_request_model)

        kwargs = {key: value for key, value in kw.items() if key in self.__annotations__}

        super().__init__(**kwargs, created_at=current_time, updated_at=current_time)

        super().__init__(id=self.compute_and_get_id())

    def token(self) -> str:
        return "product"

    def get_identifiers(self) -> List[Any]:
        return [self.s_no, self.csv_file_id]
