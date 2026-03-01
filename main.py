from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from ultralytics import YOLO
from PIL import Image
import io

app = FastAPI(title="Car Damage Detection API")

try:
    model = YOLO("best.pt")
    print("Модель успешно загружена!")
except Exception as e:
    print(f"Ошибка загрузки модели: {e}")


@app.get("/")
def home():
    return {"message": "API работает. Используйте /predict для оценки фото."}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Принимает изображение, прогоняет через YOLO и возвращает JSON с найденными дефектами.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Только файлы JPEG или PNG")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        results = model.predict(source=image, conf=0.1)

        result = results[0]

        detections = []

        for box in result.boxes:
            coords = box.xyxy[0].tolist()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            detections.append({
                "class": class_name,
                "confidence": round(confidence, 2),
                "box": {
                    "x1": round(coords[0]),
                    "y1": round(coords[1]),
                    "x2": round(coords[2]),
                    "y2": round(coords[3])
                }
            })
        verdict = "Damaged" if len(detections) > 0 else "Good Condition"

        return JSONResponse(content={
            "filename": file.filename,
            "verdict": verdict,
            "total_damages": len(detections),
            "detections": detections
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
