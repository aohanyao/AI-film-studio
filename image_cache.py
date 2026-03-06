"""
图像缓存系统
缓存生成的图像以避免重复生成
"""

import hashlib
import json
import os
from typing import Dict, Any, Optional


class ImageCache:
    """图像缓存管理器"""
    
    def __init__(self, cache_dir: str = "cache/images"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, prompt: str) -> str:
        """生成缓存键"""
        return hashlib.md5(prompt.encode('utf-8')).hexdigest()
    
    def _get_cache_file(self, key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取图像
        
        Args:
            prompt: 提示词
            
        Returns:
            缓存的图像结果，如果不存在返回 None
        """
        key = self._get_cache_key(prompt)
        cache_file = self._get_cache_file(key)
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取缓存失败: {e}")
        
        return None
    
    def set(self, prompt: str, result: Dict[str, Any]) -> None:
        """
        将图像结果存入缓存
        
        Args:
            prompt: 提示词
            result: 图像生成结果
        """
        key = self._get_cache_key(prompt)
        cache_file = self._get_cache_file(key)
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入缓存失败: {e}")
    
    def clear(self) -> None:
        """清空所有缓存"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception as e:
            print(f"清空缓存失败: {e}")
    
    def get_cache_size(self) -> int:
        """获取缓存大小（文件数量）"""
        try:
            return len([f for f in os.listdir(self.cache_dir) if f.endswith('.json')])
        except Exception:
            return 0


if __name__ == "__main__":
    # 测试用例
    print("=" * 50)
    print("图像缓存测试")
    print("=" * 50)
    
    cache = ImageCache(cache_dir="cache/test_images")
    
    # 测试缓存
    prompt = "测试提示词"
    result = {
        "prompt_id": "test_123",
        "images": ["test_image.png"]
    }
    
    print("\n1. 设置缓存...")
    cache.set(prompt, result)
    print(f"✅ 缓存已设置")
    
    print("\n2. 获取缓存...")
    cached = cache.get(prompt)
    print(f"✅ 缓存结果: {cached}")
    
    print("\n3. 检查缓存大小...")
    size = cache.get_cache_size()
    print(f"✅ 缓存文件数: {size}")
    
    print("\n4. 清空缓存...")
    cache.clear()
    print(f"✅ 缓存已清空")
    
    print("\n✅ 测试完成")
