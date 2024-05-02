import io
from xlsxwriter import Workbook


def create_xlsx_file(headers: dict, items: list, constant_memory: bool = False):
    output = io.BytesIO()
    with Workbook(output, options={"remove_timezone": True, 'constant_memory': constant_memory}) as workbook:
        worksheet = workbook.add_worksheet()
        worksheet.write_row(row=0, col=0, data=headers.values())
        header_keys = list(headers.keys())
        for index, item in enumerate(items):
            row = map(lambda field_id: item.get(field_id, ""), header_keys)
            worksheet.write_row(row=index + 1, col=0, data=row)

        worksheet.autofit()

    return output
