import requests
import json

print("开始测试千问 API...")

url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-7a447ace618942288c48e7d1d56de58c",
    "Content-Type": "application/json"
}
payload = {
    "model": "qwen-max",
    "messages": [{"role": "user", "content": "回复：测试成功"}]
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")
