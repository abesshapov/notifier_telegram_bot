# Notifier telegram bot

Бот представляет из себя менеджер напоминаний.

Для создания заметок пользователь обязан пройти регистрацию - указать имя пользователя и электронную почту.

**Технологический стек:**

- Взаимодействие с API телеграмма с помощью aiogram
- Бэкенд - FastAPI. Необходим для обработки вебхуков со стороны телеграмма (механизм на базе Update)
- DI - dependency_injector
- Хранение данных - PostgreSQL, aiopg (паттерн "Репозиторий")

**Запуск**

1. Создание venv: ```python -m venv .``` ИЛИ ```poetry shell```
2. Установка зависимостей (после активации виртуального окружения): ```poetry install```
3. Заполнить .env и положить в корень проекта (пример можно взять из .env.example)
4. Так как update-ы приходят через webhook, необходимо установить WEBHOOK_URL со схемой https (требование Telegram API). Для этого подойдет такое решение, как [ngrok](https://ngrok.com/download)
5. Накатить миграции: ```poetry run python -m scripts.migrate --reload```
6. Запустить проект: ```uvicorn app:create_app --reload --port XXX```. Порт при этом должен совпадать с указанным в ngrok на этапе **4**.

**Отчет о тестировании**

Проект покрыт тестами на 95%:

![image](https://github.com/user-attachments/assets/0a195167-fb7d-4c16-b392-fd8116b7ff79)

