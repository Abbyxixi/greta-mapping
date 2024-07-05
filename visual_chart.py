import json
import re
import numpy as np
import matplotlib.pyplot as plt


with open('greta_kompetenzmodell_2-0_1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('greta_results.json', 'r', encoding='utf-8') as f:
    result_data = json.load(f)


def get_color(achievement):
    if 0 <= achievement <= 0.25:
        return '#C0C0C0'
    elif 0.25 < achievement <= 0.5:
        return '#C4D4A0'
    elif 0.5 < achievement <= 0.75:
        return '#A4B97F'
    elif 0.75 < achievement <= 1:
        return '#8A9A5B'


def normalize_id(id_str):
    return re.sub(r'[^\w\s]', '', id_str).replace(" ", "").lower()


facet_scores = {normalize_id(item['id']): item['achievement'] for item in result_data["Facet Scores"]}
area_scores = {normalize_id(item['id']): item['achievement'] for item in result_data["Area Scores"]}
aspect_scores = {normalize_id(item['id']): item['achievement'] for item in result_data["Aspect Scores"]}

def parse_competence_facet(facet_data, path):
    full_id = normalize_id(f"{path}/{facet_data['ID']}")
    achievement = facet_scores.get(full_id, 0)
    color = get_color(achievement)
    return {
        'name': facet_data['Name'],
        'id': facet_data['ID'],
        'description': '\n'.join(facet_data.get('Kompetenzanforderungen', [])),
        'color': color
    }

def parse_competence_area(area_data, path):
    full_id = normalize_id(f"{path}/{area_data['ID']}")
    achievement = area_scores.get(full_id, 0)
    color = get_color(achievement)
    facets = [parse_competence_facet(facet, full_id) for facet in area_data.get('Kompetenzfacetten', [])]
    return {
        'name': area_data['Name'],
        'id': area_data['ID'],
        'facets': facets,
        'color': color,
        'facet_count': len(facets)  
    }

def parse_competence_aspect(aspect_data):
    full_id = normalize_id(aspect_data['ID'])
    achievement = aspect_scores.get(full_id, 0)
    color = get_color(achievement)
    areas = [parse_competence_area(area, full_id) for area in aspect_data.get('Kompetenzbereiche', [])]
    facet_count = sum(area['facet_count'] for area in areas)  
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


competence_tree_data = data['Kompetenzmodell']
competence_tree = parse_competence_tree(competence_tree_data)


labels1 = [aspect['name'] for aspect in competence_tree['aspects']]
sizes1 = [aspect['facet_count'] for aspect in competence_tree['aspects']]
colors1 = [aspect['color'] for aspect in competence_tree['aspects']]

labels3 = [area['name'] for aspect in competence_tree['aspects'] for area in aspect['areas']]
sizes3 = [len(area['facets']) for aspect in competence_tree['aspects'] for area in aspect['areas']]
colors3 = [area['color'] for aspect in competence_tree['aspects'] for area in aspect['areas']]

labels2 = [facet['name'] for aspect in competence_tree['aspects'] for area in aspect['areas'] for facet in area['facets']]
sizes2 = [1 for aspect in competence_tree['aspects'] for area in aspect['areas'] for facet in area['facets']]
colors2 = [facet['color'] for aspect in competence_tree['aspects'] for area in aspect['areas'] for facet in area['facets']]

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




labels1 = [split_text(label, 25) for label in labels1]
labels2 = [split_text(label, 17) for label in labels2]
labels3 = [split_text(label, 15) for label in labels3]

fig, ax = plt.subplots(figsize=(12, 12))


wedges1, texts1 = ax.pie(sizes1, colors=colors1, radius=1.3, startangle=90, wedgeprops=dict(width=0.25, edgecolor='w'))


wedges2, texts2 = ax.pie(sizes2, colors=colors2, radius=1.05, startangle=90, wedgeprops=dict(width=0.5, edgecolor='w'))


wedges3, texts3 = ax.pie(sizes3, colors=colors3, radius=0.55, startangle=90, wedgeprops=dict(width=0.37, edgecolor='w'))



for i, p in enumerate(wedges1):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang)) * 1.15
    x = np.cos(np.deg2rad(ang)) * 1.15
    rotation = ang + 270 if ang <= 180 else ang - 90 
    ax.annotate(labels1[i], xy=(x, y), xytext=(x, y), textcoords='data',
                ha='center', va='center', rotation=rotation, fontsize=10, rotation_mode='anchor')


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


center_text = "Professionelle\nHandlungs-\nkompetenz\nLehrender"
ax.text(0, 0, center_text, horizontalalignment='center', verticalalignment='center', fontsize=8, fontweight='bold', color='black')


ax.axis('equal')  

plt.tight_layout()
plt.show()


plt.savefig('greta_kompetenzmodell.jpg', format='jpg', bbox_inches='tight', dpi=300)

print("JPG file generated successfully.")
