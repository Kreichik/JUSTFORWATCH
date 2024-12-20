import requests
from config import TOKEN
import json


def process_data(data):
    not_submitted_students = []

    for item in data:
        lesson_progress = item.get("lessonProgress", {})
        homework_result = lesson_progress.get("homeworkResult")
        profile_view = item.get("profileView", {})

        if homework_result is None:
            student_id = profile_view.get("id", "Unknown ID")
            first_name = profile_view.get("firstName", "Unknown")
            last_name = profile_view.get("lastName", "Unknown")
            not_submitted_students.append({
                "id": student_id,
                "name": f"{first_name} {last_name}"
            })

    return not_submitted_students


def get_total_objects(url):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        if isinstance(data, list):
            return process_data(data)
        else:
            print("Unexpected data format.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []


def fetch_and_choose_lesson(limit=10):
    # URL и заголовки запроса
    url = "https://api.eduser.app/course-service/group/progress/group/98/lessons"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru",
        "Authorization": f"Bearer {TOKEN}",
        "Connection": "keep-alive",
        "Host": "api.eduser.app",
        "Origin": "https://admin.eduser.app",
        "Referer": "https://admin.eduser.app/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
    }

    try:
        # Отправка GET-запроса
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Обработка ответа
        lessons = response.json()

        # Ограничение количества выводимых записей
        print("Доступные уроки:")
        for lesson in lessons[:limit]:
            print(f"ID: {lesson['id']}, Название: {lesson['title']}")

        # Запрос ID у пользователя
        selected_id = input("Введите ID выбранного урока: ")
        return selected_id

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    except json.JSONDecodeError:
        print("Ошибка при обработке ответа: некорректный JSON.")
        return None


print("Scanning...\n")
choose_id = fetch_and_choose_lesson()

url = f"https://api.eduser.app/course-service/group/98/progress/lesson/{choose_id}"


# not_submitted_students = get_total_objects(url)
#
# print("\n\nStudents who did not submit homework:\n\n")
# for student in not_submitted_students:
#     print(f"{student['name']}")


def get_students_to_grade(url):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        students_to_grade = []

        for item in data:
            lesson_progress = item.get("lessonProgress", {})
            homework_result = lesson_progress.get("homeworkResult")

            if homework_result:
                applied_homework = homework_result.get("appliedHomework", {})
                if applied_homework.get("status") == "ON_MODERATION":
                    profile_view = item.get("profileView", {})
                    student_id = profile_view.get("id", "Unknown ID")
                    first_name = profile_view.get("firstName", "Unknown")
                    last_name = profile_view.get("lastName", "Unknown")
                    students_to_grade.append({
                        "id": student_id,
                        "name": f"{first_name} {last_name}",
                        "homeworkId": applied_homework.get("homeworkId")
                    })

        return students_to_grade

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []


def grade_homework(student_id, homework_id):
    url = "https://api.eduser.app/course-service/applied-homework/make-decision"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Origin": "https://admin.eduser.app",
        "Referer": "https://admin.eduser.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    payload = {
        "profileId": student_id,
        "homeworkId": homework_id,
        "homeworkStatus": "APPROVED",
        "score": "100"
    }

    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Successfully graded student {student_id} with 100 points.")
    else:
        print(f"Failed to grade student {student_id}: {response.status_code}, {response.text}")


def get_students_with_test_results(data):
    students_with_results = []
    for item in data:
        profile_view = item.get("profileView", {})
        lesson_progress = item.get("lessonProgress", {})
        test_results = lesson_progress.get("testResultResponseList", [])

        first_name = profile_view.get("firstName", "Unknown")
        last_name = profile_view.get("lastName", "Unknown")

        if test_results:
            score = test_results[0].get("score", 0)
            adjusted_score = score + 10
            students_with_results.append(f"{first_name} {last_name}: {adjusted_score}")
        else:
            students_with_results.append(f"{first_name} {last_name}: НЕТ")

    return students_with_results


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
            return get_students_with_test_results(data)
        else:
            print("Unexpected data format.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []


# students_to_grade = get_students_to_grade(url)
#
# if not students_to_grade:
#     print("No students to grade.")
# else:
#     print("Students with ungraded homework:")
#     for student in students_to_grade:
#         print(f"ID: {student['id']}, Name: {student['name']}")
#
#     selected_ids = input("Enter the IDs of students to grade, separated by commas: ").split(",")
#
#     for student in students_to_grade:
#         if str(student['id']) in selected_ids:
#             grade_homework(student['id'], student['homeworkId'])
students_results = fetch_students(url)

print("\nРезультаты тестов студентов:")
for student in students_results:
    print(student)
