# Графический редактор

Создать новое виртуальное окружение: `py -m venv .venv`

Чтобы активировать ВС нужно выполнить: 
- на windows  в PowerShell: `.venv\Scripts\activate`
- на macOS или Linux: `source .venv/bin/activate`


---
>Иногда, даже с правильной командой, PowerShell может выдать другую ошибку, связанную с "политикой выполнения". 
>- Команда для разрешения запуска в конкретном терминале: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`
>- Команда для разрешения запуска текущему пользователю: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
>- Посмотреть список разрешений: `Get-ExecutionPolicy -List`
---


Установка зависимостей: `pip install -r requirements.txt`

Обновить зависимости из окружения: `pip freeze > requirements.txt`

Запуск скрипта `python editor.py`