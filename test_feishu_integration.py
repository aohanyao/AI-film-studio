"""
测试飞书集成
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import os
from feishu_client import FeishuClient

print("=" * 50)
print("飞书集成测试")
print("=" * 50)

# 加载配置
config_path = "settings.json"
if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print("✅ 配置已加载")
else:
    print("❌ 配置文件不存在")
    sys.exit(1)

# 获取飞书配置
feishu_config = config.get('feishu', {})
app_id = feishu_config.get('app_id', '')
app_secret = feishu_config.get('app_secret', '')

if not app_id or not app_secret:
    print("❌ 飞书配置不完整")
    print("请在 settings.json 中配置 feishu.app_id 和 feishu.app_secret")
    sys.exit(1)

# 创建客户端
print(f"\n创建飞书客户端...")
client = FeishuClient(app_id, app_secret)
print(f"✅ App ID: {app_id[:8]}...")

# 测试 1: 获取 token

print("\n[测试 1] 获取 tenant_access_token...")
token = client.get_tenant_access_token()
if token:
    print(f"✅ Token 获取成功: {token[:20]}...")
else:
    print("❌ Token 获取失败")
    sys.exit(1)

# 测试 2: 读取飞书文档
test_doc_token = feishu_config.get('test_doc_token', '')
if test_doc_token:
    print(f"\n[测试 2] 读取文档: {test_doc_token}")
    doc_content = client.get_doc_content(test_doc_token)
    
    if doc_content:
        print("✅ 文档内容获取成功")
        
        # 提取文本
        blocks = doc_content.get('items', [])
        text = client.extract_text_from_blocks(blocks)
        
        print(f"\n--- 文本预览（前 500 字）---")
        print(text[:500])
        print("---\n")
    else:
        print("❌ 文档内容获取失败")
else:
    print("\n[测试 2] 跳过文档测试（未配置 test_doc_token）")

# 测试 3: 发送消息
test_chat_id = feishu_config.get('test_chat_id', '')
if test_chat_id:
    print(f"\n[测试 3] 发送文本消息...")
    success = client.send_text_message(
        test_chat_id,
        f"🤖 AI Film Studio 测试消息\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    if success:
        print("✅ 文本消息发送成功")
    else:
        print("❌ 文本消息发送失败")
else:
    print("\n[测试 3] 跳过消息测试（未配置 test_chat_id）")

# 测试 4: 发送进度消息
if test_chat_id:
    print(f"\n[测试 4] 发送进度消息...")
    success = client.send_progress_message(
        test_chat_id,
        title="AI Film Studio 任务",
        status="running",
        current_step="解析章节",
        total_steps=5,
        current_step_index=2,
        details="正在提取角色和场景信息..."
    )
    
    if success:
        print("✅ 进度消息发送成功")
    else:
        print("❌ 进度消息发送失败")
else:
    print("\n[测试 4] 跳过进度消息测试（未配置 test_chat_id）")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)
