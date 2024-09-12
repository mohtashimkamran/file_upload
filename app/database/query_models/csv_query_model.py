from dataclasses import dataclass
from typing import List, Optional
from dataclasses_json import LetterCase, Undefined, dataclass_json


@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.CAMEL)
@dataclass
class CreateCsvQueryModel:
    csv_file: bytes


@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.CAMEL)
@dataclass
class CsvPollingResponse:
    count_rows: int
    count_rows_inserted: int
