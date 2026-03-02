#!/bin/bash

# Цвета для вывода в терминал
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Запуск AI Car Damage Detector ===${NC}"

# Активация виртуального окружения, если оно существует
if [ -d "venv" ]; then
    echo "Активация виртуального окружения (venv)..."
    source venv/bin/activate
fi

# Убиваем старые процессы на портах 8000 (FastAPI) и 8501 (Streamlit), если они зависли
echo "Очистка портов 8000 и 8501..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null

# Функция для завершения обоих серверов при нажатии Ctrl+C
function cleanup() {
    echo -e "\n${RED}Остановка серверов...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Серверы остановлены. Хорошего дня!${NC}"
    exit 0
}

trap cleanup SIGINT

# Запуск FastAPI
echo -e "${GREEN}-> Запуск FastAPI Backend (порт 8000)${NC}"
python -m uvicorn main:app --reload &
BACKEND_PID=$!

# Дадим бэкенду секунду на старт
sleep 2

# Запуск Streamlit
echo -e "${GREEN}-> Запуск Streamlit Frontend (порт 8501)${NC}"
python -m streamlit run streamlit_app.py --server.headless=true &
FRONTEND_PID=$!

# Открываем браузер (если Mac)
sleep 2
open http://localhost:8501 2>/dev/null

echo -e "${BLUE}=====================================${NC}"
echo -e "🚀 ${GREEN}Приложение успешно запущено!${NC}"
echo -e "UI доступно по адресу: http://localhost:8501"
echo -e "Backend API доступно по адресу: http://localhost:8000/docs"
echo -e "Для остановки нажмите ${RED}Ctrl+C${NC}"
echo -e "${BLUE}=====================================${NC}"

# Ожидание
wait
