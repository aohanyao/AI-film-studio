"""
简单测试千问 API
"""
import requests
import json
import time

print("=" * 50)
print("测试千问 API 连接")
print("=" * 50)

# 测试数据
url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-7a447ace618942288c48e7d1d56de58c",
    "Content-Type": "application/json"
}
payload = {
    "model": "qwen-max",
    "messages": [
        {"role": "user", "content": "你好，请用一句话回复"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

print(f"\nAPI URL: {url}")
print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
print(f"\n开始请求...")

start_time = time.time()

try:
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    elapsed = time.time() - start_time
    
    print(f"\n✅ 请求完成！")
    print(f"耗时: {elapsed:.2f} 秒")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n响应内容:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n❌ 错误响应:")
        print(response.text)
        
except requests.exceptions.Timeout:
    elapsed = time.time() - start_time
    print(f"\n❌ 请求超时！")
    print(f"已等待: {elapsed:.2f} 秒")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n❌ 请求失败！")
    print(f"错误: {e}")
    print(f"已等待: {elapsed:.2f} 秒")
    import traceback
    traceback.print_exc()
