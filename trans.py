import os
import json
import time
import random
from openai import OpenAI
import re

# 设置OpenAI API密钥
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<此处填API Key>"))

# 请求速率限制参数
MAX_TOKENS_PER_MINUTE = 30000
MAX_REQUESTS_PER_MINUTE = 500

# 速率限制跟踪变量
tokens_used = 0
requests_made = 0
start_time = time.time()

def rate_limit_check():
    global tokens_used, requests_made, start_time

    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time < 60:
        if requests_made >= MAX_REQUESTS_PER_MINUTE or tokens_used >= MAX_TOKENS_PER_MINUTE:
            sleep_time = 60 - elapsed_time
            print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
            start_time = time.time()
            tokens_used = 0
            requests_made = 0
    else:
        start_time = current_time
        tokens_used = 0
        requests_made = 0

def translate_texts(texts):
    global tokens_used, requests_made

    messages = [
        {"role": "system", "content": "please translate the following galgame conversations from Japanese to Chinese. Please strictly keep the JSON format of the provided content. Do not forget to add a ',' after each conversation.Keep the number of input and output conversations the same, and do not output the same conversation twice.*DO NOT* output the original Japanese text.Here are the conversations:\n"}
    ]
    for text in texts:
        messages.append({"role": "user", "content": text})
    
    rate_limit_check()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            frequency_penalty=0.2
        )
        translations = []
        for choice in response.choices:
            translations.append(choice.message.content.strip())
        
        # 更新速率限制跟踪变量
        tokens_used += sum(len(message['content']) for message in messages)
        requests_made += 1

        return translations
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def process_json_file(file_path, output_folder):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 将对话文本每30句分为一个批次
    batches = [data[i:i + 30] for i in range(0, len(data), 30)]
    i = 1
    translated_data = []
    for batch in batches:
        batch_text = json.dumps(batch, ensure_ascii=False)
        translated_batch = translate_texts([batch_text])
        
        # 打印翻译结果以便调试
        print(i,i+10)
        print("Translated batch:", translated_batch[0])
        i += 10
        try:
            # 移除Markdown代码块标记
            clean_translated_batch = translated_batch[0].replace('```json', '').replace('```', '').strip()
            
            # 移除或替换无效的控制字符
            clean_translated_batch = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', clean_translated_batch)
            
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
input_folder = 'C:\\Users\\qizhi\\Desktop\\汉化\\诗\\json-t-conv'  # 替换为你的输入文件夹路径
output_folder = 'C:\\Users\\qizhi\\Desktop\\汉化\\诗\\json-conv-trans'  # 替换为你的输出文件夹路径
process_folder(input_folder, output_folder)
