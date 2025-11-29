-- PSB Learning Platform - Тестовые данные
-- Пароль для всех пользователей: password123

-- ============================================
-- ОЧИСТКА ДАННЫХ (в правильном порядке)
-- ============================================
TRUNCATE TABLE lesson_progress CASCADE;
TRUNCATE TABLE grades CASCADE;
TRUNCATE TABLE submissions CASCADE;
TRUNCATE TABLE assignments CASCADE;
TRUNCATE TABLE lessons CASCADE;
TRUNCATE TABLE enrollments CASCADE;
TRUNCATE TABLE courses CASCADE;
TRUNCATE TABLE users CASCADE;

-- Сброс sequences
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE courses_id_seq RESTART WITH 1;
ALTER SEQUENCE lessons_id_seq RESTART WITH 1;
ALTER SEQUENCE assignments_id_seq RESTART WITH 1;
ALTER SEQUENCE submissions_id_seq RESTART WITH 1;
ALTER SEQUENCE grades_id_seq RESTART WITH 1;
ALTER SEQUENCE enrollments_id_seq RESTART WITH 1;
ALTER SEQUENCE lesson_progress_id_seq RESTART WITH 1;

-- ============================================
-- ПОЛЬЗОВАТЕЛИ
-- ============================================
-- Пароль: password123 (bcrypt hash)
-- $2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW

INSERT INTO users (email, hashed_password, first_name, last_name, role, is_active, created_at, updated_at) VALUES
-- Администратор (пароль: admin123)
('admin@psb.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Админ', 'Системы', 'ADMIN', true, NOW(), NOW()),

-- Преподаватели
('ivanov@university.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Иван', 'Иванов', 'TEACHER', true, NOW(), NOW()),
('petrova@university.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Мария', 'Петрова', 'TEACHER', true, NOW(), NOW()),
('sidorov@university.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Алексей', 'Сидоров', 'TEACHER', true, NOW(), NOW()),

-- Студенты
('student1@mail.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Анна', 'Смирнова', 'STUDENT', true, NOW(), NOW()),
('student2@mail.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Дмитрий', 'Козлов', 'STUDENT', true, NOW(), NOW()),
('student3@mail.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Елена', 'Новикова', 'STUDENT', true, NOW(), NOW()),
('student4@mail.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Максим', 'Морозов', 'STUDENT', true, NOW(), NOW()),
('student5@mail.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Ольга', 'Волкова', 'STUDENT', true, NOW(), NOW()),
('student6@mail.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Артём', 'Соколов', 'STUDENT', true, NOW(), NOW()),
('student7@mail.ru', '$2b$12$vxzwnBHAWYZqsRya3wckZO/YjIVe8dxx5CFJlqkTnvXoQCvK3RKSW', 'Виктория', 'Лебедева', 'STUDENT', true, NOW(), NOW());

-- ============================================
-- КУРСЫ
-- ============================================
INSERT INTO courses (title, description, teacher_id, created_at, updated_at) VALUES
('Python для начинающих', 'Основы программирования на языке Python. Изучение синтаксиса, типов данных, функций и ООП.', 1, NOW(), NOW()),
('Веб-разработка на FastAPI', 'Создание современных REST API с использованием FastAPI, SQLAlchemy и PostgreSQL.', 1, NOW(), NOW()),
('Базы данных и SQL', 'Проектирование баз данных, язык SQL, оптимизация запросов.', 2, NOW(), NOW()),
('Алгоритмы и структуры данных', 'Фундаментальные алгоритмы, сложность, деревья, графы, динамическое программирование.', 2, NOW(), NOW()),
('Machine Learning основы', 'Введение в машинное обучение: регрессия, классификация, кластеризация.', 3, NOW(), NOW());

