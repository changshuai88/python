import os
import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from PIL.ExifTags import TAGS


def get_photo_capture_time(photo_path):
    try:
        image = Image.open(photo_path)
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag)
                if tag_name == 'DateTimeOriginal':
                    return datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error reading exif data from {photo_path}: {e}")
    return None


async def get_photo_time_async(executor, photo_path):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, get_photo_capture_time, photo_path)


async def find_similar_time_photos(target_time, folder_path, num_photos=10):
    photo_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                photo_paths.append(os.path.join(root, file))

    with ThreadPoolExecutor() as executor:
        tasks = [get_photo_time_async(executor, path) for path in photo_paths]
        capture_times = await asyncio.gather(*tasks)

    photo_times = []
    for path, capture_time in zip(photo_paths, capture_times):
        if capture_time:
            time_difference = abs((capture_time - target_time).total_seconds())
            photo_times.append((time_difference, path))

    photo_times.sort(key=lambda x: x[0])
    return [photo for _, photo in photo_times[:num_photos]]


if __name__ == "__main__":
    target_photo_path = './name/1981092.JPG'  # 替换为目标照片的路径
    folder_path = 'E:\手机照片备份'  # 替换为照片文件夹的路径

    target_time = get_photo_capture_time(target_photo_path)
    if target_time:
        loop = asyncio.get_event_loop()
        similar_photos = loop.run_until_complete(
            find_similar_time_photos(target_time, folder_path))
        print("Photos with similar capture times:")
        for photo in similar_photos:
            print(photo)
    else:
        print("Could not get capture time from the target photo.")