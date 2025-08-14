# Mateusz Expenses

## Установка и запуск

1. **Скачай проект**  
   Перейди на страницу главного репозитория roadmap-meta в GitHub, нажми **Code → Download ZIP**, распакуй архив в удобную папку.

2. **Открой PowerShell**  
   Перейди в **корневую папку проекта** (где лежит `pyproject.toml`).  
   Например:  
   ```powershell
   cd "C:\Users\Имя\Загрузки\roadmap-meta\mateusz_expenses"
   ```

3. **Установи Python** (если нет)  
   Скачай и установи Python 3.12+ с [python.org](https://www.python.org/downloads/), при установке поставь галочку *Add Python to PATH*.

4. **Создай виртуальное окружение и установи зависимости**  
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install --upgrade pip
   pip install .
   ```

5. **Подготовь данные**  
   Положи файл отчёта **`transactions.csv`** в папку `data`.

6. **Запусти проект**  
   ```powershell
   expenses --from YYYY-MM-DD --to YYYY-MM-DD --uah-rate КУРС(именно сколько 1 PLN в UAH)
   ```
   *Пример:*
   ```powershell
   expenses --from 2025-07-06 --to 2025-08-12 --uah-rate 11.53
   ```
---

## Дополнительно
- При каждом запуске старые графики и логи перезаписываются.
- Для вопросов по данным или ошибкам — обращаться к автору проекта напрямую.

