#!/bin/bash
set -e

echo "=== SaaS Dashboard — Backend Setup ==="

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 не найден. Установи Python 3.11+"
    exit 1
fi

# Виртуальное окружение
if [ ! -d "venv" ]; then
    echo "Создаём виртуальное окружение..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Устанавливаем зависимости..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Проверяем .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "ВНИМАНИЕ: Создан .env из примера."
    echo "Обязательно заполни DATABASE_URL и SECRET_KEY перед запуском!"
    echo ""
fi

echo "Запускаем сервер..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000