import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

# Настройка доступа
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "massive-folder-433918-f8-b8bc5efe3d8d.json", scope)
gc = gspread.authorize(credentials)

# Открытие Google Таблицы
spreadsheet = gc.open("ИНФО 29 ағым | Бақдәулет")  # Название вашей таблицы
sheet = spreadsheet.worksheet("#1,2 апта")  # Лист, на котором будем работать

# Получаем ID таблицы и листа
spreadsheet_id = spreadsheet.id
sheet_id = sheet.id

# Получение данных из столбца F2:F22
results = sheet.get("F2:F22")

# Определяем индексы строк, где результат == "НЕТ"
rows_to_color = []
start_row_index = 1  # Строки нумеруются с 0, F2 = 2 строка → индекс = 1

for i, row in enumerate(results):
    if row and row[0].strip().upper() == "НЕТ":  # Проверка на "НЕТ" (регистр не важен)
        rows_to_color.append(start_row_index + i)  # Добавляем индекс строки

# Формируем запрос для изменения цвета ячеек
requests = []
for row_index in rows_to_color:
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row_index,
                "endRowIndex": row_index + 1,
                "startColumnIndex": 5,  # F - 6-й столбец (индекс 5)
                "endColumnIndex": 6
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 0.956,  # Значение для #f4cccc
                        "green": 0.8,
                        "blue": 0.8
                    }
                }
            },
            "fields": "userEnteredFormat.backgroundColor"
        }
    })

# Отправка запроса на изменение формата
if requests:
    service = build('sheets', 'v4', credentials=credentials)
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()
    print("Цвет ячеек успешно изменён для тех, у кого результат 'НЕТ'.")
else:
    print("Результатов с 'НЕТ' не найдено.")
