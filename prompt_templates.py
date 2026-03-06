"""
提示词模板系统
用于生成不同场景的图像和视频提示词
"""


class PromptTemplates:
    """提示词模板管理器"""
    
    # 图像风格模板
    IMAGE_STYLES = {
        "realistic": {
            "base": "photorealistic, 8K, ultra detailed, sharp focus",
            "lighting": "natural lighting, soft shadows",
            "camera": "professional photography, depth of field"
        },
        "cinematic": {
            "base": "cinematic lighting, movie quality, film grain",
            "lighting": "dramatic lighting, volumetric lighting",
            "camera": "anamorphic lens, cinematic composition"
        },
        "anime": {
            "base": "anime style, vibrant colors, clean lines",
            "lighting": "soft anime lighting",
            "camera": "manga art style"
        }
    }
    
    # 镜头类型模板
    SHOT_TYPES = {
        "wide": {
            "name": "全景",
            "description": "wide shot, full scene visible",
            "camera": "wide angle lens",
            "keywords": ["environment", "landscape", "surroundings"]
        },
        "medium": {
            "name": "中景",
            "description": "medium shot, waist up",
            "camera": "standard lens",
            "keywords": ["character", "action", "interaction"]
        },
        "closeup": {
            "name": "特写",
            "description": "close-up shot, face and shoulders",
            "camera": "portrait lens, bokeh",
            "keywords": "emotions", "expressions", "details"
        },
        "extreme_closeup": {
            "name": "大特写",
            "description": "extreme close-up, eyes or mouth",
            "camera": "macro lens",
            "keywords": ["intense emotions", "micro expressions"]
        }
    }
    
    @classmethod
    def generate_image_prompt(
        cls,
        scene_description: str,
        characters: list = None,
        style: str = "cinematic",
        shot_type: str = "medium",
        additional_tags: list = None
    ) -> str:
        """
        生成图像提示词
        
        Args:
            scene_description: 场景描述
            characters: 角色列表（每个角色包含 name 和 consistency_prompt）
            style: 风格（realistic/cinematic/anime）
            shot_type: 镜头类型（wide/medium/closeup/extreme_closeup）
            additional_tags: 额外标签
            
        Returns:
            完生成的图像提示词
        """
        # 基础风格
        style_template = cls.IMAGE_STYLES.get(style, cls.IMAGE_STYLES["cinematic"])
        
        # 镜头类型
        shot_template = cls.SHOT_TYPES.get(shot_type, cls.SHOT_TYPES["medium"])
        
        # 构建提示词
        prompt_parts = []
        
        # 1. 添加角色一致性提示词
        if characters:
            for char in characters:
                consistency = char.get('consistency_prompt', '')
                if consistency:
                    prompt_parts.append(consistency)
        
        # 2. 添加场景描述
        if scene_description:
            prompt_parts.append(scene_description)
        
        # 3. 添加风格标签
        prompt_parts.append(style_template["base"])
        prompt_parts.append(style_template["lighting"])
        
        # 4. 添加镜头类型
        prompt_parts.append(shot_template["description"])
        prompt_parts.append(shot_template["camera"])
        
        # 5. 添加额外标签
        if additional_tags:
            prompt_parts.extend(additional_tags)
        
        # 合并并去重
        all_tags = []
        seen = set()
        for part in prompt_parts:
            words = [w.strip() for w in part.split(',')]
            for word in words:
                if word and word.lower() not in seen:
                    seen.add(word.lower())
                    all_tags.append(word)
        
        return ', '.join(all_tags)
    
    @classmethod
    def generate_bilingual_prompt(
        cls,
        scene_description: str,
        characters: list = None,
        style: str = "cinematic",
        shot_type: str = "medium"
    ) -> dict:
        """
        生成中英双语提示词
        
        Args:
            scene_description: 场景描述
            characters: 角色列表
            style: 风格
            shot_type: 镜头类型
            
        Returns:
            包含 cn（中文）和 en（英文）的字典
        """
        # 生成中文提示词
        cn_prompt = cls.generate_image_prompt(
            scene_description,
            characters,
            style,
            shot_type
        )
        
        # 简单的英文转换（实际应用中应使用翻译 API）
        en_prompt = cn_prompt  # 这里简化处理
        
        return {
            "cn": cn_prompt,
            "en": en_prompt
        }
    
    @classmethod
    def generate_video_prompt(
        cls,
        image_prompt: str,
        motion_description: str = None,
        duration: str = "5s"
    ) -> dict:
        """
        生成视频提示词
        
        Args:
            image_prompt: 图像提示词
            motion_description: 运动描述
            duration: 视频时长
            
        Returns:
            视频生成参数
        """
        return {
            "image_prompt": image_prompt,
            "motion_prompt": motion_description or "subtle movement",
            "duration": duration,
            "fps": 24,
            "quality": "high"
        }


if __name__ == "__main__":
    # 测试用例
    print("=" * 50)
    print("提示词模板测试")
    print("=" * 50)
    
    # 测试数据
    scene = "咖啡馆，阳光透过窗户洒在木质桌面上"
    
    characters = [
        {
            "name": "林小雨",
            "consistency_prompt": "23岁女性，米白色毛衣，长发，温柔恬静， same character, ID: char_lin_xiaoyu"
        }
    ]
    
    print("\n1. 测试图像提示词生成...")
    prompt = PromptTemplates.generate_image_prompt(
        scene_description=scene,
        characters=characters,
        style="cinematic",
        shot_type="medium"
    )
    print(f"提示词: {prompt}")
    
    print("\n2. 测试不同镜头类型...")
    for shot_type in ["wide", "medium", "closeup"]:
        prompt = PromptTemplates.generate_image_prompt(
            scene_description=scene,
            characters=characters,
            style="cinematic",
            shot_type=shot_type
        )
        print(f"{shot_type}: {prompt[:100]}...")
    
    print("\n3. 测试双语提示词...")
    bilingual = PromptTemplates.generate_bilingual_prompt(
        scene_description=scene,
        characters=characters
    )
    print(f"中文: {bilingual['cn'][:100]}...")
    print(f"英文: {bilingual['en'][:100]}...")
    
    print("\n4. 测试视频提示词...")
    video_params = PromptTemplates.generate_video_prompt(
        image_prompt=prompt,
        motion_description="林小雨微微转头，阳光照在脸上"
    )
    print(f"视频参数: {json.dumps(video_params, ensure_ascii=False, indent=2)}")
    
    print("\n✅ 测试完成")
