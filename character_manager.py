"""
角色卡片管理系统
用于管理角色一致性，包括角色信息、参考图像和提示词模板
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime


class CharacterManager:
    """角色管理器"""
    
    def __init__(self, project_dir: str = "."):
        self.project_dir = project_dir
        self.characters_file = os.path.join(project_dir, "characters.json")
        self.characters = self._load_characters()
        
    def _load_characters(self) -> Dict[str, Any]:
        """加载角色数据"""
        if os.path.exists(self.characters_file):
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_characters(self):
        """保存角色数据"""
        with open(self.characters_file, 'w', encoding='utf-8') as f:
            json.dump(self.characters, f, ensure_ascii=False, indent=2)
    
    def add_character(self, character_info: Dict[str, Any]) -> str:
        """
        添加或更新角色
        
        Args:
            character_info: 角色信息字典
            
        Returns:
            角色 ID
        """
        name = character_info.get('name', '')
        if not name:
            raise ValueError("角色名称不能为空")
        
        # 生成角色 ID
        char_id = f"char_{name.lower().replace(' ', '_')}"
        
        # 构建角色卡片
        character_card = {
            "id": char_id,
            "name": name,
            "description": character_info.get('description', ''),
            "personality": character_info.get('personality', []),
            "role": character_info.get('role', '配角'),
            "importance": character_info.get('importance', 5),
            "reference_images": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 保存角色
        self.characters[char_id] = character_card
        self._save_characters()
        
        return char_id
    
    def get_character(self, char_id: str) -> Dict[str, Any]:
        """获取角色信息"""
        return self.characters.get(char_id, {})
    
    def get_character_by_name(self, name: str) -> Dict[str, Any]:
        """根据姓名获取角色"""
        for char_id, char in self.characters.items():
            if char.get('name') == name:
                return char
        return {}
    
    def add_reference_image(self, char_id: str, image_path: str):
        """
        为角色添加参考图像
        
        Args:
            char_id: 角色 ID
            image_path: 图像路径
        """
        if char_id in self.characters:
            if image_path not in self.characters[char_id]['reference_images']:
                self.characters[char_id]['reference_images'].append(image_path)
                self.characters[char_id]['updated_at'] = datetime.now().isoformat()
                self._save_characters()
    
    def generate_consistency_prompt(self, char_id: str, style: str = "realistic") -> str:
        """
        生成角色一致性提示词
        
        Args:
            char_id: 角色 ID
            style: 风格（realistic/anime/cinematic）
            
        Returns:
            角色一致性提示词
        """
        char = self.characters.get(char_id, {})
        if not char:
            return ""
        
        # 基础描述
        description = char.get('description', '')
        personality = ', '.join(char.get('personality', []))
        
        # 根据风格调整
        style_modifiers = {
            "realistic": "photorealistic, 8K, ultra detailed",
            "anime": "anime style, vibrant colors",
            "cinematic": "cinematic lighting, movie quality"
        }
        
        base_prompt = f"{description}, {personality}"
        
        # 添加风格标签
        if style in style_modifiers:
            base_prompt += f", {style_modifiers[style]}"
        
        # 添加角色一致性标签
        base_prompt += f", same character, ID: {char_id}"
        
        return base_prompt
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """获取所有角色"""
        return list(self.characters.values())
    
    def export_for_llm(self) -> str:
        """
        导出角色信息为 LLM 可理解的格式
        
        Returns:
            角色信息文本
        """
        if not self.characters:
            return "尚未添加角色信息"
        
        output = "角色列表：\n\n"
        for char in self.get_all_characters():
            output += f"角色：{char['name']}\n"
            output += f"  描述：{char.get('description', '')}\n"
            output += f"  性格：{', '.join(char.get('personality', []))}\n"
            output += f"  类型：{char.get('role', '配角')}\n"
            output += f"  重要程度：{char.get('importance', 5)}/10\n\n"
        
        return output
    
    def update_character(self, char_id: str, updates: Dict[str, Any]):
        """
        更新角色信息
        
        Args:
            char_id: 角色 ID
            updates: 要更新的字段
        """
        if char_id in self.characters:
            self.characters[char_id].update(updates)
            self.characters[char_id]['updated_at'] = datetime.now().isoformat()
            self._save_characters()


if __name__ == "__main__":
    # 测试用例
    print("=" * 50)
    print("角色管理器测试")
    print("=" * 50)
    
    # 创建管理器
    manager = CharacterManager()
    
    # 添加角色
    char1 = {
        "name": "林小雨",
        "description": "23岁女性，穿着米白色毛衣，长发，温柔恬静",
        "personality": ["温柔", "恬静", "善良"],
        "role": "主角",
        "importance": 10
    }
    
    char2 = {
        "name": "陈默",
        "description": "30岁男性，穿着深灰色风衣，面容冷峻，眼神锐利",
        "personality": ["冷峻", "果断", "正义"],
        "role": "主角",
        "importance": 10
    }
    
    print("\n添加角色...")
    id1 = manager.add_character(char1)
    id2 = manager.add_character(char2)
    print(f"角色 1 ID: {id1}")
    print(f"角色 2 ID: {id2}")
    
    print("\n获取角色信息...")
    print(json.dumps(manager.get_character(id1), ensure_ascii=False, indent=2))
    
    print("\n生成一致性提示词...")
    prompt1 = manager.generate_consistency_prompt(id1, "cinematic")
    prompt2 = manager.generate_consistency_prompt(id2, "cinematic")
    print(f"林小雨: {prompt1}")
    print(f"陈默: {prompt2}")
    
    print("\n导出为 LLM 格式...")
    print(manager.export_for_llm())
    
    print("\n✅ 测试完成")
