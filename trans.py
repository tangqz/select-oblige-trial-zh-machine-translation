import os
import json
import time
import random
from openai import OpenAI

# 设置OpenAI API密钥
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<此处输入API KEY>"))

def translate_texts(texts):
    messages = [
        {"role": "system", "content": "please translate the following galgame conversations from Japanese to Chinese. Please strictly keep the JSON format of the provided content. DO NOT output the original text.Here are the conversations:\n"}
    ]
    for text in texts:
        messages.append({"role": "user", "content": text})
    
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.5,
            )
            translations = []
            for choice in response.choices:
                translations.append(choice.message.content.strip())
            return translations
        except openai.error.RateLimitError as e:  #这块是用gpt写的 这个用法似乎已经过时了 所以不起作用 如果超过速度限制会报错 所以建议加点限速的代码
            retry_count += 1
            sleep_time = (2 ** retry_count) + random.uniform(0, 1)
            print(f"Rate limit error. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    return []

def process_json_file(file_path, output_folder):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 将对话文本每20句分为一个批次
    batches = [data[i:i + 20] for i in range(0, len(data), 20)]
    
    translated_data = []
    for batch in batches:
        batch_text = json.dumps(batch, ensure_ascii=False)
        translated_batch = translate_texts([batch_text])
        
        # 打印翻译结果以便调试
        print("Translated batch:", translated_batch[0])
        
        try:
            # 移除Markdown代码块标记
            clean_translated_batch = translated_batch[0].replace('```json', '').replace('```', '').strip()
            translated_data.extend(json.loads(clean_translated_batch))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Batch text: {batch_text}")
            print(f"Translated batch: {translated_batch[0]}")
    
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 保存翻译后的内容
    output_file_path = os.path.join(output_folder, os.path.basename(file_path))
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=4)

def process_folder(input_folder, output_folder):
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.json'):
            input_file_path = os.path.join(input_folder, file_name)
            output_file_path = os.path.join(output_folder, file_name)
            
            # 检查输出文件是否已经存在
            if os.path.exists(output_file_path):
                print(f"File {output_file_path} already exists. Skipping.")  #万一报错了，再次运行也不会从头开始翻，注意看看最后一个文件结尾有没有翻译完整
                continue
            
            process_json_file(input_file_path, output_folder)

# 处理文件夹中的所有JSON文件
input_folder = 'E:\\gal\\セレクトオブリージュ体験版\\script-json-conv'  # 替换为你的输入文件夹路径
output_folder = 'E:\\gal\\セレクトオブリージュ体験版\\script-json-conv-trans'  # 替换为你的输出文件夹路径
process_folder(input_folder, output_folder)