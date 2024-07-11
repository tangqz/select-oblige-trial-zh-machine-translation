"""
将翻译后的json结果转换回VNTextPatch支持的格式
因为encode.py的问题 翻译的json文件的名字部分有问题 懒得改了 直接用日文原版了 如果encode.py改好了 这边或许可以改成使用翻译过的名字
"""
import os
import json

# 定义输入文件夹和输出文件夹
original_folder = 'E:\\gal\\セレクトオブリージュ体験版\\script-json'
translated_folder = 'E:\\gal\\セレクトオブリージュ体験版\\script-json-conv-trans'
output_folder = 'E:\\gal\\セレクトオブリージュ体験版\\script-json-conv-trans-conv'

# 如果输出文件夹不存在，则创建它
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历原始文件夹中的所有文件
for filename in os.listdir(original_folder):
    if filename.endswith('.json'):
        original_path = os.path.join(original_folder, filename)
        translated_path = os.path.join(translated_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # 读取原始 JSON 文件
        with open(original_path, 'r', encoding='utf-8') as original_file:
            original_data = json.load(original_file)

        # 读取翻译后的 JSON 文件
        with open(translated_path, 'r', encoding='utf-8') as translated_file:
            translated_data = json.load(translated_file)

        # 转换数据格式
        converted_data = []
        for original_entry, translated_entry in zip(original_data, translated_data):
            new_entry = {}
            if 'names' in original_entry:
                new_entry['names'] = original_entry['names']
            if 'name' in original_entry:
                new_entry['name'] = original_entry['name']
            new_entry['message'] = list(translated_entry.values())[0]
            converted_data.append(new_entry)

        # 写入新的 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as output_file:
            json.dump(converted_data, output_file, ensure_ascii=False, indent=2)

print("转换完成！")
