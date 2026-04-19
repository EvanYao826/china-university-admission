import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import time

# 连接数据库
conn = sqlite3.connect('data/university.db')
cursor = conn.cursor()

# 目标URL
base_url = 'https://www.gaokao.cn'
search_url = f'{base_url}/school/search'

# 发送请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 获取大学列表
def get_university_list():
    universities = []
    page = 1
    
    while True:
        # 构建带分页的URL
        url = f'{search_url}?page={page}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到大学列表容器
        school_list = soup.find_all('div', class_='school-item')
        
        # 如果没有找到大学，说明已经到最后一页
        if not school_list:
            break
        
        for item in school_list:
            # 提取大学名称和链接
            name_elem = item.find('h3')
            if not name_elem:
                continue
            
            name = name_elem.text.strip()
            link_elem = name_elem.find('a')
            detail_url = f'{base_url}{link_elem["href"]}' if link_elem and 'href' in link_elem.attrs else ''
            
            # 提取大学基本信息
            info_items = item.find_all('div', class_='info-item')
            
            # 初始化信息字典
            info = {
                'name': name,
                'detail_url': detail_url,
                'location': '',
                'type': '',
                'admin': '',
                'tags': ''
            }
            
            for info_item in info_items:
                label = info_item.find('span', class_='label').text.strip() if info_item.find('span', class_='label') else ''
                value = info_item.find('span', class_='value').text.strip() if info_item.find('span', class_='value') else ''
                
                if label == '所在地':
                    info['location'] = value
                elif label == '院校类型':
                    info['type'] = value
                elif label == '主管部门':
                    info['admin'] = value
                elif label == '标签':
                    info['tags'] = value
            
            universities.append(info)
        
        # 增加页码
        page += 1
        # 避免请求过快
        time.sleep(1)
    
    return universities

# 获取大学详细信息和录取数据
def get_university_details(uni):
    if not uni['detail_url']:
        return
    
    try:
        response = requests.get(uni['detail_url'], headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取大学描述
        desc_elem = soup.find('div', class_='school-desc')
        if desc_elem:
            uni['description'] = desc_elem.text.strip()
        
        # 提取录取分数线数据
        # 这里需要根据实际页面结构进行调整
        # 示例：查找录取分数线表格
        score_tables = soup.find_all('table', class_='score-table')
        for table in score_tables:
            # 提取表格数据
            rows = table.find_all('tr')
            for row in rows[1:]:  # 跳过表头
                cells = row.find_all('td')
                if len(cells) >= 5:
                    province = cells[0].text.strip()
                    year = cells[1].text.strip()
                    category = cells[2].text.strip()
                    batch = cells[3].text.strip()
                    min_score = cells[4].text.strip()
                    
                    # 检查是否是有效的年份
                    if year.isdigit() and int(year) >= 2020:
                        # 插入录取数据
                        cursor.execute('''
                            INSERT INTO undergraduate_admissions (university_id, province, year, category, batch, min_score, source_url)
                            VALUES ((SELECT id FROM universities WHERE name = ?), ?, ?, ?, ?, ?, ?)
                        ''', (uni['name'], province, int(year), category, batch, min_score, uni['detail_url']))
                        print(f'插入 {uni["name"]} {year}年 {province} 录取数据')
        
    except Exception as e:
        print(f'获取 {uni["name"]} 详细信息失败: {e}')
    
    # 避免请求过快
    time.sleep(1)

# 主函数
def main():
    # 获取大学列表
    universities = get_university_list()
    print(f'共找到 {len(universities)} 所大学')
    
    # 处理并插入数据
    for uni in universities:
        # 提取省份和城市
        location = uni['location']
        if location:
            parts = location.split(' ')
            province = parts[0] if len(parts) > 0 else ''
            city = parts[1] if len(parts) > 1 else ''
        else:
            province = ''
            city = ''
        
        # 提取层次标签
        tags = uni['tags']
        level = []
        if '985' in tags:
            level.append('985')
        if '211' in tags:
            level.append('211')
        if '双一流' in tags:
            level.append('双一流')
        level_str = ' '.join(level)
        
        # 检查大学是否已存在
        cursor.execute('SELECT id FROM universities WHERE name = ?', (uni['name'],))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有大学信息
            cursor.execute('''
                UPDATE universities 
                SET type = ?, level = ?, province = ?, city = ?, tags = ?, description = ? 
                WHERE id = ?
            ''', (uni['type'], level_str, province, city, uni['tags'], uni.get('description', ''), existing[0]))
            print(f'更新大学: {uni["name"]}')
        else:
            # 插入新大学
            cursor.execute('''
                INSERT INTO universities (name, type, level, province, city, tags, description) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (uni['name'], uni['type'], level_str, province, city, uni['tags'], uni.get('description', '')))
            print(f'插入大学: {uni["name"]}')
        
        # 获取详细信息和录取数据
        get_university_details(uni)
        
        # 每处理10所大学提交一次事务
        if (universities.index(uni) + 1) % 10 == 0:
            conn.commit()
            print('提交事务')
    
    # 提交最终事务并关闭连接
    conn.commit()
    conn.close()
    
    print(f'共处理 {len(universities)} 所大学')

if __name__ == '__main__':
    main()