-- ============================================
-- УРОКИ
-- ============================================
-- Курс 1: Python для начинающих
INSERT INTO lessons (course_id, title, content, "order", type, created_at, updated_at) VALUES
(1, 'Введение в Python', 'Python — это высокоуровневый язык программирования общего назначения. В этом уроке мы установим Python и напишем первую программу.', 1, 'TEXT', NOW(), NOW()),
(1, 'Переменные и типы данных', 'Изучаем основные типы данных: int, float, str, bool, list, dict, tuple.', 2, 'TEXT', NOW(), NOW()),
(1, 'Условные операторы', 'Конструкции if, elif, else. Логические операторы and, or, not.', 3, 'TEXT', NOW(), NOW()),
(1, 'Циклы for и while', 'Итерация по коллекциям, range(), break, continue.', 4, 'TEXT', NOW(), NOW()),
(1, 'Функции', 'Определение функций, аргументы, возвращаемые значения, lambda-функции.', 5, 'TEXT', NOW(), NOW()),
(1, 'ООП в Python', 'Классы, объекты, наследование, инкапсуляция, полиморфизм.', 6, 'TEXT', NOW(), NOW());

-- Курс 2: Веб-разработка на FastAPI
INSERT INTO lessons (course_id, title, content, "order", type, created_at, updated_at) VALUES
(2, 'Введение в FastAPI', 'Что такое FastAPI, установка, первое приложение Hello World.', 1, 'TEXT', NOW(), NOW()),
(2, 'Маршрутизация и параметры', 'Path parameters, query parameters, request body.', 2, 'TEXT', NOW(), NOW()),
(2, 'Pydantic модели', 'Валидация данных с помощью Pydantic, BaseModel, Field.', 3, 'TEXT', NOW(), NOW()),
(2, 'Работа с базой данных', 'SQLAlchemy, async сессии, CRUD операции.', 4, 'TEXT', NOW(), NOW()),
(2, 'Аутентификация JWT', 'JWT токены, OAuth2, защита эндпоинтов.', 5, 'TEXT', NOW(), NOW());

-- Курс 3: Базы данных и SQL
INSERT INTO lessons (course_id, title, content, "order", type, created_at, updated_at) VALUES
(3, 'Введение в реляционные БД', 'Концепции реляционных баз данных, таблицы, связи.', 1, 'TEXT', NOW(), NOW()),
(3, 'SELECT запросы', 'Выборка данных, WHERE, ORDER BY, LIMIT.', 2, 'TEXT', NOW(), NOW()),
(3, 'JOIN операции', 'INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN.', 3, 'TEXT', NOW(), NOW()),
(3, 'Агрегатные функции', 'COUNT, SUM, AVG, GROUP BY, HAVING.', 4, 'TEXT', NOW(), NOW()),
(3, 'Индексы и оптимизация', 'Создание индексов, EXPLAIN, оптимизация запросов.', 5, 'TEXT', NOW(), NOW());

-- Курс 4: Алгоритмы
INSERT INTO lessons (course_id, title, content, "order", type, created_at, updated_at) VALUES
(4, 'Сложность алгоритмов', 'Big O нотация, временная и пространственная сложность.', 1, 'TEXT', NOW(), NOW()),
(4, 'Сортировки', 'Bubble sort, Quick sort, Merge sort, их сложность.', 2, 'TEXT', NOW(), NOW()),
(4, 'Деревья', 'Бинарные деревья, BST, обходы деревьев.', 3, 'TEXT', NOW(), NOW()),
(4, 'Графы', 'Представление графов, BFS, DFS.', 4, 'TEXT', NOW(), NOW());

-- Курс 5: ML
INSERT INTO lessons (course_id, title, content, "order", type, created_at, updated_at) VALUES
(5, 'Введение в ML', 'Что такое машинное обучение, типы задач, библиотеки.', 1, 'TEXT', NOW(), NOW()),
(5, 'Линейная регрессия', 'Модель, функция потерь, градиентный спуск.', 2, 'TEXT', NOW(), NOW()),
(5, 'Классификация', 'Логистическая регрессия, метрики качества.', 3, 'TEXT', NOW(), NOW());

