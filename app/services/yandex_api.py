import io
from datetime import datetime, timedelta

import xlsxwriter

from app.core.base_storage import BaseStorageClient
from app.core.config import settings
from app.core.constants import (
    CELL_FORMAT,
    HEADER_FORMAT,
    SECONDS_IN_HOUR,
    SECONDS_IN_MINUTE,
    TITLE_FORMAT,
    TOTAL_FORMAT,
)
from app.models.charity_project import CharityProject


def format_time_delta(delta: timedelta) -> str:
    """Форматирует timedelta в читаемый вид."""
    days = delta.days
    hours = delta.seconds // SECONDS_IN_HOUR
    if days > 0:
        return f'{days} дн. {hours} ч.'
    minutes = (delta.seconds % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
    projects: list[CharityProject],
    storage_client: BaseStorageClient,
) -> str:
    """Создает Excel-отчёт с проектами и возвращает публичную ссылку."""
    now_date_time = datetime.now().strftime(settings.report_format)
    file_name = f'report_{now_date_time}'

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Отчет')

    title_format = workbook.add_format(TITLE_FORMAT)
    header_format = workbook.add_format(HEADER_FORMAT)
    cell_format = workbook.add_format(CELL_FORMAT)
    total_format = workbook.add_format(TOTAL_FORMAT)

    worksheet.write(0, 0, f'Отчет от {now_date_time}', title_format)

    headers = ['Название проекта', 'Время сбора', 'Описание']
    for col, header in enumerate(headers):
        worksheet.write(1, col, header, header_format)

    for row, project in enumerate(projects, start=2):
        time_delta = project.close_date - project.create_date
        time_str = format_time_delta(time_delta)
        worksheet.write(row, 0, project.name, cell_format)
        worksheet.write(row, 1, time_str, cell_format)
        worksheet.write(row, 2, project.description, cell_format)

    len_projects = len(projects)
    worksheet.write(
        len_projects + 2, 0, f'Всего проектов: {len_projects}', total_format
    )
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 50)
    workbook.close()
    output.seek(0)

    upload_url, file_path = await storage_client.create_excel_file(file_name)
    await storage_client.upload_file(upload_url, output.getvalue())
    return await storage_client.publish_file(file_path)
