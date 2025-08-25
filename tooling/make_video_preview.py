#!/usr/bin/env python3

import os
import sys
import subprocess
import json
import logging
from datetime import timedelta
from PIL import Image

# FRAME SETTINGS
GRID_COLS = 3
GRID_ROWS = 4
TOTAL_FRAMES = GRID_COLS * GRID_ROWS  # 12

# FRAME SIZE
THUMB_WIDTH = 320
THUMB_HEIGHT = 180

# FRAME QUALITY
OUTPUT_QUALITY = 85

TEMP_DIR = os.path.join(os.getcwd(), ".preview_cache")
BORDER_COLOR = (30, 30, 30)  # dark-grey
BORDER_SIZE = 1

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


# --- Получить длительность видео в секундах ---
def get_video_duration(filepath):
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_entries", "format=duration", filepath]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception as e:
        logging.error(f"❌ Ошибка при получении длительности видео: {e}")
        return None


# --- Извлечь кадр в указанное время ---
def extract_frame(filepath, timestamp, output_path):
    cmd = [
        "ffmpeg",
        "-ss",
        str(timestamp),
        "-i",
        filepath,
        "-frames:v",
        "1",
        "-f",
        "image2",
        "-y",  # перезаписать
        output_path,
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except Exception:
        return False


# --- Создать коллаж из кадров ---
def create_collage(image_paths, output_path):
    if len(image_paths) != TOTAL_FRAMES:
        logging.error(f"⚠ Ожидается {TOTAL_FRAMES} кадров, получено {len(image_paths)}")
        return False

    # Создаём большое изображение
    collage_width = GRID_COLS * (THUMB_WIDTH + BORDER_SIZE) + BORDER_SIZE
    collage_height = GRID_ROWS * (THUMB_HEIGHT + BORDER_SIZE) + BORDER_SIZE
    collage = Image.new("RGB", (collage_width, collage_height), BORDER_COLOR)

    for idx, img_path in enumerate(image_paths):
        try:
            with Image.open(img_path) as img:
                # Изменяем размер
                img = img.resize((THUMB_WIDTH, THUMB_HEIGHT), Image.LANCZOS)
                # Позиция
                row = idx // GRID_COLS
                col = idx % GRID_COLS
                x = col * (THUMB_WIDTH + BORDER_SIZE) + BORDER_SIZE
                y = row * (THUMB_HEIGHT + BORDER_SIZE) + BORDER_SIZE
                collage.paste(img, (x, y))
        except Exception as e:
            logging.error(f"❌ Ошибка при обработке кадра {img_path}: {e}")
            return False

    # Сохраняем
    collage.save(output_path, "JPEG", quality=OUTPUT_QUALITY, optimize=True)
    logging.info(f"✅ Коллаж сохранён: {output_path}")
    return True


# --- Очистка временных файлов ---
def cleanup_temp_files(temp_files):
    for f in temp_files:
        try:
            os.remove(f)
        except:
            pass


# --- Основная функция ---
def generate_preview(video_path):
    if not os.path.isfile(video_path):
        logging.error(f"❌ Файл не найден: {video_path}")
        return False

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    filename = os.path.basename(video_path)
    name, ext = os.path.splitext(filename)

    output_preview = os.path.join(os.path.dirname(video_path), f"{name}_preview.jpg")

    logging.info(f"🔍 Обработка видео: {filename}")
    duration = get_video_duration(video_path)
    if not duration:
        return False

    logging.info(f"⏱ Длительность: {timedelta(seconds=duration)}")
    logging.info(f"🖼 Генерация 12 кадров...")

    # Временные файлы кадров
    temp_files = []
    timestamps = []
    for i in range(TOTAL_FRAMES):
        t = duration * (i + 0.5) / TOTAL_FRAMES  # равномерно, не на границах
        timestamps.append(round(t, 2))

    # Извлечение кадров
    for i, t in enumerate(timestamps):
        temp_path = os.path.join(TEMP_DIR, f"frame_{i:02d}.jpg")
        if extract_frame(video_path, t, temp_path):
            temp_files.append(temp_path)
        else:
            logging.error(f"❌ Не удалось извлечь кадр в {t} сек")
            cleanup_temp_files(temp_files)
            return False

    # Создание коллажа
    if create_collage(temp_files, output_preview):
        cleanup_temp_files(temp_files)  # удаляем временные кадры
        return output_preview
    else:
        cleanup_temp_files(temp_files)
        return False


if __name__ == "__main__":
    video_file = "/home/takimoysha/linux-media/downloads/0-output.mp4"
    result = generate_preview(video_file)

    if result:
        logging.info(f"🎉 Готово: {result}")
    else:
        logging.error("❌ Ошибка при генерации превью.")
        sys.exit(1)
