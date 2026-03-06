"""
工作流协调器
协调整个小说转视频的完整流程
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime

from chapter_parser import ChapterParser
from character_manager import CharacterManager
from prompt_templates import PromptTemplates
from comfyui_wrapper import ComfyUIWrapper
from image_cache import ImageCache


class WorkflowCoordinator:
    """工作流协调器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.chapter_parser = ChapterParser(config)  # 传递完整 config，不是只传 llm 部分
        self.character_manager = CharacterManager()
        self.image_cache = ImageCache(cache_dir="cache/images")
        
        comfy_config = config.get('comfyui', {})
        self.comfyui = ComfyUIWrapper(
            host=comfy_config.get('host', '127.0.0.1'),
            port=comfy_config.get('port', 8018)
        )
    
    def process_chapter(
        self,
        chapter_text: str,
        style: str = "cinematic",
        generate_images: bool = True,
        generate_videos: bool = False
    ) -> Dict[str, Any]:
        """
        处理章节（完整流程）
        
        Args:
            chapter_text: 章节文本
            style: 风格
            generate_images: 是否生成图像
            generate_videos: 是否生成视频
            
        Returns:
            处理结果
        """
        print("=" * 50)
        print("开始处理章节")
        print("=" * 50)
        
        result = {
            'success': False,
            'chapter': {},
            'characters': [],
            'scenes': [],
            'images': [],
            'videos': [],
            'errors': []
        }
        
        try:
            # Step 1: 解析章节
            print("\n[1/5] 解析章节...")
            chapter_data = self.chapter_parser.parse_chapter(chapter_text)
            result['chapter'] = chapter_data
            print(f"✅ 发现 {len(chapter_data.get('characters', []))} 个角色")
            print(f"✅ 发现 {len(chapter_data.get('scenes', []))} 个场景")
            
            # Step 2: 提取并管理角色
            print("\n[2/5] 管理角色...")
            characters = chapter_data.get('characters', [])
            for char in characters:
                try:
                    char_id = self.character_manager.add_character(char)
                    char['char_id'] = char_id
                    print(f"✅ 添加角色: {char.get('name')}")
                except Exception as e:
                    print(f"⚠️ 添加角色失败: {e}")
                    result['errors'].append(str(e))
            
            result['characters'] = characters
            
            # Step 3: 为每个场景生成提示词
            print("\n[3/5] 生成场景提示词...")
            scenes = chapter_data.get('scenes', [])
            
            for scene_idx, scene in enumerate(scenes):
                scene_desc = scene.get('description', '')
                
                # 查找场景中的角色
                scene_characters = []
                for char in characters:
                    if char.get('name') in scene_desc:
                        consistency_prompt = self.character_manager.generate_consistency_prompt(
                            char.get('char_id'),
                            style
                        )
                        scene_characters.append({
                            'name': char.get('name'),
                            'consistency_prompt': consistency_prompt
                        })
                
                # 生成提示词
                prompt = PromptTemplates.generate_image_prompt(
                    scene_description=scene_desc,
                    characters=scene_characters,
                    style=style,
                    shot_type="medium"
                )
                
                scene['prompt'] = prompt
                print(f"✅ 场景 {scene_idx + 1} 提示词生成完成")
            
            result['scenes'] = scenes
            
            # Step 4: 生成图像
            if generate_images:
                print("\n[4/4] 生成场景图像...")
                
                # 检查 ComfyUI 连接
                if not self.comfyui.check_connection():
                    print("⚠️ ComfyUI 未连接，跳过图像生成")
                    result['errors'].append("ComfyUI 未连接")
                else:
                    for scene_idx, scene in enumerate(scenes):
                        try:
                            prompt = scene.get('prompt', '')
                            
                            # 检查缓存
                            cached_image = self.image_cache.get(prompt)
                            if cached_image:
                                print(f"✅ 场景 {scene_idx + 1} 使用缓存图像")
                                image_result = cached_image
                            else:
                                print(f"生成场景 {scene_idx + 1} 图像...")
                                
                                # 生成图像
                                image_result = self.comfyui.generate_image(
                                    prompt=prompt,
                                    width=1024,
                                    height=576,
                                    steps=20
                                )
                                
                                # 保存到缓存
                                if image_result.get('success'):
                                    self.image_cache.set(prompt, image_result)
                            
                            result['images'].append({
                                'scene_index': scene_idx,
                                'prompt': prompt,
                                'result': image_result
                            })
                            
                            print(f"✅ 场景 {scene_idx + 1} 图像生成完成")
                            
                        except Exception as e:
                            print(f"⚠️ 场景 {scene_idx + 1} 图像生成失败: {e}")
                            result['errors'].append(str(e))
            
            # Step 5: 生成视频（可选）
            if generate_videos:
                print("\n生成视频...")
                # TODO: 实现视频生成逻辑
                pass
            
            result['success'] = True
            
        except Exception as e:
            print(f"\n❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            result['errors'].append(str(e))
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"output/workflow_result_{timestamp}.json"
        os.makedirs('output', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 移除不能序列化的对象
            clean_result = self._clean_result_for_json(result)
            json.dump(clean_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 结果已保存到: {output_file}")
        
        return result
    
    def _clean_result_for_json(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """清理结果以便 JSON 序列化"""
        # 简单的清理逻辑
        if 'images' in result:
            for img in result['images']:
                if 'result' in img:
                    # 只保留必要信息
                    img['result'] = {
                        'success': img['result'].get('success'),
                        'prompt_id': img['result'].get('prompt_id')
                    }
        return result


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # 测试用例
    print("=" * 50)
    print("工作流协调器测试")
    print("=" * 50)
    
    # 加载配置
    config_path = "settings.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 配置已加载")
        print(f"  LLM URL: {config.get('llm', {}).get('api_url', '未设置')}")
        print(f"  LLM 模型: {config.get('llm', {}).get('model', '未设置')}")
    else:
        config = {}
        print("⚠️ 配置文件不存在，使用空配置")
    
    # 创建协调器
    coordinator = WorkflowCoordinator(config)
    
    # 测试章节
    test_chapter = """
    第一章：初遇
    
    深秋的午后，阳光透过咖啡馆的玻璃窗洒在木质桌面上。林小雨坐在靠窗的位置，手里捧着一杯热拿铁，眼神有些发呆。她今年二十三岁，穿着一件米白色的毛衣，长发随意地披在肩上，给人一种温柔恬静的感觉。
    
    门铃响起，一个高大的男人推门而入。他约莫三十岁，穿着深灰色的风衣，面容冷峻，眼神锐利。这个男人叫陈默，是一名刑警，刚从警局过来。
    
    陈默环顾四周，目光最终落在了林小雨身上。他径直走过去，在她对面坐下。
    """
    
    # 处理章节
    result = coordinator.process_chapter(
        chapter_text=test_chapter,
        style="cinematic",
        generate_images=False  # 测试时不生成图像
    )
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
    
    if result['success']:
        print("✅ 工作流测试成功")
        print(f"角色数量: {len(result['characters'])}")
        print(f"场景数量: {len(result['scenes'])}")
    else:
        print("❌ 工作流测试失败")
        print(f"错误: {result['errors']}")
