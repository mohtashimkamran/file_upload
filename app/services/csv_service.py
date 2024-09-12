import csv
from io import StringIO
import io
import time
from typing import List
from werkzeug.datastructures import FileStorage
from app.database import query_manager
from app.database.models.csv_model import CsvModel
from app.database.models.product import ProductModel
from app.database.query_models.csv_query_model import CreateCsvQueryModel, CsvPollingResponse
from app.database.query_models.product_query_model import CreateProductQueryModel
from app.database.repository.object_repository import ObjectRepository
import threading


class CsvService:
    @classmethod
    def handle_csv(cls, csv_file: FileStorage) -> CsvModel:
        """
        As we get the csv_file from the api
        we quickly store the file as a blob in db and return the id of the row
        Asynchronously we create a new thread to process the csv file and once
        the file is processed we mark the column is_processed as true
        """
        inserted_csv: CsvModel = cls.insert_csv_to_db(csv_file=csv_file)
        thread = threading.Thread(target=CsvUploadService.process_csv_files, args=(inserted_csv,))
        thread.start()
        return inserted_csv

    @classmethod
    def insert_csv_to_db(cls, csv_file: FileStorage) -> CsvModel:
        """
        this function takes in csv_file and reads the content and inserts it in db
        """
        csv_file_content = csv_file.read()
        create_csv_request_model: CreateCsvQueryModel = CreateCsvQueryModel(
            csv_file=csv_file_content
        )
        csv_file_model: CsvModel = CsvModel(create_csv_request_model=create_csv_request_model)
        return ObjectRepository.insert_single_object(object_to_be_inserted=csv_file_model)


class CsvUploadService:
    @classmethod
    def process_csv_files(cls, csv_model: CsvModel):
        """
        we pull up all unprocessed files and start inserting data from them
        """
        unprocessed_csv_files: List[CsvModel] = query_manager.query_with_filter(
            model=CsvModel, filters=(CsvModel.is_processed.is_(False))
        )
        for csv_record in unprocessed_csv_files:
            csv_data: List[List[str]] = cls.get_csv_data_from_csv_model(csv_model=csv_record)
            cls.create_products_from_csv(csv_data=csv_data, csv_file_id=csv_model.id)

            # once all the products are inserted into the db we update in csv model the row as is_processed=True
            csv_model.is_processed = True
            ObjectRepository.update_single_object(object_to_be_updated=csv_model)

    @classmethod
    def create_products_from_csv(cls, csv_data: List[List[str]], csv_file_id: str) -> None:
        """
        this function takes in list of all rows in csv and creates product out of it
        """
        for row in csv_data[1:]:
            cls.create_single_product(
                csv_row=row,
                csv_file_id=csv_file_id,
            )
            time.sleep(10)

    @classmethod
    def create_single_product(cls, csv_row: List[str], csv_file_id: str) -> ProductModel:
        """
        inserts single product to db
        """
        create_product_query_model: CreateProductQueryModel = CreateProductQueryModel(
            s_no=csv_row[0],
            csv_file_id=csv_file_id,
            product_name=csv_row[1],
            input_image_urls=csv_row[2:],
            output_image_urls=cls.add_image_to_cloud(image_urls=csv_row[2:]),
        )
        product: ProductModel = ProductModel(
            create_product_request_model=create_product_query_model
        )

        return ObjectRepository.insert_single_object(object_to_be_inserted=product)

    @classmethod
    def add_image_to_cloud(cls, image_urls: List[str]) -> List[str]:
        """
        this function is basically a dummy function but its purpose is to upload image to cloud and return its url
        """

        return [image_url + "output" for image_url in image_urls]

    @classmethod
    def get_csv_data_from_csv_model(cls, csv_model: CsvModel) -> List[List[str]]:
        csv_content = csv_model.csv_file
        decoded_content = csv_content.decode("utf-8").splitlines()
        csv_reader = csv.reader(decoded_content)
        csv_data = [row for row in csv_reader]
        return csv_data


class CsvPollService:
    @classmethod
    def get_csv_file_upload_status(cls, csv_file_id: str) -> CsvPollingResponse:
        csv_file_model: CsvModel = ObjectRepository.get_object_by_id(
            model=CsvModel, object_id=csv_file_id
        )
        csv_rows: List[List[str]] = CsvUploadService.get_csv_data_from_csv_model(
            csv_model=csv_file_model
        )
        products_inserted: List[ProductModel] = query_manager.query_with_filter(
            model=ProductModel, filters=ProductModel.csv_file_id == csv_file_id
        )

        return CsvPollingResponse(
            count_rows=len(csv_rows) - 1, count_rows_inserted=len(products_inserted)
        )


class CsvDownloadService:
    @classmethod
    def download_uploaded_csv(cls, csv_file_id: str) -> None:
        products_inserted: List[ProductModel] = query_manager.query_with_filter(
            model=ProductModel, filters=ProductModel.csv_file_id == csv_file_id
        )
        csv_data = cls.convert_products_to_csv(products=products_inserted)
        return csv_data

    @classmethod
    def convert_products_to_csv(cls, products: List[ProductModel]):
        """
        Converts a list of ProductModel instances into a CSV string.
        """
        headers = [
            "PRODUCT_SL_NO",
            "PRODUCT_NAME",
            "INPUT_PRODUCT_IMAGE_URLS",
            "OUTPUT_PRODUCT_IMAGE_URLS",
        ]

        csv_output = StringIO()
        csv_writer = csv.DictWriter(csv_output, fieldnames=headers)

        csv_writer.writeheader()
        for product in products:
            csv_writer.writerow(
                {
                    "PRODUCT_SL_NO": product.s_no,
                    "PRODUCT_NAME": product.product_name,
                    "INPUT_PRODUCT_IMAGE_URLS": (
                        ", ".join(product.input_image_urls) if product.input_image_urls else ""
                    ),
                    "OUTPUT_PRODUCT_IMAGE_URLS": (
                        ", ".join(product.output_image_urls) if product.output_image_urls else ""
                    ),
                }
            )

        output = io.BytesIO()
        output.write(csv_output.getvalue().encode("utf-8"))
        output.seek(0)  # Reset pointer to the beginning of the stream
        return output
