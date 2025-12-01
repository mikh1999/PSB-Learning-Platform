"""
Скрипт для наполнения базы данных тестовыми данными.
Создает 30+ курсов, уроки, задания, ответы, комментарии и оценки.
"""
import asyncio
import random
from datetime import datetime, timedelta
from passlib.context import CryptContext
import asyncpg

# Настройки подключения к продакшн БД
DB_CONFIG = {
    "host": "194.87.74.244",
    "port": 5432,
    "database": "psb_db",
    "user": "psb_admin",
    "password": "K9tZrW7!eN4uJa5sf3vLp@8yHdG2Rxb",
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Данные для генерации
COURSE_TOPICS = [
    "Python для начинающих", "Продвинутый Python", "Веб-разработка на Django",
    "FastAPI: современные API", "Машинное обучение", "Data Science",
    "Алгоритмы и структуры данных", "Базы данных SQL", "NoSQL и MongoDB",
    "Docker и контейнеризация", "Kubernetes", "CI/CD практики",
    "Git и командная работа", "Linux для разработчиков", "Сети и протоколы",
    "JavaScript основы", "React.js", "Vue.js", "Node.js", "TypeScript",
    "HTML и CSS", "Адаптивный дизайн", "UX/UI основы", "Figma для разработчиков",
    "Тестирование ПО", "Автоматизация тестирования", "Selenium и Playwright",
    "Кибербезопасность", "Криптография", "Блокчейн разработка",
    "Мобильная разработка Flutter", "React Native", "Swift для iOS",
    "Kotlin для Android", "C++ для игр", "Unity разработка",
    "Unreal Engine", "3D моделирование", "Компьютерное зрение",
    "NLP и обработка текста"
]

LESSON_TYPES = ["VIDEO", "TEXT", "FILE"]

ASSIGNMENT_TEMPLATES = [
    "Практическое задание: {topic}",
    "Лабораторная работа: {topic}",
    "Тест по теме: {topic}",
    "Проект: {topic}",
    "Контрольная работа: {topic}",
    "Домашнее задание: {topic}",
    "Самостоятельная работа: {topic}",
    "Кейс-стади: {topic}",
    "Групповой проект: {topic}",
    "Финальный проект: {topic}",
]

FIRST_NAMES = ["Александр", "Мария", "Иван", "Елена", "Дмитрий", "Анна", "Сергей", "Ольга",
               "Андрей", "Наталья", "Михаил", "Екатерина", "Алексей", "Татьяна", "Николай"]
LAST_NAMES = ["Иванов", "Петров", "Сидоров", "Козлов", "Новиков", "Морозов", "Волков",
              "Соколов", "Попов", "Лебедев", "Кузнецов", "Смирнов", "Федоров", "Орлов"]

COMMENT_TEMPLATES = [
    "Хорошая работа! Но есть несколько замечаний.",
    "Отлично выполнено задание!",
    "Нужно доработать раздел о {topic}.",
    "Пожалуйста, исправьте ошибки в коде.",
    "Молодец! Так держать!",
    "Спасибо за работу. Есть вопросы по реализации.",
    "Необходимо добавить комментарии к коду.",
    "Работа принята. Оценка выставлена.",
    "Пересмотрите алгоритм решения.",
    "Хороший подход к решению задачи!",
]

STUDENT_COMMENTS = [
    "Спасибо за обратную связь!",
    "Исправил указанные замечания.",
    "Можно уточнить, что именно нужно доработать?",
    "Готово, проверьте пожалуйста.",
    "Добавил комментарии к коду.",
    "Переделал раздел согласно замечаниям.",
]


async def seed_database():
    print("Подключение к базе данных...")
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        # Очистка существующих данных (опционально)
        print("Очистка существующих тестовых данных...")
        await conn.execute("DELETE FROM submission_comments WHERE TRUE")
        await conn.execute("DELETE FROM grades WHERE TRUE")
        await conn.execute("DELETE FROM submissions WHERE TRUE")
        await conn.execute("DELETE FROM assignments WHERE TRUE")
        await conn.execute("DELETE FROM lesson_progress WHERE TRUE")
        await conn.execute("DELETE FROM lessons WHERE TRUE")
        await conn.execute("DELETE FROM enrollments WHERE TRUE")
        await conn.execute("DELETE FROM courses WHERE TRUE")
        await conn.execute("DELETE FROM users WHERE email LIKE '%@test.edu'")

        # 1. Создание преподавателей
        print("Создание преподавателей...")
        teachers = []
        for i in range(5):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = f"teacher{i+1}@test.edu"
            hashed_password = pwd_context.hash("password123")

            teacher_id = await conn.fetchval("""
                INSERT INTO users (email, hashed_password, first_name, last_name, role, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, 'TEACHER', true, NOW(), NOW())
                RETURNING id
            """, email, hashed_password, first_name, last_name)
            teachers.append(teacher_id)
            print(f"  Преподаватель: {first_name} {last_name} ({email})")

        # 2. Создание студентов
        print("Создание студентов...")
        students = []
        for i in range(50):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = f"student{i+1}@test.edu"
            hashed_password = pwd_context.hash("password123")

            student_id = await conn.fetchval("""
                INSERT INTO users (email, hashed_password, first_name, last_name, role, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, 'STUDENT', true, NOW(), NOW())
                RETURNING id
            """, email, hashed_password, first_name, last_name)
            students.append(student_id)
        print(f"  Создано {len(students)} студентов")

        # 3. Создание курсов
        print("Создание курсов...")
        courses = []
        for i, topic in enumerate(COURSE_TOPICS[:35]):  # 35 курсов
            teacher_id = random.choice(teachers)
            status = random.choice(["DRAFT", "PUBLISHED", "PUBLISHED", "PUBLISHED"])  # Больше опубликованных

            course_id = await conn.fetchval("""
                INSERT INTO courses (title, description, teacher_id, status, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
                RETURNING id
            """, topic, f"Полный курс по теме: {topic}. Включает теорию и практику.", teacher_id, status)
            courses.append({"id": course_id, "title": topic, "teacher_id": teacher_id})
            print(f"  Курс: {topic}")

        # 4. Создание уроков и заданий для каждого курса
        print("Создание уроков и заданий...")
        all_assignments = []

        for course in courses:
            num_lessons = random.randint(8, 15)

            for lesson_num in range(1, num_lessons + 1):
                lesson_type = random.choice(LESSON_TYPES)
                lesson_title = f"Урок {lesson_num}: {course['title']} - часть {lesson_num}"

                # Определяем file_url в зависимости от типа урока
                if lesson_type == "VIDEO":
                    file_url = f"/uploads/lessons/course_{course['id']}/lesson_{lesson_num}.mp4"
                elif lesson_type == "FILE":
                    file_url = f"/uploads/lessons/course_{course['id']}/lesson_{lesson_num}.pdf"
                else:
                    file_url = None

                lesson_id = await conn.fetchval("""
                    INSERT INTO lessons (course_id, title, content, type, file_url, "order", created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                    RETURNING id
                """, course["id"], lesson_title,
                    f"Содержание урока {lesson_num} курса {course['title']}",
                    lesson_type,
                    file_url,
                    lesson_num)

                # Создаем 1-2 задания на урок (всего ~10-15 на курс)
                num_assignments = 1 if lesson_num > 8 else random.randint(1, 2)

                for assign_num in range(num_assignments):
                    template = random.choice(ASSIGNMENT_TEMPLATES)
                    assign_title = template.format(topic=f"урок {lesson_num}")
                    max_score = random.choice([10, 20, 50, 100])

                    assignment_id = await conn.fetchval("""
                        INSERT INTO assignments (lesson_id, title, description, max_score, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, NOW(), NOW())
                        RETURNING id
                    """, lesson_id, assign_title,
                        f"Выполните задание по материалам урока {lesson_num}. Максимальный балл: {max_score}",
                        max_score)

                    all_assignments.append({
                        "id": assignment_id,
                        "course_id": course["id"],
                        "teacher_id": course["teacher_id"],
                        "max_score": max_score
                    })

        print(f"  Создано {len(all_assignments)} заданий")

        # 5. Записываем студентов на курсы
        print("Запись студентов на курсы...")
        enrollments = []
        for student_id in students:
            # Каждый студент записан на 3-8 курсов
            num_courses = random.randint(3, 8)
            enrolled_courses = random.sample(courses, min(num_courses, len(courses)))

            for course in enrolled_courses:
                progress = random.randint(0, 100)
                await conn.execute("""
                    INSERT INTO enrollments (student_id, course_id, progress, enrolled_at, created_at, updated_at)
                    VALUES ($1, $2, $3, NOW(), NOW(), NOW())
                    ON CONFLICT DO NOTHING
                """, student_id, course["id"], progress)
                enrollments.append({"student_id": student_id, "course_id": course["id"]})

        print(f"  Создано {len(enrollments)} записей на курсы")

        # 6. Создание ответов на задания
        print("Создание ответов студентов...")
        submissions = []
        statuses = ["SUBMITTED", "SUBMITTED", "GRADED", "GRADED", "GRADED", "RETURNED"]

        for enrollment in enrollments:
            # Получаем задания курса
            course_assignments = [a for a in all_assignments if a["course_id"] == enrollment["course_id"]]

            # Студент выполняет 50-80% заданий курса
            num_submissions = int(len(course_assignments) * random.uniform(0.5, 0.8))
            assignments_to_submit = random.sample(course_assignments, min(num_submissions, len(course_assignments)))

            for assignment in assignments_to_submit:
                status = random.choice(statuses)
                submitted_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))

                submission_id = await conn.fetchval("""
                    INSERT INTO submissions (assignment_id, student_id, content, status, submitted_at, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                    RETURNING id
                """, assignment["id"], enrollment["student_id"],
                    "Мой ответ на задание. Код и пояснения приложены.",
                    status, submitted_at)

                submissions.append({
                    "id": submission_id,
                    "assignment_id": assignment["id"],
                    "student_id": enrollment["student_id"],
                    "teacher_id": assignment["teacher_id"],
                    "max_score": assignment["max_score"],
                    "status": status
                })

        print(f"  Создано {len(submissions)} ответов")

        # 7. Создание оценок для проверенных работ
        print("Создание оценок...")
        grades_count = 0
        for submission in submissions:
            if submission["status"] == "GRADED":
                score = random.randint(int(submission["max_score"] * 0.5), submission["max_score"])

                await conn.execute("""
                    INSERT INTO grades (submission_id, graded_by, score, comment, graded_at, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, NOW(), NOW(), NOW())
                """, submission["id"], submission["teacher_id"], score,
                    random.choice(COMMENT_TEMPLATES).format(topic="данной теме"))
                grades_count += 1

        print(f"  Создано {grades_count} оценок")

        # 8. Создание комментариев к работам
        print("Создание комментариев (чат)...")
        comments_count = 0
        for submission in submissions:
            # 30% работ имеют комментарии
            if random.random() < 0.3:
                num_comments = random.randint(2, 6)

                for i in range(num_comments):
                    # Чередуем комментарии преподавателя и студента
                    if i % 2 == 0:
                        user_id = submission["teacher_id"]
                        content = random.choice(COMMENT_TEMPLATES).format(topic="этой теме")
                    else:
                        user_id = submission["student_id"]
                        content = random.choice(STUDENT_COMMENTS)

                    created_at = datetime.utcnow() - timedelta(days=random.randint(1, 20), hours=random.randint(0, 23))

                    await conn.execute("""
                        INSERT INTO submission_comments (submission_id, user_id, content, created_at)
                        VALUES ($1, $2, $3, $4)
                    """, submission["id"], user_id, content, created_at)
                    comments_count += 1

        print(f"  Создано {comments_count} комментариев")

        # Итоги
        print("\n" + "="*50)
        print("ГОТОВО! Статистика:")
        print(f"  Преподавателей: {len(teachers)}")
        print(f"  Студентов: {len(students)}")
        print(f"  Курсов: {len(courses)}")
        print(f"  Заданий: {len(all_assignments)}")
        print(f"  Записей на курсы: {len(enrollments)}")
        print(f"  Ответов студентов: {len(submissions)}")
        print(f"  Оценок: {grades_count}")
        print(f"  Комментариев: {comments_count}")
        print("="*50)
        print("\nДанные для входа:")
        print("  Преподаватель: teacher1@test.edu / password123")
        print("  Студент: student1@test.edu / password123")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
