"""
章节解析模块
用于从小说章节中提取角色、场景和分镜信息
"""

import json
import requests
from typing import Dict, List, Any


class ChapterParser:
    """章节解析器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_config = config.get('llm', {})
        
    def _call_llm(self, prompt: str) -> str:
        """
        调用大模型 API
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.llm_config.get('api_key')}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.llm_config.get('model'),
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.llm_config.get('temperature', 0.7),
                "max_tokens": self.llm_config.get('max_tokens', 2000)
            }
            
            response = requests.post(
                self.llm_config.get('api_url'),
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"LLM API 调用失败: {e}")
            raise
    
    def extract_characters(self, chapter_text: str) -> List[Dict[str, Any]]:
        """
        提取章节中的角色信息
        
        Args:
            chapter_text: 章节文本
            
        Returns:
            角色列表，每个角色包含姓名、外貌、性格等信息
        """
        prompt = f"""请分析以下小说章节，提取其中出现的所有主要角色。

章节内容：
{chapter_text}

请以 JSON 格式返回角色列表，每个角色包含以下字段：
- name: 角色姓名
- description: 外貌描述（年龄、性别、穿着、特征等）
- personality: 性格特征（3-5个关键词）
- role: 角色类型（主角/配角/反派等）
- importance: 重要程度（1-10）

返回格式示例：
[
  {{
    "name": "张三",
    "description": "30岁男性，身材高大，穿着黑色风衣",
    "personality": ["勇敢", "果断", "正义"],
    "role": "主角",
    "importance": 10
  }}
]

请只返回 JSON，不要有其他文字。"""
        
        response = self._call_llm(prompt)
        
        try:
            # 提取 JSON 部分（处理可能的 Markdown 代码块）
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            characters = json.loads(response)
            return characters
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            print(f"原始响应: {response}")
            return []
    
    def extract_scenes(self, chapter_text: str) -> List[Dict[str, Any]]:
        """
        提取章节中的场景信息
        
        Args:
            chapter_text: 章节文本
            
        Returns:
            场景列表，每个场景包含地点、时间、氛围等信息
        """
        prompt = f"""请分析以下小说章节，提取其中出现的主要场景。

章节内容：
{chapter_text}

请以 JSON 格式返回场景列表，每个场景包含以下字段：
- location: 地点名称
- description: 环境描述（室内/室外、光线、天气、细节等）
- time: 时间段（早晨/午后/夜晚等）
- atmosphere: 氛围关键词（如紧张/温馨/阴森等）
- importance: 重要程度（1-10）

返回格式示例：
[
  {{
    "location": "咖啡馆",
    "description": "安静的室内，阳光透过窗户洒在木桌上",
    "time": "午后",
    "atmosphere": ["温馨", "放松"],
    "importance": 8
  }}
]

请只返回 JSON，不要有其他文字。"""
        
        response = self._call_llm(prompt)
        
        try:
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            scenes = json.loads(response)
            return scenes
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            print(f"原始响应: {response}")
            return []
    
    def parse_chapter(self, chapter_text: str) -> Dict[str, Any]:
        """
        完整解析章节，提取角色、场景和结构化信息
        
        Args:
            chapter_text: 章节文本
            
        Returns:
            包含角色、场景和元数据的字典
        """
        print("开始解析章节...")
        
        # 提取角色
        print("提取角色信息...")
        characters = self.extract_characters(chapter_text)
        print(f"发现 {len(characters)} 个角色")
        
        # 提取场景
        print("提取场景信息...")
        scenes = self.extract_scenes(chapter_text)
        print(f"发现 {len(scenes)} 个场景")
        
        # 构建结果
        result = {
            "characters": characters,
            "scenes": scenes,
            "metadata": {
                "text_length": len(chapter_text),
                "character_count": len(characters),
                "scene_count": len(scenes)
            }
        }
        
        return result
    
    def save_to_file(self, parsed_data: Dict[str, Any], output_path: str):
        """
        将解析结果保存到 JSON 文件
        
        Args:
            parsed_data: 解析后的数据
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        print(f"解析结果已保存到: {output_path}")


if __name__ == "__main__":
    # 测试用例
    test_chapter = """
    第一章：初遇
    
    深秋的午后，阳光透过咖啡馆的玻璃窗洒在木质桌面上。林小雨坐在靠窗的位置，手里捧着一杯热拿铁，眼神有些发呆。她今年二十三岁，穿着一件米白色的毛衣，长发随意地披在肩上，给人一种温柔恬静的感觉。
    
    门铃响起，一个高大的男人推门而入。他约莫三十岁，穿着深灰色的风衣，面容冷峻，眼神锐利。这个男人叫陈默，是一名刑警，刚从警局过来。
    
    陈默环顾四周，目光最终落在了林小雨身上。他径直走过去，在她对面坐下。
    """
    
    # 配置（需要用户提供实际的 API key）
    config = {
        "llm": {
            "api_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
            "model": "custom-ark-cn-beijing-volces-com/glm-4.7",
            "api_key": "YOUR_API_KEY_HERE",
            "temperature": 0.7,
            "max_tokens": 2000
        }
    }
    
    parser = ChapterParser(config)
    result = parser.parse_chapter(test_chapter)
    parser.save_to_file(result, "test_output.json")
    
    print("\n解析结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
