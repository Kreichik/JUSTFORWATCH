import requests
from config import TOKEN


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


url = "https://api.eduser.app/course-service/group/98/progress/lesson/1442"
not_submitted_students = get_total_objects(url)

print("Students who did not submit homework:")
for student in not_submitted_students:
    print(f"{student['name']}")
