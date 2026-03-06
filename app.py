from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime

# 导入自定义模块
from modules import (
    script_input,
    character_input,
    environment_input,
    text_generation,
    image_description_generation,
    keyframe_generation,
    shot_video_generation
)

# 导入章节解析模块
from chapter_parser import ChapterParser
# 导入角色管理模块
from character_manager import CharacterManager
# 导入提示词模板模块
from prompt_templates import PromptTemplates
# 导入 ComfyUI 封装
from comfyui_wrapper import ComfyUIWrapper


app = Flask(__name__)
CORS(app)

# 配置
config = {}
config_path = "settings.json"
if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

# ── 根路由 ────────────────────────────────────────────────
@app.route('/')
def index():
    return jsonify({
        'name': config.get('project', {}).get('name', 'AI Film Studio'),
        'status': 'running',
        'features': [
            '章节解析',
            '角色管理',
            '提示词生成',
            '图像生成',
            '视频生成'
        ]
    })

# ── 保存 API ────────────────────────────────────────────────
@app.route('/api/save', methods=['POST'])
def save_text():
    data = request.json
    text = data.get('text', '')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'saved_{timestamp}.txt'
    with open(f'cache/{filename}', 'w', encoding='utf-8') as f:
        f.write(text)
    return jsonify({
        'success': True,
        'filename': filename
    })

# ── 章节解析 API ────────────────────────────────────────────
@app.route('/api/parse_chapter', methods=['POST'])
def parse_chapter():
    try:
        data = request.json
        chapter_text = data.get('chapter_text', '')
        
        # 获取 LLM 配置（优先使用请求中的配置）
        llm_config = data.get('llm_config', config.get('llm', {}))
        
        # 创建解析器
        parser = ChapterParser(llm_config)
        
        # 解析章节
        result = parser.parse_chapter(chapter_text)
        
        # 保存角色到角色管理器
        manager = CharacterManager()
        for char in result.get('characters', []):
            try:
                manager.add_character(char)
            except Exception as e:
                print(f"保存角色失败: {e}")
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        import traceback
        print(f"章节解析失败: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ── 角色管理 API ────────────────────────────────────────────
@app.route('/api/characters', methods=['GET'])
def get_characters():
    """获取所有角色"""
    try:
        manager = CharacterManager()
        characters = manager.get_all_characters()
        return jsonify({
            'success': True,
            'data': characters
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/characters', methods=['POST'])
def add_character():
    """添加角色"""
    try:
        data = request.json
        manager = CharacterManager()
        char_id = manager.add_character(data)
        return jsonify({
            'success': True,
            'data': {
                'char_id': char_id,
                'character': manager.get_character(char_id)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/characters/<char_id>/reference_image', methods=['POST'])
def add_reference_image(char_id):
    """为角色添加参考图像"""
    try:
        data = request.json
        image_path = data.get('image_path', '')
        manager = CharacterManager()
        manager.add_reference_image(char_id, image_path)
        return jsonify({
            'success': True,
            'data': manager.get_character(char_id)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ── 提示词生成 API ────────────────────────────────────────────
@app.route('/api/generate_prompt', methods=['POST'])
def generate_prompt():
    """生成图像提示词"""
    try:
        data = request.json
        scene_description = data.get('scene_description', '')
        characters = data.get('characters', [])
        style = data.get('style', 'cinematic')
        shot_type = data.get('shot_type', 'medium')
        
        prompt = PromptTemplates.generate_image_prompt(
            scene_description=scene_description,
            characters=characters,
            style=style,
            shot_type=shot_type
        )
        
        return jsonify({
            'success': True,
            'data': {
                'prompt': prompt
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ── 图像生成 API ────────────────────────────────────────────
@app.route('/api/generate_image', methods=['POST'])
def generate_image():
    """生成图像"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        negative_prompt = data.get('negative_prompt', '')
        width = data.get('width', 1024)
        height = data.get('height', 1024)
        steps = data.get('steps', 20)
        seed = data.get('seed')
        workflow_path = data.get('workflow_path', 'workflows/image_generation.json')
        
        # 创建 ComfyUI 封装
        comfy_config = config.get('comfyui', {})
        wrapper = ComfyUIWrapper(
            host=comfy_config.get('host', '127.0.0.1'),
            port=comfy_config.get('port', 8018)
        )
        
        # 检查连接
        if not wrapper.check_connection():
            return jsonify({
                'success': False,
                'error': 'ComfyUI 未连接，请确保 ComfyUI 正在运行'
            }), 500
        
        # 生成图像
        result = wrapper.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            seed=seed,
            workflow_path=workflow_path
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        import traceback
        print(f"图像生成失败: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ── 视频生成 API ────────────────────────────────────────────
@app.route('/api/generate_video', methods=['POST'])
def generate_video():
    """生成视频"""
    try:
        data = request.json
        image_prompt = data.get('image_prompt', '')
        motion_prompt = data.get('motion_prompt', '')
        duration = data.get('duration', 5)
        workflow_path = data.get('workflow_path', 'workflows/video_generation.json')
        
        # 创建 ComfyUI 封装
        comfy_config = config.get('comfyui', {})
        wrapper = ComfyUIWrapper(
            host=comfy_config.get('host', '127.0.0.1'),
            port=comfy_config.get('port', 8018)
        )
        
        # 检查连接
        if not wrapper.check_connection():
            return jsonify({
                'success': False,
                'error': 'ComfyUI 未连接，请确保 ComfyUI 正在运行'
            }), 500
        
        # 生成视频
        result = wrapper.generate_video(
            image_prompt=image_prompt,
            motion_prompt=motion_prompt,
            duration=duration,
            workflow_path=workflow_path
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        import traceback
        print(f"视频生成失败: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ── LLM 调用 API ────────────────────────────────────────────
@app.route('/api/llm', methods=['POST'])
def call_llm():
    try:
        data = request.json
        messages = data.get('messages', [])
        llm_config = data.get('llm_config', config.get('llm', {}))
        
        # 简单的 LLM 调用（实际应使用专门的 LLM 客户端）
        from chapter_parser import ChapterParser
        parser = ChapterParser(llm_config)
        
        # 只使用最后一条消息作为提示词
        if messages:
            prompt = messages[-1].get('content', '')
            response = parser._call_llm(
                system_prompt="你是一个有帮助的 AI 助手。",
                user_prompt=prompt
            )
            return jsonify({
                'success': True,
                'response': response
            })
        else:
            return jsonify({
                'success': False,
                'error': '未提供消息'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ── 主程序 ────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 50)
    print("AI Film Studio")
    print("=" * 50)
    print(f"项目名称: {config.get('project', {}).get('name', '未设置')}")
    print(f"ComfyUI: {config.get('comfyui', {}).get('host', '127.0.0.1')}:{config.get('comfyui', {}).get('port', 8018)}")
    print(f"LLM 模型: {config.get('llm', {}).get('model', '未设置')}")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
