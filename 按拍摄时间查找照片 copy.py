<<<<<<< HEAD
import os
import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import tkinter as tk
from tkinter import filedialog


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


def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        global target_photo_path
        target_photo_path = file_path
        show_image(file_path)
        find_and_display_similar_photos()


def show_image(photo_path):
    try:
        img = Image.open(photo_path)
        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo
    except Exception as e:
        print(f"Error displaying image: {e}")


def find_and_display_similar_photos():
    target_time = get_photo_capture_time(target_photo_path)
    if target_time:
        folder_path = r'E:\手机照片备份'  # 替换为照片文件夹的路径
        loop = asyncio.get_event_loop()
        similar_photos = loop.run_until_complete(
            find_similar_time_photos(target_time, folder_path))
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Photos with similar capture times:\n")
        for photo in similar_photos:
            result_text.insert(tk.END, photo + '\n')
    else:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Could not get capture time from the target photo.")


target_photo_path = ''

root = tk.Tk()
root.title("Find Similar Photos")

open_button = tk.Button(root, text="Open Image", command=open_image)
open_button.pack(pady=10)

image_label = tk.Label(root)
image_label.pack(pady=10)

result_text = tk.Text(root, height=10, width=50)
result_text.pack(pady=10)

root.mainloop()
=======
import os
import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import tkinter as tk
from tkinter import filedialog


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


def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        global target_photo_path
        target_photo_path = file_path
        show_image(file_path)
        find_and_display_similar_photos()


def show_image(photo_path):
    try:
        img = Image.open(photo_path)
        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo
    except Exception as e:
        print(f"Error displaying image: {e}")


def find_and_display_similar_photos():
    target_time = get_photo_capture_time(target_photo_path)
    if target_time:
        folder_path = r'E:\手机照片备份'  # 替换为照片文件夹的路径
        loop = asyncio.get_event_loop()
        similar_photos = loop.run_until_complete(
            find_similar_time_photos(target_time, folder_path))
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Photos with similar capture times:\n")
        for photo in similar_photos:
            result_text.insert(tk.END, photo + '\n')
    else:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Could not get capture time from the target photo.")


target_photo_path = ''

root = tk.Tk()
root.title("Find Similar Photos")

open_button = tk.Button(root, text="Open Image", command=open_image)
open_button.pack(pady=10)

image_label = tk.Label(root)
image_label.pack(pady=10)

result_text = tk.Text(root, height=10, width=50)
result_text.pack(pady=10)

root.mainloop()
>>>>>>> 86db32080a3583a553eecafb03035d7bf7032e68
    