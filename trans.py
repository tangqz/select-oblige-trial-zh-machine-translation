import os
import json
import time
from openai import OpenAI
import re

# 设置OpenAI API密钥
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "《API KEY HERE》"))

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
    {"role": "system", "content": "Please translate the following galgame conversations from Japanese to Chinese. Adhere strictly to the JSON format provided. Maintain the same number of input and output conversations, without duplicating or merging them. *DO NOT* include the original Japanese text. Character names must also be translated. Japanese characters are not permitted in the output. Your output will be verified, and any presence of '[あ-んア-ン]' will invalidate the translation, requiring a redo. Preserve '&' unchanged, and translate names on both sides of it without merging them. Main character names are as follows: [いっしき かなめ => 一色奏命][たてしな イヴ => 蓼科伊舞][やと くくる => 夜刀玖玖瑠][トウリ => 灯理][旁白 => 旁白][ファイブ => 法伊芙]. Translate 'ワン・ズ・ギフト' to 'One's gift'. Supporting character names must be translated by you. Japanese characters in [txruby], such as [txruby text=\"ふわの\"], are acceptable. Note that all [txruby] in the text to be translated are identifiers and must be strictly preserved.Ensure the translated text is literary and contextually coherent. The Chinese text must be accurate and fluent. Please approach this task with dedication, as it is very important to me.  Here are the conversations:\n"}
    ]
    for text in texts:
        messages.append({"role": "user", "content": text})
    
    rate_limit_check()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
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
    CONV_PER_BATCH = 30 # 每批次对话数
    # 将文本拆分为若干批次
    batches = [data[i:i + CONV_PER_BATCH] for i in range(0, len(data), CONV_PER_BATCH)]
    i = 1
    translated_data = []
    for batch in batches:
        batch_text = json.dumps(batch, ensure_ascii=False)
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            print("Translating batch:", [batch_text])
            translated_batch = translate_texts([batch_text])
            
            # 打印翻译结果以便调试
            print(i, i + CONV_PER_BATCH)
            print("Translated batch:", translated_batch[0])
            i += CONV_PER_BATCH
            try:
                # 移除Markdown代码块标记
                clean_translated_batch = translated_batch[0].replace('```json', '').replace('```', '').strip()
                # 移除[txruby text=*]标注
                clean_translated_batch_no_ruby = re.sub(r'\[txruby text=\\"[^\\"]*\\"\]', '', clean_translated_batch)
                # （漏译检测）检查翻译结果中是否包含日文字符
                if re.search(r'[あ-んア-ン]', clean_translated_batch_no_ruby):
                    raise ValueError("Translation contains Japanese characters.")
                
                translated_data.extend(json.loads(clean_translated_batch))
                break  # 成功翻译，跳出重试循环
            except (json.JSONDecodeError, ValueError) as e:
                retry_count += 1
                print(f"Error occurred: {e}. Retrying {retry_count}/{max_retries}...")
                if retry_count >= max_retries:
                    print(f"Failed to translate batch after {max_retries} attempts. Skipping this file.")
                    return  # 跳过该文件，翻译下一个文件
    
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
                print(f"File {output_file_path} already exists. Skipping.")  #万一报错了，再次运行也不会从头开始翻
                continue
            
            process_json_file(input_file_path, output_folder)

# 处理文件夹中的所有JSON文件
input_folder = 'C:\\Users\\qizhi\\Desktop\\汉化\\窗社1\\script-json-conv-1'  # 替换为你的输入文件夹路径
output_folder = 'C:\\Users\\qizhi\\Desktop\\汉化\\窗社1\\script-json-conv-trans'  # 替换为你的输出文件夹路径
process_folder(input_folder, output_folder)
