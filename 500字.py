# def split_text_into_paragraphs(file_path):
#     try:
#         with open(file_path, 'r', encoding='gb2312') as file:
#             text = file.read()
#         paragraphs = []
#         current_paragraph = ""
#         for char in text:
#             current_paragraph += char
#             if len(current_paragraph) >= 500 and char in '。！？':
#                 paragraphs.append(current_paragraph)
#                 current_paragraph = ""
#         if current_paragraph:
#             paragraphs.append(current_paragraph)
#         return paragraphs
#     except FileNotFoundError:
#         print("错误: 文件未找到!")
#     except Exception as e:
#         print(f"错误: 发生了一个未知错误: {e}")
#     return []


# if __name__ == "__main__":
#     file_path = './film/《101个爱情故事》.txt'    
#     result = split_text_into_paragraphs(file_path)
#     for i, paragraph in enumerate(result, start=1):
#         print(f"段落 {i}:")
#         print(paragraph)
#         print("-" * 50)
    
# import chardet

# def detect_encoding(file_path):
#     with open(file_path, 'rb') as file:
#         raw_data = file.read()
#     result = chardet.detect(raw_data)
#     return result['encoding']

# file_path = './film/《101个爱情故事》.txt'
# encoding = detect_encoding(file_path)
# print(f"文件编码格式是: {encoding}")

