"""
直接测试章节解析模块（不经过服务器）
"""
import sys
sys.path.insert(0, '.')

from chapter_parser import ChapterParser
import json

print("=" * 50)
print("直接测试章节解析模块")
print("=" * 50)

# 配置
config = {
    "llm": {
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-max",
        "api_key": "sk-7a447ace618942288c48e7d1d56de58c",
        "temperature": 0.7,
        "max_tokens": 2000
    }
}

# 测试章节
test_chapter = """
第一章：初遇

深秋的午后，阳光透过咖啡馆的玻璃窗洒在木质桌面上。林小雨坐在靠窗的位置，手里捧着一杯热拿铁，眼神有些发呆。她今年二十三岁，穿着一件米白色的毛衣，长发随意地披在肩上，给人一种温柔恬静的感觉。

门铃响起，一个高大的男人推门而入。他约莫三十岁，穿着深灰色的风衣，面容冷峻，眼神锐利。这个男人叫陈默，是一名刑警，刚从警局过来。

陈默环顾四周，目光最终落在了林小雨身上。他径直走过去，在她对面坐下。
"""

try:
    print("\n创建章节解析器...")
    parser = ChapterParser(config)
    print("✅ 解析器创建成功")
    
    print("\n开始解析章节...")
    print(f"章节文本长度: {len(test_chapter)} 字符")
    
    result = parser.parse_chapter(test_chapter)
    
    print("\n✅ 解析成功！")
    print("\n" + "=" * 50)
    print("解析结果")
    print("=" * 50)
    
    # 打印角色信息
    print(f"\n📋 发现 {len(result.get('characters', []))} 个角色:")
    for idx, char in enumerate(result.get('characters', []), 1):
        print(f"\n  角色 {idx}:")
        print(f"    姓名: {char.get('name', '未知')}")
        print(f"    描述: {char.get('description', '未知')}")
        print(f"    性格: {', '.join(char.get('personality', []))}")
        print(f"    类型: {char.get('role', '未知')}")
        print(f"    重要程度: {char.get('importance', 0)}/10")
    
    # 打印场景信息
    print(f"\n🎬 发现 {len(result.get('scenes', []))} 个场景:")
    for idx, scene in enumerate(result.get('scenes', []), 1):
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
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
