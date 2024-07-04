import json

def load_xapi_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        xapi_data = json.load(file)
    return xapi_data

def normalize_score(score):
    min_score = score["min"]
    max_score = score["max"]
    raw_score = score["raw"]
    return (raw_score - min_score) / (max_score - min_score)

def map_activities_to_competencies(xapi_activities, competency_hierarchy, mapping_table_resource):
    # Extract the sub-competency (facet) scores from the xAPI data
    sub_competency_scores = {}
    sub_competency_resources = {}
    for activity in xapi_activities:
        statement = activity["statement"]
        context = statement["context"]["extensions"]["learningObjectMetadata"]
        facet = context["facet"]
        area = context["area"]
        aspect = context["aspect"]
        score = normalize_score(statement["result"]["score"])
        competence_path = context["competencePath"]

        if facet not in sub_competency_scores:
            sub_competency_scores[facet] = []
        sub_competency_scores[facet].append(score)
        if facet in mapping_table_resource:
            sub_competency_resources[facet] = mapping_table_resource[facet]

    # Ensure all facets from the hierarchy are included, with default score of 0 if missing
    for aspect, areas in competency_hierarchy.items():
        for area, facets in areas.items():
            for facet in facets:
                if facet not in sub_competency_scores:
                    sub_competency_scores[facet] = [0]
                    if facet in mapping_table_resource:
                        sub_competency_resources[facet] = mapping_table_resource[facet]

    # Calculate the average scores for each sub-competency (facet)
    sub_competency_averages = {facet: sum(scores)/len(scores) for facet, scores in sub_competency_scores.items()}

    # Calculate the average scores for each area and main competency
    area_averages = {}
    aspect_averages = {}
    
    for aspect, areas in competency_hierarchy.items():
        for area, facets in areas.items():
            relevant_scores = [sub_competency_averages[facet] for facet in facets]
            area_averages[area] = sum(relevant_scores)/len(relevant_scores) if relevant_scores else 0
        
        relevant_area_scores = [area_averages[area] for area in areas]
        aspect_averages[aspect] = sum(relevant_area_scores)/len(relevant_area_scores) if relevant_area_scores else 0

    # Create the GRETA competencies structure with full paths and scores
    facet_scores = [
        {"id": f"{aspect}/{area}/{facet}", "achievement": sub_competency_averages[facet]}
        for aspect, areas in competency_hierarchy.items()
        for area, facets in areas.items()
        for facet in facets
    ]
    
    # Create the area and main competency scores structure
    area_scores = [
        {"id": f"{aspect}/{area}", "achievement": area_averages[area]}
        for aspect, areas in competency_hierarchy.items()
        for area in areas
    ]
    
    aspect_scores = [
        {"id": f"{aspect}", "achievement": aspect_averages[aspect]}
        for aspect in competency_hierarchy
    ]

    # Find the sub-competencies (facets) with scores below 0.5 and provide learning resource links
    low_score_links = []
    added_links = set()
    
    for facet, score in sub_competency_averages.items():
        if score < 0.5:  # Adjust this threshold as needed
            competence_path = mapping_table_resource[facet]
            link = {"id": f"{facet}", "link": competence_path}
            link_tuple = (link["id"], link["link"])
            if link_tuple not in added_links:
                low_score_links.append(link)
                added_links.add(link_tuple)
    
    return facet_scores, area_scores, aspect_scores, low_score_links

# Example usage:
xapi_file_path = 'greta_xapi_example1.json'
xapi_activities = load_xapi_data(xapi_file_path)

