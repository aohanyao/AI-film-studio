# 飞书集成配置指南

## 获取飞书应用凭证

要使用飞书集成功能，你需要创建一个飞书应用并获取凭证。

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 登录并进入[开发者后台](https://open.feishu.cn/app)
3. 点击"创建应用"
4. 选择"企业自建应用"
5. 填写应用信息：
   - 应用名称：AI Film Studio
   - 应用描述：AI电影制作工具

### 2. 获取 App ID 和 App Secret

在应用详情页面，找到：
- **App ID**：复制到 `settings.json` 的 `feishu.app_id`
- **App Secret**：复制到 `settings.json` 的 `feishu.app_secret`

### 3. 配置权限

在应用权限管理中，申请以下权限：

**文档权限：**
- `docx:document` - 查看、评论、导出文档
- `docx:document:readonly` - 只读访问文档

**消息权限：**
- `im:message` - 发送消息
- `im:message:group_at_msg` - 发送群组消息

### 4. 发布应用

1. 在"版本管理与发布"页面
2. "创建版本"
3. "申请发布"
4. 等待管理员审批（如果是个人应用，可能需要联系管理员）

### 5. 获取测试 Chat ID

**发送测试消息的方式：**

**方式 1：使用飞书机器人发送消息**
1. 在飞书中搜索你的应用名称
2. 添加机器人到群聊或单聊
3. 机器人会收到一个 chat_id

**方式 2：通过开发者后台**
1. 在"调试工具"中找到"发送消息"
2. 可以查看当前会话的 chat_id

### 6. 获取测试文档 Token

1. 在飞书中创建一个文档
2. 复制文档 URL，例如：`https://xxxx.feishu.cn/docx/AbCdEfGhIjKlMnOpQrStUv`
3. `AbCdEfGhIjKlMnOpQrStUv` 就是文档 token

## 配置 settings.json

```json
{
  "feishu": {
    "app_id": "cli_xxxxxxxxxxxxxx",
    "app_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "test_doc_token": "AbCdEfGhIjKlMnOpQrStUv",
    "test_chat_id": "oc_xxxxxxxxxxxxxx"
  }
}
```

## 测试集成

配置完成后，运行测试脚本：

```bash
cd AI-film-studio
python test_feishu_integration.py
```

测试脚本会：
1. ✅ 测试获取 tenant_access_token
2. ✅ 测试读取飞书文档（需要配置 test_doc_token）
3. ✅ 测试发送文本消息（需要配置 test_chat_id）
4. ✅ 测试发送进度消息（需要配置 test_chat_id）

## API 端点

### 获取飞书文档内容
```
GET /api/feishu/doc?doc_token={token}
```

### 发送飞书消息
```
POST /api/feishu/send_message
{
  "chat_id": "oc_xxxxxxxxxxxxxx",
  "text": "消息内容"
}
```

### 发送飞书进度消息
```
POST /api/feishu/send_progress
{
  "chat_id": "oc_xxxxxxxxxxxxxx",
  "title": "任务标题",
  "status": "running",
  "current_step": "解析章节",
  "total_steps": 5,
  "current_step_index": 2,
  "details": "详细信息"
}
```

## 常见问题

### Token 获取失败
- 检查 App ID 和 App Secret 是否正确
- 确认应用已发布并审批通过

### 文档读取失败
- 检查文档 token 是否正确
- 确认应用有文档读取权限
- 确认机器人已添加到文档所在的工作区

### 消息发送失败
- 检查 chat_id 是否正确
- 确认应用有消息发送权限
- 确认机器人已添加到目标群聊或已建立单聊

### 权限不足
- 在飞书开放平台申请所需的权限
- 等待权限审批通过
- 重新获取 tenant_access_token

## 下一步

配置完成后，你可以：
1. 使用 `/api/feishu/doc` 读取飞书中的小说章节
2. 使用 `/api/feishu/send_progress` 在飞书中接收任务进度通知
3. 集成到完整的工作流中，实现从飞书读取章节 → 生成视频 → 发送结果到飞书
