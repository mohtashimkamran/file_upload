import csv
from dataclasses import asdict
import io
from flask_restx import Namespace, Resource
from app.database.models.csv_model import CsvModel
from app.database.query_models.csv_query_model import CsvPollingResponse
from app.request.csv_api_requests import CsvApiRequests
from app.services.csv_service import CsvDownloadService, CsvPollService, CsvService
from flask import send_file

csv_api_ns = Namespace("csv", description="APIs for handling csv")


@csv_api_ns.route("")
class CsvApiUpload(Resource):
    upload_csv_parser = CsvApiRequests.get_upload_csv_request_parser(namespace=csv_api_ns)

    @csv_api_ns.expect(upload_csv_parser)  # Expect file upload via parser
    def post(self):
        # Parse the incoming request to get the file
        args = self.upload_csv_parser.parse_args()
        csv_file = args["csv"]  # This is a FileStorage object
        if csv_file:
            inserted_csv: CsvModel = CsvService.handle_csv(csv_file=csv_file)
            return {"message": "File uploaded successfully", "fileId": inserted_csv.id}, 201

        return {"message": "No file uploaded"}, 400


@csv_api_ns.route("/<csv_file_id>")
class CsvApiPoll(Resource):
    def get(self, csv_file_id: str):
        # Parse the incoming request to get the file
        polling_status: CsvPollingResponse = CsvPollService.get_csv_file_upload_status(
            csv_file_id=csv_file_id
        )

        return {"data": asdict(polling_status)}, 200


@csv_api_ns.route("download/<csv_file_id>")
class CsvDownload(Resource):
    def get(self, csv_file_id: str):
        result = CsvDownloadService.download_uploaded_csv(csv_file_id=csv_file_id)
        return send_file(
            path_or_file=result, as_attachment=True, download_name="output.csv", mimetype="text/csv"
        )
