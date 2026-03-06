"""
测试 API 连接
"""
import requests
import json

print("=" * 50)
print("API 连接测试")
print("=" * 50)

# 测试主页
try:
    print("\n1. 测试主页访问...")
    response = requests.get('http://127.0.0.1:5000', timeout=5)
    print(f"   ✅ 主页响应: {response.status_code}")
except Exception as e:
    print(f"   ❌ 主页访问失败: {e}")

# 测试保存 API
try:
    print("\n2. 测试保存 API...")
    data = {'text': '测试'}
    response = requests.post(
        'http://127.0.0.1:5000/api/save',
        json=data,
        timeout=5
    )
    print(f"   ✅ 保存 API 响应: {response.status_code}")
    print(f"   返回数据: {response.json()}")
except Exception as e:
    print(f"   ❌ 保存 API 失败: {e}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)
