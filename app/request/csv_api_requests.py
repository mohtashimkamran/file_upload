from flask_restx import Namespace, reqparse
from werkzeug.datastructures import FileStorage


class CsvApiRequests:
    @classmethod
    def get_upload_csv_request_parser(cls, namespace: Namespace):
        # Create a request parser to handle file uploads
        parser = namespace.parser()
        parser.add_argument(
            "csv",
            type=FileStorage,  # Accept file uploads using FileStorage
            location="files",  # Specifies the file will be part of 'files' in a multipart request
            required=True,
            help="CSV file to upload",
        )
        return parser
