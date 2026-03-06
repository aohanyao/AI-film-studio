"""
快速测试章节解析功能（无交互版）
"""

import json
import requests
import sys


def test_chapter_parser():
    """测试章节解析 API"""
    
    # 测试章节
    test_chapter = """
    第一章：初遇
    
    深秋的午后，阳光透过咖啡馆的玻璃窗洒在木质桌面上。林小雨坐在靠窗的位置，手里捧着一杯热拿铁，眼神有些发呆。她今年二十三岁，穿着一件米白色的毛衣，长发随意地披在肩上，给人一种温柔恬静的感觉。
    
    门铃响起，一个高大的男人推门而入。他约默三十岁，穿着深灰色的风衣，面容冷峻，眼神锐利。这个男人叫陈默，是一名刑警，刚从警局过来。
    
    陈默环顾四周，目光最终落在了林小雨身上。他径直走过去，在她对面坐下。
    """
    
    print("=" * 50)
    print("章节解析测试")
    print("=" * 50)
    
    try:
        # 先测试服务器是否在线
        print("\n检查服务器状态...")
        health_response = requests.get('http://127.0.0.1:5000', timeout=5)
        print("✅ 服务器在线")
        
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        print("请确保 app.py 正在运行")
        return False
    
    # 构造请求数据
    data = {
        "chapter_text": test_chapter,
        # 不传 config，让服务器使用 settings.json 中的配置
    }
    
    try:
        # 调用 API
        print("\n正在调用章节解析 API...")
        print(f"章节文本长度: {len(test_chapter)} 字符")
        print(f"API 地址: http://127.0.0.1:5000/api/parse_chapter")
        
        response = requests.post(
            'http://127.0.0.1:5000/api/parse_chapter',
            json=data,
            timeout=300  # 5 分钟超时
        )
        
        print(f"响应状态码: {response.status_code}")
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("\n✅ 解析成功！")
                print("\n" + "=" * 50)
                print("解析结果")
                print("=" * 50)
                
                data = result['data']
                
                # 打印角色信息
                print(f"\n📋 发现 {len(data.get('characters', []))} 个角色:")
                for idx, char in enumerate(data.get('characters', []), 1):
                    print(f"\n  角色 {idx}:")
                    print(f"    姓名: {char.get('name', '未知')}")
                    print(f"    描述: {char.get('description', '未知')}")
                    print(f"    性格: {', '.join(char.get('personality', []))}")
                    print(f"    类型: {char.get('role', '未知')}")
                    print(f"    重要程度: {char.get('importance', 0)}/10")
                
                # 打印场景信息
                print(f"\n🎬 发现 {len(data.get('scenes', []))} 个场景:")
                for idx, scene in enumerate(data.get('scenes', []), 1):
                    print(f"\n  场景 {idx}:")
                    print(f"    地点: {scene.get('location', '未知')}")
                    print(f"    描述: {scene.get('description', '未知')}")
                    print(f"    时间: {scene.get('time', '未知')}")
                    print(f"    氛围: {', '.join(scene.get('atmosphere', []))}")
                    print(f"    重要程度: {scene.get('importance', 0)}/10")
                
                # 保存到文件
                output_file = "test_chapter_output.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n📁 结果已保存到: {output_file}")
                
                print("\n" + "=" * 50)
                print("测试完成")
                print("=" * 50)
                
                return True
                
            else:
                print(f"\n❌ 解析失败: {result.get('error', '未知错误')}")
                return False
                
        else:
            print(f"\n❌ API 调用失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时（5分钟）")
        print("可能原因：")
        print("  1. LLM API 响应时间过长")
        print("  2. 网络连接问题")
        print("  3. API Key 无效")
        return False
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_chapter_parser()
