import requests
from config import TOKEN


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


url = "https://api.eduser.app/course-service/group/98/progress/lesson/1442"
students_to_grade = get_students_to_grade(url)

if not students_to_grade:
    print("No students to grade.")
else:
    print("Students with ungraded homework:")
    for student in students_to_grade:
        print(f"ID: {student['id']}, Name: {student['name']}")

    selected_ids = input("Enter the IDs of students to grade, separated by commas: ").split(",")

    for student in students_to_grade:
        if str(student['id']) in selected_ids:
            grade_homework(student['id'], student['homeworkId'])