-- ============================================
-- ЗАДАНИЯ
-- ============================================
-- Курс 1: Python
INSERT INTO assignments (lesson_id, title, description, deadline, max_score, created_at, updated_at) VALUES
(1, 'Установка Python', 'Установите Python 3.11+ и сделайте скриншот версии в терминале.', NOW() + INTERVAL '7 days', 10, NOW(), NOW()),
(2, 'Работа с типами данных', 'Создайте программу, которая демонстрирует работу со всеми базовыми типами данных.', NOW() + INTERVAL '7 days', 20, NOW(), NOW()),
(4, 'Задачи на циклы', 'Решите 5 задач на использование циклов for и while.', NOW() + INTERVAL '14 days', 30, NOW(), NOW()),
(5, 'Калькулятор на функциях', 'Напишите калькулятор с функциями для каждой операции.', NOW() + INTERVAL '14 days', 40, NOW(), NOW()),
(6, 'ООП: Класс Student', 'Создайте класс Student с атрибутами и методами.', NOW() + INTERVAL '21 days', 50, NOW(), NOW());

-- Курс 2: FastAPI
INSERT INTO assignments (lesson_id, title, description, deadline, max_score, created_at, updated_at) VALUES
(7, 'Hello FastAPI', 'Создайте простое FastAPI приложение с 3 эндпоинтами.', NOW() + INTERVAL '7 days', 20, NOW(), NOW()),
(9, 'Pydantic схемы', 'Опишите Pydantic модели для сущностей вашего проекта.', NOW() + INTERVAL '14 days', 30, NOW(), NOW()),
(11, 'JWT авторизация', 'Реализуйте регистрацию и авторизацию с JWT.', NOW() + INTERVAL '21 days', 50, NOW(), NOW());

-- Курс 3: SQL
INSERT INTO assignments (lesson_id, title, description, deadline, max_score, created_at, updated_at) VALUES
(12, 'Проектирование БД', 'Спроектируйте схему базы данных для интернет-магазина.', NOW() + INTERVAL '7 days', 30, NOW(), NOW()),
(14, 'Сложные запросы', 'Напишите 10 SQL запросов с JOIN операциями.', NOW() + INTERVAL '14 days', 40, NOW(), NOW());

-- Курс 4: Алгоритмы
INSERT INTO assignments (lesson_id, title, description, deadline, max_score, created_at, updated_at) VALUES
(17, 'Анализ сложности', 'Определите сложность 10 алгоритмов.', NOW() + INTERVAL '7 days', 25, NOW(), NOW()),
(18, 'Реализация сортировок', 'Реализуйте 3 алгоритма сортировки на Python.', NOW() + INTERVAL '14 days', 50, NOW(), NOW());

-- Курс 5: ML
INSERT INTO assignments (lesson_id, title, description, deadline, max_score, created_at, updated_at) VALUES
(21, 'Первая модель', 'Обучите модель линейной регрессии на датасете Boston Housing.', NOW() + INTERVAL '14 days', 50, NOW(), NOW());

-- ============================================
-- ЗАПИСИ НА КУРСЫ (ENROLLMENTS)
-- ============================================
INSERT INTO enrollments (student_id, course_id, progress, enrolled_at, created_at, updated_at) VALUES
-- Студент 4 (Анна) - записана на 3 курса
(4, 1, 67, NOW() - INTERVAL '30 days', NOW(), NOW()),
(4, 2, 40, NOW() - INTERVAL '20 days', NOW(), NOW()),
(4, 3, 20, NOW() - INTERVAL '10 days', NOW(), NOW()),

-- Студент 5 (Дмитрий) - записан на 2 курса
(5, 1, 83, NOW() - INTERVAL '30 days', NOW(), NOW()),
(5, 4, 25, NOW() - INTERVAL '15 days', NOW(), NOW()),

