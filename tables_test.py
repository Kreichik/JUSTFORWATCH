import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import requests
from config import TOKEN
import json

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("massive-folder-433918-f8-b8bc5efe3d8d.json", scope)
client = gspread.authorize(credentials)

spreadsheet = client.open("ИНФО 29 ағым | Бақдәулет")
worksheet = spreadsheet.worksheet("#1,2 апта")
spreadsheet_id = spreadsheet.id
sheet_id = worksheet.id

range_in_table = 'F2:F26'
lesson_id = "1442"


def get_students_results(data):
    students_results = []
    for item in data:
        profile_view = item.get("profileView", {})
        lesson_progress = item.get("lessonProgress", {})
        test_results = lesson_progress.get("testResultResponseList", [])
        homework_result = lesson_progress.get("homeworkResult")

        first_name = profile_view.get("firstName", "Unknown")
        last_name = profile_view.get("lastName", "Unknown")

        if test_results:
            test_score = test_results[0].get("score", 0)
            if homework_result:
                final_result = test_score + 10
            else:
                final_result = f"{test_score} + дз"
        else:

            if homework_result:
                final_result = f"{10} + тест"
            else:
                final_result = "0"

        students_results.append(f"{first_name} {last_name}: {final_result}")

    return students_results


def fetch_students(url):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return get_students_results(data)
        else:
            print("Unexpected data format.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []


#
# marks = [95, 87, 76, 88, 92, 85, 78, 84, 90, 89, 73, 77, 91, 86, 80, 82, 94, 75, 88, 93, 79]
#
#
#
# # Преобразование списка в формат списка списков для API
# values = [[mark] for mark in marks]
#
# # Обновление диапазона F2:F22
# worksheet.update(range_name="F2:F22", values=values)

print("Значения успешно записаны в F2:F22!")
url = f"https://api.eduser.app/course-service/group/98/progress/lesson/{lesson_id}"

students_results = fetch_students(url)

print("\nРезультаты тестов студентов:")
for student in students_results:
    print(student)

print(students_results)

# Парсинг списка результатов: разбиваем на ключи (слова) и значения с учётом регистра
results_dict = {}
for item in students_results:
    full_name, result = item.split(":")
    words = full_name.lower().split()  # Разбиваем ФИО на слова и переводим их в нижний регистр
    for word in words:
        results_dict[word.strip()] = result.strip()

# Чтение ФИО из второго столбца (B2:B22)
names = worksheet.get("B2:B22")  # Чтение диапазона с именами

# Подготовка значений для вставки в F2:F22
values_to_update = []

for row in names:
    if row:  # Проверка на пустую строку
        full_name = row[0]  # Получаем значение ячейки (полное ФИО)
        words_in_cell = full_name.lower().split()  # Разбиваем на слова и переводим в нижний регистр
        result = ""
        # Проверка на совпадение хотя бы одного слова
        for word in words_in_cell:
            if word.strip() in results_dict:
                result = results_dict[word.strip()]
                break  # Если нашли совпадение, выходим из цикла
    else:
        result = ""  # Если ячейка пустая, оставляем пустым
    values_to_update.append([result])

# Обновление значений в F2:F22
worksheet.update(range_name=range_in_table, values=values_to_update)

print("Результаты успешно вставлены!")

results = worksheet.get(range_in_table)

# Формируем запрос для изменения цвета ячеек на белый
requests = []
for i in range(1, 22):  # Строки F2:F22
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": i,
                "endRowIndex": i + 1,
                "startColumnIndex": 5,  # F - 6-й столбец (индекс 5)
                "endColumnIndex": 6
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {
                        "red": 1.0,  # Белый цвет
                        "green": 1.0,
                        "blue": 1.0
                    }
                }
            },
            "fields": "userEnteredFormat.backgroundColor"
        }
    })

# Определяем индексы строк, где результат == "0"
rows_to_color = []
start_row_index = 1  # Строки нумеруются с 0, F2 = 2 строка → индекс = 1

for i, row in enumerate(results):
    if row and row[0].strip() == "0":  # Проверка на "0"
        rows_to_color.append(start_row_index + i)  # Добавляем индекс строки

# Формируем запрос для изменения цвета на #f4cccc для ячеек с "0"
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
    print("Цвет ячеек успешно изменён: '0' — #f4cccc, остальные — белый.")
else:
    print("Результатов с '0' не найдено.")
