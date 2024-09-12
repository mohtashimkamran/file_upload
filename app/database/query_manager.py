from typing import Any, List, Optional, Type, TypeVar, Union

import sqlalchemy
from app.logger import logger
from app.database.database_engine import DatabaseEngine
from app.database.models.base import Base
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.sql.expression import ColumnElement, BinaryExpression, UnaryExpression


database_engine = DatabaseEngine.create_mysql_db_engine()
from .models.product import ProductModel
from .models.csv_model import CsvModel

Base.metadata.create_all(database_engine)

T = TypeVar("T")


def insert_single_object(db_object: Any) -> None:
    with Session(database_engine) as session:
        try:
            session.merge(db_object)
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"Error in inserting object to database. {e.args}")
            raise e


def query_by_id(model: Type[T], object_id: str) -> T:
    with Session(database_engine) as session:
        try:
            result = session.query(model).filter(model.id == object_id).one_or_none()  # type: ignore[attr-defined]
            value = result

            session.expunge_all()
            session.commit()

        except Exception as e:
            raise RuntimeError(f"error in fetching object for id = {object_id}. Error = {e.args}")

    if value is None:
        raise ValueError(
            f"No {model._sa_class_manager.class_.__name__} found for id = {object_id}"  # type: ignore[attr-defined]
        )

    return value


def query_with_filter(
    filters: Union[ColumnElement[bool], BinaryExpression[bool]],
    model: Type[T],
    order_by: Optional[UnaryExpression[Any]] = None,
    limit: Optional[int] = None,
    offset: int = 0,
    is_dict_response: bool = False,
) -> List[T]:
    values = []
    with Session(database_engine) as session:
        try:
            query = session.query(model).filter(filters).order_by(order_by)

            if limit:
                query = query.limit(limit)

            if offset:
                query = query.offset(offset)

            results = query.all()

            for result_row in results:
                if is_dict_response is True:
                    values.append(result_row._asdict())  # type: ignore[attr-defined]
                else:
                    values.append(result_row)

        except Exception as e:
            logger.error(f"Error in reading objects from database. {e.args}")
            raise e

    return values


def get_attributes_of_object(obj: T) -> List[str]:
    attributes: List[str] = [
        attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("_")
    ]
    return attributes


def update_single_object(model: Type[T], updated_object: T) -> T:
    with Session(database_engine) as session:
        try:
            database_object = (
                session.query(model)
                .filter(and_(model.id == updated_object.id))  # type: ignore[attr-defined]
                .one_or_none()
            )

            if database_object is None:
                raise ValueError(
                    f"No object found for model = {model} with id = {updated_object.id}"  # type: ignore[attr-defined]
                )

            object_attributes = get_attributes_of_object(updated_object)

            for attribute in object_attributes:
                if hasattr(updated_object, attribute):
                    setattr(database_object, attribute, getattr(updated_object, attribute))

            session.commit()
        except Exception as e:
            logger.error(f"Error in updating object in database. {e.args}")
            raise e

    return query_by_id(model=model, object_id=updated_object.id)  # type: ignore[attr-defined]
