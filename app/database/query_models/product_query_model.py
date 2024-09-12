from dataclasses import dataclass
from typing import List, Optional
from dataclasses_json import LetterCase, Undefined, dataclass_json


@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.CAMEL)
@dataclass
class CreateProductQueryModel:
    s_no: str
    csv_file_id: str
    product_name: str
    input_image_urls: List[str]
    output_image_urls: List[str]
