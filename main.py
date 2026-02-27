from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image
import io

app = FastAPI()

# РАЗРЕШАЕМ CORS (Важно для связи фронтенда и бэкенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)
# 1. ЗАГРУЗКА МОДЕЛИ
# Мы загружаем модель один раз при старте сервера, чтобы не тратить время на каждом запросе.
try:
    model = YOLO("best.pt")
except Exception:
    model = YOLO("yolov8n.pt") # Резервный вариант
    # Если best.pt нет, можно загрузить стандартную для теста:
    # model = YOLO("yolov8n.pt") 

@app.get("/")
def home():
    return {"message": "API работает. Используйте /predict для оценки фото."}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Принимает изображение, прогоняет через YOLO и возвращает JSON с найденными дефектами.
    """
    # Проверка формата файла
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Только файлы JPEG или PNG")

    try:
        # 2. ЧТЕНИЕ ИЗОБРАЖЕНИЯ
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # 3. ИНФЕРЕНС (Распознавание)
        # conf=0.1 отсекает слабые предсказания
        results = model.predict(source=image, conf=0.1)
        
        # Получаем первый результат (так как загружаем 1 фото)
        result = results[0]

        detections = []
        
        # 4. ОБРАБОТКА РЕЗУЛЬТАТОВ
        # result.boxes содержит все найденные прямоугольники
        for box in result.boxes:
            # Получаем координаты x1, y1, x2, y2
            coords = box.xyxy[0].tolist()
            # Получаем уверенность (probability)
            confidence = float(box.conf[0])
            # Получаем ID класса и его имя (например, "dent")
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            detections.append({
                "class": class_name,
                "confidence": round(confidence, 2), # Округляем до 2 знаков
                "box": {
                    "x1": round(coords[0]),
                    "y1": round(coords[1]),
                    "x2": round(coords[2]),
                    "y2": round(coords[3])
                }
            })

        # 5. ФОРМИРОВАНИЕ ОТВЕТА
        # Простая логика вердикта
        verdict = "Damaged" if len(detections) > 0 else "Good Condition"

        return JSONResponse(content={
            "filename": file.filename,
            "verdict": verdict,
            "total_damages": len(detections),
            "detections": detections
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