competency_hierarchy = {
    "Professionelle Selbststeuerung": {
        "Motivationale Orientierungen": [
            "Enthusiasmus",
            "Selbstwirksamkeitsüberzeugungen"
        ],
        "Selbstregulation": [
            "Engagement und Distanz",
            "Umgang mit Feedback und Kritik"
        ],
        "Berufspraktische Erfahrungen": [
            "Reflexion des eigenen Lehrhandelns",
            "Berufliche Weiterentwicklung"
        ]
    },
    "Professionelle Werteshaltungen und Überzeugungen": {
        "Berufsethos": [
            "Menschenbilder",
            "Wertvorstellungen"
        ],
        "Fachbezogene Überzeugungen": [
            "Eigenes Rollenbewusstsein",
            "Subjektive Annahmen über das Lehren und Lernen"
        ]
    },
    "Berufspraktisches Wissen und Können": {
        "Organisation": [
            "Kooperation mit Eltern",
            "Kollegiale Zusammenarbeit und Netzwerken"
        ],
        "Didaktik und Methodik": [
            "Lerninhalte und -ziele",
            "Methoden, Medien und Materialien",
            "Outcomeorientierung",
            "Rahmenbedingungen und Lernumgebungen"
        ],
        "Kommunikation und Interaktion": [
            "Moderation und Steuerung von Gruppen",
            "Professionelle Kommunikation"
        ],
        "Beratung / individualisierte Lernunterstützung": [
            "Diagnostik und Lernberatung",
            "Teilnehmendenorientierung"
        ],
        "Fachdidatik":[]
    },
    "Fach- und feldspezifisches Wissen": {
        "Feldbezug": [
            "Curriculare und institutionelle Rahmenbedingungen",
            "Feldspezifisches Wissen",
            "Adressaten und Adressaten"
        ],
        "Fachinhalt":[]
    }
}

mapping_table_resource = {
    "Enthusiasmus": "http://example.com/Enthusiasmus",
    "Selbstwirksamkeitsüberzeugungen": "http://example.com/Selbstwirksamkeitsüberzeugungen",
    "Engagement und Distanz": "http://example.com/Engagement",
    "Umgang mit Feedback und Kritik": "http://example.com/Umgang",
    "Reflexion des eigenen Lehrhandelns": "http://example.com/Reflexion",
    "Berufliche Weiterentwicklung": "http://example.com/Berufliche",
    "Menschenbilder": "http://example.com/Menschenbilder",
    "Wertvorstellungen": "http://example.com/Wertvorstellungen",
    "Eigenes Rollenbewusstsein": "http://example.com/Eigenes",
    "Subjektive Annahmen über das Lehren und Lernen": "http://example.com/Subjektive",
    "Kooperation mit Eltern": "http://example.com/Kooperation",
    "Kollegiale Zusammenarbeit und Netzwerken": "http://example.com/Kollegiale",
    "Lerninhalte und -ziele": "http://example.com/Lerninhalte",
    "Methoden, Medien und Materialien": "http://example.com/Methoden",
    "Outcomeorientierung": "http://example.com/Outcomeorientierung",
    "Rahmenbedingungen und Lernumgebungen": "http://example.com/Rahmenbedingungen",
    "Moderation und Steuerung von Gruppen": "http://example.com/Moderation",
    "Professionelle Kommunikation": "http://example.com/Professionelle",
    "Diagnostik und Lernberatung": "http://example.com/Diagnostik",
    "Teilnehmendenorientierung": "http://example.com/Teilnehmendenorientierung",
    "Curriculare und institutionelle Rahmenbedingungen": "http://example.com/Curriculare",
    "Feldspezifisches Wissen": "http://example.com/Feldspezifisches",
    "Adressaten und Adressaten": "http://example.com/Adressaten",
}

facet_scores, area_scores, aspect_scores, low_score_links = map_activities_to_competencies(xapi_activities, competency_hierarchy, mapping_table_resource)

output_data = {
    "Facet Scores": facet_scores,
    "Area Scores": area_scores,
    "Aspect Scores": aspect_scores,
    #"Low Score Links": low_score_links
}

with open('greta_results.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

'''
print("Facet Scores:")
print(len(facet_scores))
for facet_score in facet_scores:
    print(facet_score)

print("\nArea Scores:")
for area_score in area_scores:
    print(area_score)

print("\nAspect Scores:")
for aspect_score in aspect_scores:
    print(aspect_score)

print("\nLow Score Links:")
print(len(low_score_links))
for link in low_score_links:
    print(link)
'''