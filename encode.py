"""
将VNTextPatch的json进一步转换格式以减少token用量
这个脚本有问题 没有兼容names字段 所以要改改再用
"""
import os
import json

# 定义输入文件夹和输出文件夹
input_folder = 'E:\gal\セレクトオブリージュ体験版\script-json'
output_folder = 'E:\gal\セレクトオブリージュ体験版\script-json-conv'

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
        converted_data = []
        for entry in data:
            if 'name' in entry:
                converted_data.append({entry['name']: entry['message']})
            else:
                converted_data.append({"旁白": entry['message']})

        # 写入新的 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(converted_data, outfile, ensure_ascii=False, indent=2)

print("转换完成！")