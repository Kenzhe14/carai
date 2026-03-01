import streamlit as st
import requests
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Car Damage Detector", layout="centered")

st.title("🚗 Детектор повреждений авто")
st.write("Загрузите фото автомобиля, и AI найдет вмятины и царапины.")

# URL вашего FastAPI сервера (локально обычно 8000)
API_URL = "http://127.0.0.1:8000/predict"

uploaded_file = st.file_uploader("Выберите изображение...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. Отображаем исходное фото
    image = Image.open(uploaded_file)
    st.image(image, caption="Загруженное фото", use_column_width=True)
    
    if st.button("Проверить на повреждения"):
        with st.spinner('Анализируем...'):
            try:
                # Сбрасываем указатель файла и отправляем в API
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 2. Вывод общего вердикта
                    st.subheader(f"Результат: {data['verdict']}")
                    st.write(f"Найдено дефектов: {data['total_damages']}")

                    if data['total_damages'] > 0:
                        # 3. Рисуем рамки на изображении
                        draw = ImageDraw.Draw(image)
                        for det in data['detections']:
                            box = det['box']
                            # Рисуем прямоугольник
                            draw.rectangle([box['x1'], box['y1'], box['x2'], box['y2']], 
                                         outline="red", width=5)
                            # Пишем название класса
                            draw.text((box['x1'], box['y1'] - 10), 
                                     f"{det['class']} {det['confidence']}", fill="red")
                        
                        st.image(image, caption="Загруженное фото", use_container_width=True)
                        st.json(data['detections']) # Выводим сырые данные для интереса
                    else:
                        st.success("Повреждений не обнаружено!")
                else:
                    st.error(f"Ошибка сервера: {response.status_code}")
            
            except Exception as e:
                st.error(f"Не удалось связаться с API: {e}")
