from datetime import datetime
from typing import Optional, Type, TypeVar

from app.database import query_manager

T = TypeVar("T")


class ObjectRepository:
    @classmethod
    def insert_single_object(cls, object_to_be_inserted: T, user_id: Optional[str] = None) -> T:
        """
        :param object_to_be_inserted:
        :return:

        """

        query_manager.insert_single_object(object_to_be_inserted)

        return cls.get_object_by_id(
            model=type(object_to_be_inserted), object_id=object_to_be_inserted.id  # type: ignore
        )

    @classmethod
    def get_object_by_id(cls, model: Type[T], object_id: str) -> T:
        return query_manager.query_by_id(model=model, object_id=object_id)

    @classmethod
    def update_single_object(cls, object_to_be_updated: T, user_id: Optional[str] = None) -> T:
        """
        :param object_to_be_updated:
        :param user_id:
        :return:

        updates the object with same ID in database and returns the updated object
        """

        if hasattr(object_to_be_updated, "updated_at"):
            current_time: datetime = datetime.now()
            setattr(object_to_be_updated, "updated_at", current_time)

        return query_manager.update_single_object(type(object_to_be_updated), object_to_be_updated)
