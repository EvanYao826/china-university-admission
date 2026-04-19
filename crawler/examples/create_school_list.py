"""
创建学校ID列表文件
"""
import json

def create_sample_school_list():
    """创建示例学校列表"""
    # 一些常见高校的ID（示例）
    schools = [
        "140",  # 示例学校
        "141",  # 示例学校2
        "142",  # 示例学校3
        "143",  # 示例学校4
        "144",  # 示例学校5
        # 可以添加更多学校ID
    ]

    # 保存到文件
    with open("schools.txt", "w", encoding="utf-8") as f:
        for school in schools:
            f.write(f"{school}\n")

    print(f"创建学校列表文件: schools.txt")
    print(f"包含 {len(schools)} 个学校")

def create_school_list_from_json():
    """从JSON文件创建学校列表"""
    # 示例JSON数据
    school_data = [
        {"id": "140", "name": "北京大学", "province": "北京"},
        {"id": "141", "name": "清华大学", "province": "北京"},
        {"id": "142", "name": "复旦大学", "province": "上海"},
        {"id": "143", "name": "上海交通大学", "province": "上海"},
        {"id": "144", "name": "浙江大学", "province": "浙江"},
        {"id": "145", "name": "南京大学", "province": "江苏"},
        {"id": "146", "name": "武汉大学", "province": "湖北"},
        {"id": "147", "name": "华中科技大学", "province": "湖北"},
        {"id": "148", "name": "中山大学", "province": "广东"},
        {"id": "149", "name": "西安交通大学", "province": "陕西"},
    ]

    # 保存ID列表
    with open("schools_from_json.txt", "w", encoding="utf-8") as f:
        for school in school_data:
            f.write(f"{school['id']}\n")

    # 保存完整信息
    with open("schools_info.json", "w", encoding="utf-8") as f:
        json.dump(school_data, f, ensure_ascii=False, indent=2)

    print(f"创建学校列表文件: schools_from_json.txt")
    print(f"创建学校信息文件: schools_info.json")
    print(f"包含 {len(school_data)} 个学校")

def create_regional_school_lists():
    """创建按地区分组的学校列表"""
    regions = {
        "north": ["140", "141"],  # 北京地区
        "east": ["142", "143", "144", "145"],  # 华东地区
        "central": ["146", "147"],  # 华中地区
        "south": ["148"],  # 华南地区
        "west": ["149"],  # 西部地区
    }

    for region, schools in regions.items():
        filename = f"schools_{region}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for school in schools:
                f.write(f"{school}\n")

        print(f"创建地区列表: {filename} ({len(schools)} 个学校)")

def create_test_school_list():
    """创建测试用学校列表"""
    test_schools = [
        "140",  # 主要测试学校
        "999",  # 不存在的学校（测试错误处理）
    ]

    with open("test_schools.txt", "w", encoding="utf-8") as f:
        for school in test_schools:
            f.write(f"{school}\n")

    print(f"创建测试列表: test_schools.txt")
    print(f"包含 {len(test_schools)} 个学校（包含错误测试）")

def main():
    """主函数"""
    print("创建学校ID列表文件")
    print("=" * 60)

    print("\n1. 创建示例学校列表")
    create_sample_school_list()

    print("\n2. 从JSON创建学校列表")
    create_school_list_from_json()

    print("\n3. 创建按地区分组列表")
    create_regional_school_lists()

    print("\n4. 创建测试列表")
    create_test_school_list()

    print("\n" + "=" * 60)
    print("文件创建完成！")
    print("\n使用说明:")
    print("1. 使用 schools.txt 进行基本测试")
    print("2. 使用 schools_from_json.txt 进行完整测试")
    print("3. 使用 test_schools.txt 进行错误处理测试")
    print("4. 使用 schools_*.txt 进行地区分组测试")

if __name__ == "__main__":
    main()