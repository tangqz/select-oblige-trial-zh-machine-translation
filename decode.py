import os
import json

# 定义输入文件夹和输出文件夹
input_folder = 'C:\\Users\\qizhi\\Desktop\\汉化\诗\\json-conv-trans'
output_folder = 'C:\\Users\\qizhi\\Desktop\\汉化\诗\\json-conv-trans-conv'

# 如果输出文件夹不存在，则创建它
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历输入文件夹中的所有文件
for filename in os.listdir(input_folder):
    if filename.endswith('.json'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # 读取 JSON 文件
        with open(input_path, 'r', encoding='utf-8') as infile:
            data = json.load(infile)

        # 转换数据格式
        decoded_data = []
        for entry in data:
            for key, value in entry.items():
                if ' & ' in key:
                    # 如果键中包含 ' & '，则将其拆分为 names 字段
                    names_list = key.split(' & ')
                    decoded_data.append({"names": names_list, "message": value})
                elif key == "旁白":
                    decoded_data.append({"message": value})
                else:
                    decoded_data.append({"name": key, "message": value})

        # 写入新的 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(decoded_data, outfile, ensure_ascii=False, indent=2)

print("解码完成！")