-- Студент 6 (Елена) - записана на 3 курса
(6, 1, 100, NOW() - INTERVAL '45 days', NOW(), NOW()),
(6, 2, 60, NOW() - INTERVAL '30 days', NOW(), NOW()),
(6, 5, 33, NOW() - INTERVAL '10 days', NOW(), NOW()),

-- Студент 7 (Максим) - записан на 2 курса
(7, 3, 40, NOW() - INTERVAL '20 days', NOW(), NOW()),
(7, 4, 50, NOW() - INTERVAL '25 days', NOW(), NOW()),

-- Студент 8 (Ольга) - записана на 1 курс
(8, 1, 50, NOW() - INTERVAL '15 days', NOW(), NOW()),

-- Студент 9 (Артём) - записан на 2 курса
(9, 2, 20, NOW() - INTERVAL '10 days', NOW(), NOW()),
(9, 5, 0, NOW() - INTERVAL '5 days', NOW(), NOW()),

-- Студент 10 (Виктория) - записана на 1 курс
(10, 1, 33, NOW() - INTERVAL '7 days', NOW(), NOW());

-- ============================================
-- РАБОТЫ СТУДЕНТОВ (SUBMISSIONS)
-- ============================================
INSERT INTO submissions (assignment_id, student_id, content, file_url, status, submitted_at, created_at, updated_at) VALUES
-- Задание 1 (Установка Python)
(1, 4, 'Python 3.11.5 установлен успешно. Скриншот в приложении.', NULL, 'GRADED', NOW() - INTERVAL '25 days', NOW(), NOW()),
(1, 5, 'Установил Python 3.12.0', NULL, 'GRADED', NOW() - INTERVAL '26 days', NOW(), NOW()),
(1, 6, 'Python установлен, всё работает.', NULL, 'GRADED', NOW() - INTERVAL '40 days', NOW(), NOW()),
(1, 8, 'Готово!', NULL, 'GRADED', NOW() - INTERVAL '10 days', NOW(), NOW()),
(1, 10, 'Установка завершена.', NULL, 'SUBMITTED', NOW() - INTERVAL '3 days', NOW(), NOW()),

-- Задание 2 (Типы данных)
(2, 4, 'Программа демонстрирует int, float, str, list, dict, tuple.', NULL, 'GRADED', NOW() - INTERVAL '20 days', NOW(), NOW()),
(2, 5, 'Все типы данных продемонстрированы с примерами.', NULL, 'GRADED', NOW() - INTERVAL '22 days', NOW(), NOW()),
(2, 6, 'Полная демонстрация всех типов.', NULL, 'GRADED', NOW() - INTERVAL '35 days', NOW(), NOW()),
(2, 8, 'Работа выполнена.', NULL, 'SUBMITTED', NOW() - INTERVAL '5 days', NOW(), NOW()),

-- Задание 3 (Циклы)
(3, 4, 'Решены все 5 задач на циклы.', NULL, 'GRADED', NOW() - INTERVAL '15 days', NOW(), NOW()),
(3, 5, '5 задач решено.', NULL, 'GRADED', NOW() - INTERVAL '18 days', NOW(), NOW()),
(3, 6, 'Все задачи выполнены с комментариями.', NULL, 'GRADED', NOW() - INTERVAL '30 days', NOW(), NOW()),

-- Задание 4 (Калькулятор)
(4, 4, 'Калькулятор с функциями add, sub, mul, div.', NULL, 'SUBMITTED', NOW() - INTERVAL '5 days', NOW(), NOW()),
(4, 5, 'Калькулятор готов, добавил обработку ошибок.', NULL, 'GRADED', NOW() - INTERVAL '10 days', NOW(), NOW()),
(4, 6, 'Калькулятор с GUI на tkinter.', NULL, 'GRADED', NOW() - INTERVAL '25 days', NOW(), NOW()),

