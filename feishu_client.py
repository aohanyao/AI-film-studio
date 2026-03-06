"""
飞书客户端
封装飞书 API 调用
"""

import json
import requests
from typing import Dict, Any, Optional, List
import time
from datetime import datetime


class FeishuClient:
    """飞书 API 客户端"""
    
    def __init__(self, app_id: str, app_secret: str, tenant_access_token: Optional[str] = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = tenant_access_token
        self.base_url = "https://open.feishu.cn/open-apis"
    
    def get_tenant_access_token(self) -> Optional[str]:
        """获取 tenant_access_token"""
        if self.tenant_access_token:
            return self.tenant_access_token
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                self = tenant_access_token = result.get("tenant_access_token")
                return self.tenant_access_token
            else:
                print(f"获取 token 失败: {result}")
                return None
        
        except Exception as e:
            print(f"获取 token 异常: {e}")
            return None
    
    def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        发起飞书 API 请求
        
        Args:
            method: HTTP 方法（GET, POST, 等）
            path: API 路径
            data: 请求体数据
            params: URL 参数
            
        Returns:
            API 响应
        """
        token = self.get_tenant_access_token()
        if not token:
            print("无法获取 token")
            return None
        
        url = f"{self.base_url}{path}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            else:
                response = requests.post(url, headers=headers, json=data)
            
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data")
            else:
                print(f"API 请求失败: {result}")
}")
                return None
        
        except Exception as e:
            print(f"API 请求异常: {e}")
            return None
    
    def get_doc_content(self, doc_token: str) -> Optional[Dict[str, Any]]:
        """
        获取文档内容
        
        Args:
            doc_token: 文档 token（从 URL 提取：/docx/xxx）
            
        Returns:
            文档内容
        """
        return self._make_request(
            "GET",
            f"/docx/v1/documents/{doc_token}/blocks",
            params={"page_size": 500}
        )
    
    def get_block_content(self, doc_token: str, block_id: str) -> Optional[Dict[str, Any]]:
        """
        获取区块内容
        
        Args:
            doc_token: 文档 token
            block_id: 区块 ID
            
        Returns:
            区块内容
        """
        return self._make_request(
            "GET",
            f"/docx/v1/documents/{doc_token}/blocks/{block_id}"
        )
    
    def extract_text_from_blocks(self, blocks: List[Dict[str, Any]]) -> str:
        """
        从区块列表提取文本
        
        Args:
            blocks: 区块列表
            
        Returns:
            提取的文本
        """
        text_parts = []
        
        for block in blocks:
            block_type = block.get("block", {}).get("type")
            
            if block_type == "paragraph":
                # 段落
                text_elements = block.get("block", {}).get("paragraph", {}).get("elements", [])
                paragraph_text = self._extract_text_from_elements(text_elements)
                if paragraph_text.strip():
                    text_parts.append(paragraph_text)
            
            elif block_type == "heading1" or block_type == "heading2" or block_type == "heading3":
                # 标题
                level = block_type.replace("heading", "")
                text_elements = block.get("block", {}).get(block_type, {}).get("elements", [])
                heading_text = self._extract_text_from_elements(text_elements)
                if heading_text.strip():
                    text_parts.append(f"{'#' * int(level)} {heading_text}")
        
        return "\n\n".join(text_parts)
    
    def _extract_text_from_elements(self, elements: List[Dict[str, Any]]) -> str:
        """从元素列表提取文本"""
        text_parts = []
        
        for element in elements:
            if element.get("type") == "textRun":
                text_parts.append(element.get("textRun", {}).get("content", ""))
        
        return "".join(text_parts)
    
    def send_message(
        self,
        chat_id: str,
        msg_type: str = "text",
        content: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送消息到飞书群聊或单聊
        
        Args:
            chat_id: 会话 ID
            msg_type: 消息类型（text, post, image, 等）
            content: 消息内容
            
        Returns:
            是否发送成功
        """
        return self._make_request(
            "POST",
            "/message/v4/send",
            data={
                "receive_id": chat_id,
                "msg_type": msg_type,
                "content": json.dumps(content) if content else ""
            }
        ) is not None
    
    def send_text_message(self, chat_id: str, text: str) -> bool:
        """
        发送文本消息
        
        Args:
            chat_id: 会话 ID
            text: 文本内容
            
        Returns:
            是否发送成功
        """
        return self.send_message(
            chat_id,
            msg_type="text",
            content={"text": text}
        )
    
    def send_progress_message(
        self,
        chat_id: str,
        title: str,
        status: str,
        current_step: str,
        total_steps: int,
        current_step_index: int,
        details: Optional[str] = None
    ) -> bool:
        """
        发送进度通知消息
        
        Args:
            chat_id: 会话 ID
            title: 任务标题
            status: 状态（running, completed, failed）
            current_step: 当前步骤
            total_steps: 总步骤数
            current_step_index: 当前步骤索引
            details: 详细信息
            
        Returns:
            是否发送成功
        """
        # 创建富文本消息
        emoji = "🔄" if status == "running" else ("✅" if status == "completed" else "❌")
        
        progress_bar = "[" + "=" * current_step_index + " " * (total_steps - current_step_index) + "]"
        progress_percent = int((current_step_index / total_steps) * 100) if total_steps > 0 else 0
        
        content = {
            "post": {
            },
                "zh_cn": {
                    "title": f"{emoji} {title}",
                    "content": [
                        [{
                            "tag": "text",
                            "text": f"进度: {progress_bar} ({progress_percent}%)\n"
                        }],
                        [{
                            "tag": "text",
                            "text": f"当前步骤: {current_step}\n"
                        }],
                        [{
                            "tag": "text",
                            "text": f"状态: {status}\n"
                        }]
                    ]
                }
            }
        }
        
        if details:
            content["post"]["zh_cn"]["content"].append([{
                "tag": "text",
                "text": f"\n详情:\n{details}"
            }])
        
        return self.send_message(
            chat_id,
            msg_type="post",
            content=content
        )


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # 测试用例
    print("=" * 50)
    print("飞书客户端测试")
    print("=" * 50)
    
    # 从配置文件加载
    config_path = "settings.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        feishu_config = config.get('feishu', {})
        app_id = feishu_config.get('app_id', '')
        app_secret = feishu_config.get('app_secret', '')
        
        if app_id and app_secret:
            print(f"✅ 配置已加载")
            print(f"  App ID: {app_id[:8]}...")
            
            # 创建客户端
            client = FeishuClient(app_id, app_secret)
            
            # 测试获取 token
            print("\n测试获取 token...")
            token = client.get_tenant_access_token()
            
            if token:
                print(f"✅ Token 获取成功: {token[:20]}...")
            else:
                print("❌ Token 获取失败")
        else:
            print("⚠️ 飞书配置不完整，请检查 settings.json")
    else:
        print("⚠️ 配置文件不存在")
