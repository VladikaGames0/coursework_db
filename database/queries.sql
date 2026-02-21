-- Примеры SQL запросов для анализа данных

-- 1. Компании и количество вакансий
SELECT
    e.name AS "Компания",
    COUNT(v.id) AS "Количество вакансий"
FROM employers e
LEFT JOIN vacancies v ON e.id = v.employer_id
GROUP BY e.id, e.name
ORDER BY COUNT(v.id) DESC;

-- 2. Все вакансии с деталями
SELECT
    e.name AS "Компания",
    v.name AS "Вакансия",
    v.salary AS "Зарплата",
    v.url AS "Ссылка"
FROM vacancies v
JOIN employers e ON v.employer_id = e.id
ORDER BY v.salary DESC NULLS LAST;

-- 3. Средняя зарплата по вакансиям
SELECT
    ROUND(AVG(salary), 2) AS "Средняя зарплата"
FROM vacancies
WHERE salary IS NOT NULL;

-- 4. Вакансии с зарплатой выше средней
WITH avg_salary AS (
    SELECT AVG(salary) as avg_sal
    FROM vacancies
    WHERE salary IS NOT NULL
)
SELECT
    e.name AS "Компания",
    v.name AS "Вакансия",
    v.salary AS "Зарплата",
    v.url AS "Ссылка"
FROM vacancies v
JOIN employers e ON v.employer_id = e.id
CROSS JOIN avg_salary
WHERE v.salary > avg_salary.avg_sal
ORDER BY v.salary DESC;

-- 5. Поиск вакансий по ключевому слову
SELECT
    e.name AS "Компания",
    v.name AS "Вакансия",
    v.salary AS "Зарплата",
    v.url AS "Ссылка"
FROM vacancies v
JOIN employers e ON v.employer_id = e.id
WHERE LOWER(v.name) LIKE '%python%'
ORDER BY v.salary DESC;