import json

def load_xapi_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        xapi_data = json.load(file)
    return xapi_data

def map_activities_to_competencies(xapi_activities, competency_hierarchy, mapping_table_resource):
    # Extract the sub-competency (facet) scores from the xAPI data
    sub_competency_scores = {}
    sub_competency_resources = {}
    for activity in xapi_activities:
        statement = activity["statement"]
        context = statement["context"]["extensions"]["learningObjectMetadata"]
        facet = context["facet"]
        area = context["area"]
        main_competency = context["aspect"]
        score = statement["result"]["score"]["raw"]
        competence_path = context["competencePath"]

        if facet not in sub_competency_scores:
            sub_competency_scores[facet] = []
        sub_competency_scores[facet].append(score)
        if facet in mapping_table_resource:
            sub_competency_resources[facet] = mapping_table_resource[facet]

    # Ensure all facets from the hierarchy are included, with default score of 0 if missing
    for main_competency, areas in competency_hierarchy.items():
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
    main_competency_averages = {}
    
    for main_competency, areas in competency_hierarchy.items():
        for area, facets in areas.items():
            relevant_scores = [sub_competency_averages[facet] for facet in facets]
            area_averages[area] = sum(relevant_scores)/len(relevant_scores) if relevant_scores else 0
        
        relevant_area_scores = [area_averages[area] for area in areas]
        main_competency_averages[main_competency] = sum(relevant_area_scores)/len(relevant_area_scores) if relevant_area_scores else 0

    # Create the GRETA competencies structure with full paths and scores
    greta_competencies = [
        {"id": f"{main_competency}/{area}/{facet}", "achievement": sub_competency_averages[facet]}
        for main_competency, areas in competency_hierarchy.items()
        for area, facets in areas.items()
        for facet in facets
    ]
    
    # Create the area and main competency scores structure
    area_scores = [
        {"id": f"{main_competency}/{area}", "achievement": area_averages[area]}
        for main_competency, areas in competency_hierarchy.items()
        for area in areas
    ]
    
    main_competency_scores = [
        {"id": f"{main_competency}", "achievement": main_competency_averages[main_competency]}
        for main_competency in competency_hierarchy
    ]

    # Find the sub-competencies (facets) with scores below 3 and provide learning resource links
    low_score_links = []
    added_links = set()
    
    for facet, score in sub_competency_averages.items():
        if score < 3:
            competence_path = sub_competency_resources[facet]
            link = {"id": f"{facet}", "link": competence_path}
            link_tuple = (link["id"], link["link"])
            if link_tuple not in added_links:
                low_score_links.append(link)
                added_links.add(link_tuple)
    
    return greta_competencies, area_scores, main_competency_scores, low_score_links

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
        ]
    },
    "Fach- und feldspezifisches Wissen": {
        "Feldbezug": [
            "Curriculare und institutionelle Rahmenbedingungen",
            "Feldspezifisches Wissen",
            "Adressaten und Adressaten"
        ]
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
greta_competencies, area_scores, main_competency_scores, low_score_links = map_activities_to_competencies(xapi_activities, competency_hierarchy, mapping_table_resource)

print("GRETA Competencies:")
print(len(greta_competencies))
for competency in greta_competencies:
    print(competency)

print("\nArea Scores:")
for area_score in area_scores:
    print(area_score)

print("\nMain Competency Scores:")
for main_competency_score in main_competency_scores:
    print(main_competency_score)

print("\nLow Score Links:")
print(len(low_score_links))
for link in low_score_links:
    print(link)