-- Задание 5 (ООП)
(5, 6, 'Класс Student с методами и наследованием.', NULL, 'GRADED', NOW() - INTERVAL '20 days', NOW(), NOW()),

-- Задание 6 (FastAPI Hello)
(6, 4, 'Три эндпоинта: GET /, GET /items, POST /items', NULL, 'GRADED', NOW() - INTERVAL '15 days', NOW(), NOW()),
(6, 6, 'FastAPI приложение с документацией.', NULL, 'GRADED', NOW() - INTERVAL '25 days', NOW(), NOW()),
(6, 9, 'Hello World на FastAPI.', NULL, 'SUBMITTED', NOW() - INTERVAL '3 days', NOW(), NOW()),

-- Задание 9 (SQL проектирование)
(9, 7, 'Схема БД интернет-магазина: users, products, orders, order_items.', NULL, 'GRADED', NOW() - INTERVAL '10 days', NOW(), NOW()),

-- Задание 12 (Анализ сложности)
(12, 5, 'Анализ 10 алгоритмов выполнен.', NULL, 'SUBMITTED', NOW() - INTERVAL '5 days', NOW(), NOW()),
(12, 7, 'Сложность определена для всех алгоритмов.', NULL, 'GRADED', NOW() - INTERVAL '15 days', NOW(), NOW());

-- ============================================
-- ОЦЕНКИ (GRADES)
-- ============================================
INSERT INTO grades (submission_id, score, comment, graded_by, graded_at, created_at, updated_at) VALUES
-- Задание 1
(1, 10, 'Отлично! Всё установлено правильно.', 1, NOW() - INTERVAL '24 days', NOW(), NOW()),
(2, 10, 'Хорошо.', 1, NOW() - INTERVAL '25 days', NOW(), NOW()),
(3, 10, 'Отлично!', 1, NOW() - INTERVAL '39 days', NOW(), NOW()),
(4, 9, 'Хорошо, но скриншот был бы полезен.', 1, NOW() - INTERVAL '9 days', NOW(), NOW()),

-- Задание 2
(6, 18, 'Хорошая работа, но не хватает примера с set.', 1, NOW() - INTERVAL '19 days', NOW(), NOW()),
(7, 20, 'Отличная работа!', 1, NOW() - INTERVAL '21 days', NOW(), NOW()),
(8, 20, 'Превосходно!', 1, NOW() - INTERVAL '34 days', NOW(), NOW()),

-- Задание 3
(10, 28, 'Почти всё верно, небольшая ошибка в 4-й задаче.', 1, NOW() - INTERVAL '14 days', NOW(), NOW()),
(11, 30, 'Всё правильно!', 1, NOW() - INTERVAL '17 days', NOW(), NOW()),
(12, 30, 'Отлично!', 1, NOW() - INTERVAL '29 days', NOW(), NOW()),

-- Задание 4
(14, 40, 'Отличный калькулятор с обработкой ошибок!', 1, NOW() - INTERVAL '9 days', NOW(), NOW()),
(15, 40, 'Бонус за GUI!', 1, NOW() - INTERVAL '24 days', NOW(), NOW()),

-- Задание 5
(16, 48, 'Очень хорошая реализация ООП.', 1, NOW() - INTERVAL '19 days', NOW(), NOW()),

-- Задание 6
(17, 18, 'Хорошо, но добавьте валидацию.', 1, NOW() - INTERVAL '14 days', NOW(), NOW()),
(18, 20, 'Отлично!', 1, NOW() - INTERVAL '24 days', NOW(), NOW()),

-- Задание 9
(20, 28, 'Хорошая схема, но не хватает индексов.', 2, NOW() - INTERVAL '9 days', NOW(), NOW()),

-- Задание 12
(22, 25, 'Всё верно!', 2, NOW() - INTERVAL '14 days', NOW(), NOW());

