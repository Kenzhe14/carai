import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="AI Car Damage Detector", page_icon="🚘", layout="wide")

# Подключаем кастомные стили CSS
st.markdown("""
<style>
    /* Основной фон и текст */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Заголовок градиентом */
    h1 {
        background: -webkit-linear-gradient(45deg, #FF003C, #FF7B00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Описание под заголовком */
    .description {
        text-align: center;
        font-size: 1.2rem;
        color: #A0AEC0;
        margin-bottom: 40px;
    }
    
    /* Кнопки загрузки файлов и отправки */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #FF003C 0%, #FF2A55 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 0, 60, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 0, 60, 0.6);
        background: linear-gradient(90deg, #FF2A55 0%, #FF003C 100%);
        color: white;
    }
    
    /* Карточки метрик (статусы, счетчики) */
    .metric-card {
        background-color: #1E212B;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: 1px solid #2D3748;
        margin-bottom: 15px;
    }
    .metric-title {
        color: #A0AEC0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .status-good {
        color: #00E676; /* Неоновый зеленый */
    }
    .status-bad {
        color: #FF003C; /* Неоновый красный/розовый */
    }
    
    /* Картинки с закруглением */
    img {
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🚘 AI Car Damage Detector</h1>", unsafe_allow_html=True)
st.markdown('<p class="description">Загрузите фотографию автомобиля, и наша нейросеть моментально обнаружит царапины, вмятины и другие повреждения кузова.</p>', unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/predict"

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📸 Загрузка фото")
    uploaded_file = st.file_uploader("Выберите или перетащите изображение...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Исходное фото", use_container_width=True)

with col2:
    st.markdown("### 📊 Результаты анализа")
    if uploaded_file is None:
        st.info("👈 Пожалуйста, загрузите изображение для начала проверки.")
    else:
        if st.button("🚀 Проверить на повреждения"):
            with st.spinner("🧠 AI анализирует снимок..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(API_URL, files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        total_damages = data['total_damages']
                        
                        if total_damages > 0:
                            verdict_html = f'<div class="metric-card"><div class="metric-title">Вердикт</div><div class="metric-value status-bad">Повреждения ({total_damages})</div></div>'
                        else:
                            verdict_html = f'<div class="metric-card"><div class="metric-title">Вердикт</div><div class="metric-value status-good">Идеально (0)</div></div>'
                            
                        st.markdown(verdict_html, unsafe_allow_html=True)
                        
                        if total_damages > 0:
                            # Для рисования переводим в RGB, так как может быть RGBA/грейскейл
                            if image.mode != "RGB":
                                image = image.convert("RGB")
                            draw = ImageDraw.Draw(image)
                            
                            try:
                                # Пробуем загрузить стандартный шрифт побольше
                                font = ImageFont.truetype("Arial.ttf", 26) 
                            except:
                                try:
                                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26) # Для Mac
                                except:
                                    font = ImageFont.load_default()
                                
                            for det in data['detections']:
                                box = det['box']
                                conf = int(det['confidence'] * 100)
                                cls = det['class']
                                
                                x1, y1, x2, y2 = box['x1'], box['y1'], box['x2'], box['y2']
                                
                                draw.rectangle([x1, y1, x2, y2], outline="#FF003C", width=6)
                                
                                text = f"{cls} {conf}%"
                                
                                # Задний фон для текста
                                if hasattr(font, 'getbbox'):
                                    text_bbox = font.getbbox(text)
                                    text_width = text_bbox[2] - text_bbox[0]
                                    text_height = text_bbox[3] - text_bbox[1]
                                    draw.rectangle([x1, y1-text_height-8, x1+text_width+8, y1], fill="#FF003C")
                                else:
                                    # Fallback
                                    draw.rectangle([x1, y1-20, x1+100, y1], fill="#FF003C")
                                    
                                draw.text((x1+4, y1-24 if hasattr(font, 'getbbox') else y1-20), text, fill="white", font=font)
                                
                            st.image(image, caption="Обработанное фото", use_container_width=True)
                            
                            with st.expander("Детальный отчет (JSON)"):
                                st.json(data['detections'])
                        else:
                            st.success("🎉 Повреждений не обнаружено! Машина в отличном состоянии.")
                    else:
                        st.error(f"❌ Ошибка сервера: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Не удалось связаться с сервером AI. Убедитесь, что FastAPI запущен (port 8000). Ошибка: {e}")