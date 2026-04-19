"""
基本使用示例
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main as crawler_main
import argparse

def example_single_school():
    """示例1: 爬取单个学校的基本数据"""
    print("示例1: 爬取单个学校的基本数据")
    print("-" * 50)

    # 模拟命令行参数
    sys.argv = ['main.py', '140', '--test']

    try:
        crawler_main()
    except SystemExit as e:
        print(f"程序退出代码: {e.code}")

    print()

def example_custom_years():
    """示例2: 爬取指定年份"""
    print("示例2: 爬取指定年份")
    print("-" * 50)

    sys.argv = ['main.py', '140', '-y', '2023', '2022', '-p', '北京', '上海', '--test']

    try:
        crawler_main()
    except SystemExit as e:
        print(f"程序退出代码: {e.code}")

    print()

def example_with_database():
    """示例3: 使用自定义数据库"""
    print("示例3: 使用自定义数据库")
    print("-" * 50)

    db_path = r'E:\VSproject\China-University-Admission\data\test.db'
    sys.argv = ['main.py', '140', '-d', db_path, '--test']

    try:
        crawler_main()
    except SystemExit as e:
        print(f"程序退出代码: {e.code}")

    print()

def example_resume_feature():
    """示例4: 断点续传功能"""
    print("示例4: 断点续传功能")
    print("-" * 50)

    # 第一次运行（部分数据）
    print("第一次运行（模拟中断）...")
    sys.argv = ['main.py', '140', '-p', '北京', '上海', '--test', '--resume']

    try:
        crawler_main()
    except SystemExit as e:
        print(f"第一次运行退出代码: {e.code}")

    # 第二次运行（继续）
    print("\n第二次运行（继续爬取）...")
    sys.argv = ['main.py', '140', '-p', '北京', '上海', '广东', '--test', '--resume']

    try:
        crawler_main()
    except SystemExit as e:
        print(f"第二次运行退出代码: {e.code}")

    print()

def example_no_save_mode():
    """示例5: 仅爬取不保存模式"""
    print("示例5: 仅爬取不保存模式")
    print("-" * 50)

    sys.argv = ['main.py', '140', '--no-save', '--test']

    try:
        crawler_main()
    except SystemExit as e:
        print(f"程序退出代码: {e.code}")

    print()

def example_batch_processing():
    """示例6: 批量处理多个学校"""
    print("示例6: 批量处理多个学校")
    print("-" * 50)

    school_ids = ['140', '141', '142']  # 示例学校ID

    for school_id in school_ids:
        print(f"\n处理学校: {school_id}")
        print("-" * 30)

        sys.argv = ['main.py', school_id, '--test']

        try:
            crawler_main()
        except SystemExit as e:
            print(f"学校 {school_id} 处理完成，退出代码: {e.code}")

        # 避免请求过快
        import time
        time.sleep(3)

    print()

def main():
    """运行所有示例"""
    print("高考数据爬虫系统使用示例")
    print("=" * 60)

    examples = [
        example_single_school,
        example_custom_years,
        example_with_database,
        example_resume_feature,
        example_no_save_mode,
        example_batch_processing
    ]

    for i, example_func in enumerate(examples, 1):
        print(f"\n示例 {i}:")
        try:
            example_func()
        except Exception as e:
            print(f"示例执行失败: {e}")

        # 示例间暂停
        import time
        time.sleep(1)

    print("\n所有示例执行完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()