-- ============================================
-- ПРОГРЕСС ПО УРОКАМ (LESSON_PROGRESS)
-- ============================================
INSERT INTO lesson_progress (student_id, lesson_id, completed, completed_at, created_at, updated_at) VALUES
-- Студент 4 (Анна) - Python курс
(4, 1, true, NOW() - INTERVAL '28 days', NOW(), NOW()),
(4, 2, true, NOW() - INTERVAL '25 days', NOW(), NOW()),
(4, 3, true, NOW() - INTERVAL '20 days', NOW(), NOW()),
(4, 4, true, NOW() - INTERVAL '15 days', NOW(), NOW()),
(4, 5, false, NULL, NOW(), NOW()),
(4, 6, false, NULL, NOW(), NOW()),
-- FastAPI курс
(4, 7, true, NOW() - INTERVAL '18 days', NOW(), NOW()),
(4, 8, true, NOW() - INTERVAL '15 days', NOW(), NOW()),

-- Студент 5 (Дмитрий) - Python курс
(5, 1, true, NOW() - INTERVAL '28 days', NOW(), NOW()),
(5, 2, true, NOW() - INTERVAL '25 days', NOW(), NOW()),
(5, 3, true, NOW() - INTERVAL '22 days', NOW(), NOW()),
(5, 4, true, NOW() - INTERVAL '18 days', NOW(), NOW()),
(5, 5, true, NOW() - INTERVAL '14 days', NOW(), NOW()),
(5, 6, false, NULL, NOW(), NOW()),

-- Студент 6 (Елена) - Python курс (завершён)
(6, 1, true, NOW() - INTERVAL '42 days', NOW(), NOW()),
(6, 2, true, NOW() - INTERVAL '38 days', NOW(), NOW()),
(6, 3, true, NOW() - INTERVAL '34 days', NOW(), NOW()),
(6, 4, true, NOW() - INTERVAL '30 days', NOW(), NOW()),
(6, 5, true, NOW() - INTERVAL '26 days', NOW(), NOW()),
(6, 6, true, NOW() - INTERVAL '22 days', NOW(), NOW()),
-- FastAPI курс
(6, 7, true, NOW() - INTERVAL '28 days', NOW(), NOW()),
(6, 8, true, NOW() - INTERVAL '24 days', NOW(), NOW()),
(6, 9, true, NOW() - INTERVAL '20 days', NOW(), NOW()),

-- Студент 7 (Максим) - SQL курс
(7, 12, true, NOW() - INTERVAL '18 days', NOW(), NOW()),
(7, 13, true, NOW() - INTERVAL '14 days', NOW(), NOW()),
-- Алгоритмы курс
(7, 17, true, NOW() - INTERVAL '22 days', NOW(), NOW()),
(7, 18, true, NOW() - INTERVAL '18 days', NOW(), NOW()),

-- Студент 8 (Ольга) - Python курс
(8, 1, true, NOW() - INTERVAL '12 days', NOW(), NOW()),
(8, 2, true, NOW() - INTERVAL '8 days', NOW(), NOW()),
(8, 3, true, NOW() - INTERVAL '5 days', NOW(), NOW()),

-- Студент 10 (Виктория) - Python курс
(10, 1, true, NOW() - INTERVAL '5 days', NOW(), NOW()),
(10, 2, true, NOW() - INTERVAL '3 days', NOW(), NOW());

-- ============================================
-- ПРОВЕРКА ДАННЫХ
-- ============================================
SELECT 'Users:' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Courses:', COUNT(*) FROM courses
UNION ALL
SELECT 'Lessons:', COUNT(*) FROM lessons
UNION ALL
SELECT 'Assignments:', COUNT(*) FROM assignments
UNION ALL
SELECT 'Enrollments:', COUNT(*) FROM enrollments
UNION ALL
SELECT 'Submissions:', COUNT(*) FROM submissions
UNION ALL
SELECT 'Grades:', COUNT(*) FROM grades
UNION ALL
SELECT 'Lesson Progress:', COUNT(*) FROM lesson_progress;
