"""
ComfyUI API 封装
用于调用 ComfyUI 生成图像和视频
"""

import requests
import json
import time
import uuid


class ComfyUIWrapper:
    """ComfyUI API 封装"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8018):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
    
    def check_connection(self) -> bool:
        """检查 ComfyUI 连接"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def load_workflow(self, workflow_path: str) -> dict:
        """
        加载工作流文件
        
        Args:
            workflow_path: 工作流文件路径
            
        Returns:
            工作流字典
        """
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _queue_prompt(self, workflow: dict) -> str:
        """
        将工作流加入队列
        
        Args:
            workflow: 工作流字典
            
        Returns:
            prompt ID
        """
        # 生成 prompt ID
        prompt_id = str(uuid.uuid4())
        
        # 构造请求
        payload = {
            "prompt": workflow,
            "client_id": "ai_film_studio"
        }
        
        # 发送请求
        response = requests.post(
            f"{self.base_url}/prompt",
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            raise Exception(f"队列提示失败: {response.text}")
        
        return prompt_id
    
    def _get_history(self, prompt_id: str) -> dict:
        """
        获取执行历史
        
        Args:
            prompt_id: prompt ID
            
        Returns:
            执行历史
        """
        response = requests.get(
            f"{self.base_url}/history/{prompt_id}",
            timeout=5
        )
        
        if response.status_code != 200:
            return {}
        
        return response.json()
    
    def _wait_for_completion(self, prompt_id: str, timeout: int = 300) -> dict:
        """
        等待执行完成
        
        Args:
            prompt_id: prompt ID
            timeout: 超时时间（秒）
            
        Returns:
            执行结果
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            history = self._get_history(prompt_id)
            
            if prompt_id in history:
                execution = history[prompt_id]
                status = execution.get("status", {})
                
                if status.get("completed", False):
                    return execution
            
            time.sleep(1)
        
        raise Exception(f"执行超时（{timeout}秒）")
    
    def _get_output_image(self, execution: dict, node_id: str = None) -> dict:
        """
        获取输出图像
        
        Args:
            execution: 执行结果
            node_id: 节点 ID（可选，如果不指定则返回第一个）
            
        Returns:
            图像信息字典
        """
        outputs = execution.get("outputs", {})
        
        if node_id:
            if node_id in outputs:
                return outputs[node_id]
        else:
            # 返回第一个输出
            for node_id, output in outputs.items():
                if "images" in output:
                    return output
        
        return {}
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        seed: int = None,
        workflow_path: str = "workflows/image_generation.json"
    ) -> dict:
        """
        生成图像
        
        Args:
            prompt: 提示词
            negative_prompt: 负面提示词
            width: 图像宽度
            height: 图像高度
            steps: 采样步数
            seed: 随机种子
            workflow_path: 工作流文件路径
            
        Returns:
            生成结果
        """
        # 加载工作流
        workflow = self.load_workflow(workflow_path)
        
        # 查找节点并设置参数
        for node_id, node in workflow.items():
            if node.get("class_type") == "KSampler":
                # 设置随机种子
                if seed is not None:
                    node["inputs"]["seed"] = seed
                else:
                    node["inputs"]["seed"] = int(time.time())
                
                # 设置步数
                node["inputs"]["steps"] = steps
            
            elif node.get("class_type") == "CLIPTextEncode":
                # 设置提示词
                if node.get("inputs", {}).get("text"):
                    node["inputs"]["text"] = prompt
            
            elif node.get("class_type") == "EmptyLatentImage":
                # 设置图像尺寸
                node["inputs"]["width"] = width
                node["inputs"]["height"] = height
            
            elif node.get("class_type") == "CheckpointLoaderSimple":
                # 设置模型（可根据需要修改）
                pass
        
        # 队列提示词
        prompt_id = self._queue_prompt(workflow)
        
        # 等待完成
        execution = self._wait_for_completion(prompt_id)
        
        # 获取输出图像
        output = self._get_output_image(execution)
        
        return {
            "prompt_id": prompt_id,
            "success": True,
            "output": output
        }
    
    def download_image(self, filename: str, subfolder: str = "", image_type: str = "output") -> bytes:
        """
        下载图像
        
        Args:
            filename: 文件名
            subfolder: 子文件夹
            image_type: 图像类型
            
        Returns:
            图像数据
        """
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": image_type
        }
        
        response = requests.get(
            f"{self.base_url}/view",
            params=params,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"下载图像失败: {response.text}")
        
        return response.content
    
    def generate_video(
        self,
        image_prompt: str,
        motion_prompt: str = "",
        duration: int = 5,
        workflow_path: str = "workflows/video_generation.json"
    ) -> dict:
        """
        生成视频
        
        Args:
            image_prompt: 图像提示词
            motion_prompt: 运动提示词
            duration: 视频时长（秒）
            workflow_path: 工作流文件路径
            
        Returns:
            生成结果
        """
        # TODO: 实现视频生成逻辑
        # 这需要根据具体的 ComfyUI 视频生成节点进行适配
        
        raise NotImplementedError("视频生成功能待实现")


if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # 测试用例
    print("=" * 50)
    print("ComfyUI 封装测试")
    print("=" * 50)
    
    # 创建封装实例
    wrapper = ComfyUIWrapper()
    
    print("\n检查 ComfyUI 连接...")
    if wrapper.check_connection():
        print("✅ ComfyUI 连接成功")
        
        # 测试生成图像（需要工作流文件）
        print("\n尝试加载工作流文件...")
        try:
            workflow = wrapper.load_workflow("workflows/image_generation.json")
            print(f"✅ 工作流加载成功，包含 {len(workflow)} 个节点")
            
            # 注意：实际生成图像需要有效的 ComfyUI 工作流
            # print("\n生成测试图像...")
            # result = wrapper.generate_image("a beautiful sunset over the ocean")
            # print(f"✅ 图像生成成功: {result}")
            
        except FileNotFoundError:
            print("⚠️ 工作流文件未找到: workflows/image_generation.json")
            print("   (这是正常的，需要手动创建工作流文件)")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            
    else:
        print("❌ ComfyUI 连接失败")
        print("   请确保 ComfyUI 正在运行 (http://127.0.0.1:8018)")
    
    print("\n✅ 测试完成")
