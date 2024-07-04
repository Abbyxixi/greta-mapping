import json
import numpy as np
import matplotlib.pyplot as plt

# 读取 JSON 文件
with open('greta_kompetenzmodell_2-0_1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


# 定义颜色
color_map = {
    'Professionelle Werthaltungen und Überzeugungen': '#b3cde3',
    'Professionelle Selbststeuerung': '#ccebc5',
    'Fach- und feldspezifisches Wissen': '#decbe4',
    'Berufspraktisches Wissen und Können': '#fed9a6'
}

def get_color(aspect_name):
    return color_map.get(aspect_name, "#C0C0C0")  # 默认颜色为灰色

# 解析 JSON 数据
def parse_competence_facet(facet_data, color):
    return {
        'name': facet_data['Name'],
        'id': facet_data['ID'],
        'description': '\n'.join(facet_data.get('Kompetenzanforderungen', [])),
        'color': color
    }

def parse_competence_area(area_data, color):
    facets = [parse_competence_facet(facet, color) for facet in area_data.get('Kompetenzfacetten', [])]
    return {
        'name': area_data['Name'],
        'id': area_data['ID'],
        'facets': facets,
        'color': color,
        'facet_count': len(facets)
    }

def parse_competence_aspect(aspect_data):
    color = get_color(aspect_data['Name'])
    areas = [parse_competence_area(area, color) for area in aspect_data.get('Kompetenzbereiche', [])]
    facet_count = sum(area['facet_count'] for area in areas)  # 计算所有 area 中 facet 的总数
    return {
        'name': aspect_data['Name'],
        'id': aspect_data['ID'],
        'areas': areas,
        'color': color,
        'facet_count': facet_count
    }

def parse_competence_tree(tree_data):
    aspects = [parse_competence_aspect(aspect) for aspect in tree_data['Kompetenzaspekte']]
    return {
        'name': tree_data['Name'],
        'id': tree_data['ID'],
        'aspects': aspects,
        'color': "#C0C0C0"
    }

# 创建 competence tree 数据
competence_tree_data = data['Kompetenzmodell']
competence_tree = parse_competence_tree(competence_tree_data)

# 准备数据
labels1 = [aspect['name'] for aspect in competence_tree['aspects']]
sizes1 = [aspect['facet_count'] for aspect in competence_tree['aspects']]
colors1 = [aspect['color'] for aspect in competence_tree['aspects']]
print(sizes1,colors1)
labels3 = [area['name'] for aspect in competence_tree['aspects'] for area in aspect['areas']]
sizes3 = [len(area['facets']) for aspect in competence_tree['aspects'] for area in aspect['areas']]
colors3 = [area['color'] for aspect in competence_tree['aspects'] for area in aspect['areas']]
print(sizes3,colors3)
labels2 = [facet['name'] for aspect in competence_tree['aspects'] for area in aspect['areas'] for facet in area['facets']]
sizes2 = [1 for aspect in competence_tree['aspects'] for area in aspect['areas'] for facet in area['facets']]
colors2 = [facet['color'] for aspect in competence_tree['aspects'] for area in aspect['areas'] for facet in area['facets']]
print(sizes2,colors2)
def split_text(text, max_length):
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + 1 <= max_length:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word
            
    if current_line:
        lines.append(current_line)
        
    return "\n".join(lines)

# 设置最大行宽
max_line_length = 15

# 拆分长文本标签
#labels1 = [split_text(label, max_line_length) for label in labels1]
labels2 = [split_text(label, max_line_length) for label in labels2]
labels3 = [split_text(label, max_line_length) for label in labels3]

fig, ax = plt.subplots(figsize=(12, 12))

# 第一层环形图
wedges1, texts1 = ax.pie(sizes1, colors=colors1, radius=1.3, startangle=90, wedgeprops=dict(width=0.3, edgecolor='w'))

# 第二层环形图
wedges2, texts2 = ax.pie(sizes2, colors=colors2, radius=1, startangle=90, wedgeprops=dict(width=0.45, edgecolor='w'))

# 第三层环形图
wedges3, texts3 = ax.pie(sizes3, colors=colors3, radius=0.55, startangle=90, wedgeprops=dict(width=0.37, edgecolor='w'))

# 添加文本到每个扇区的中间位置，aspect 的文本沿环形分布
for i, p in enumerate(wedges1):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang)) * 1.15
    x = np.cos(np.deg2rad(ang)) * 1.15
    rotation = ang + 270 if ang <= 180 else ang - 90  # 确保文本不倒立
    ax.annotate(labels1[i], xy=(x, y), xytext=(x, y), textcoords='data',
                ha='center', va='center', rotation=rotation, fontsize=10, rotation_mode='anchor')

# 添加文本到每个扇区的中间位置，area 和 facet 的文本从中心向外发散
for i, p in enumerate(wedges2):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang)) * 0.58
    x = np.cos(np.deg2rad(ang)) * 0.58
    ax.text(x, y, labels2[i], horizontalalignment='left', verticalalignment='center', fontsize=8, rotation=ang, rotation_mode='anchor')

for i, p in enumerate(wedges3):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang)) * 0.21
    x = np.cos(np.deg2rad(ang)) * 0.21
    ax.text(x, y, labels3[i], horizontalalignment='left', verticalalignment='center', fontsize=8, rotation=ang, rotation_mode='anchor')

# 在中心添加文本
center_text = "Professionelle\nHandlungs-\nkompetenz\nLehrender"
ax.text(0, 0, center_text, horizontalalignment='center', verticalalignment='center', fontsize=8, fontweight='bold', color='black')

# 确保饼图是圆形的
ax.axis('equal')  

plt.tight_layout()
plt.show()

# 保存为 JPG 文件
plt.savefig('greta_kompetenzmodell.jpg', format='jpg', bbox_inches='tight', dpi=300)

print("JPG file generated successfully.")
