import json
import csv
import re

def get_name_group(name):
    name = name.lower()
    groups = {
        'Alexander': ['alexander', 'alejandro', 'alexandr', 'alexandre', 'alessandro', 'aleksander', 'ألكسندر', '亚历山大', 'アレクサンドル', '알렉산드르', 'iskender', 'magno', 'grote', 'veliky', 'wielki', 'veliký'],
        'William': ['william', 'willem', 'vilém', 'guillaume', 'guilherme', 'wilhelm', 'وليام', '威廉', 'ウィリアム', '윌리엄', 'fatih', 'veroveraar', 'conqueror', 'conquistador'],
        'Catherine': ['catherine', 'catarina', 'caterina', 'katarzyna', 'kateřina', 'كاثرين', '凯瑟琳', '叶카', '카트린', '예카', 'katerina', 'medici', 'medycejska'],
        'Philip': ['philip', 'felipe', 'filippo', 'filips', 'فيليب', '腓力', 'フェリペ', '펠리페', 'filip'],
        'Henry': ['henry', 'enrico', 'henryk', 'jindřich', 'henri', 'هنري', '亨利', 'ヘンリー', '헨리', 'jind'],
        'Ivan': ['ivan', 'ivã', 'iwan', 'إيفان', '伊凡', 'イヴァン', '이반', 'грозный', 'terrible', 'رهيب'],
        'George': ['george', 'jorge', 'giorgio', 'georg', 'jerzy', 'jiří', 'georges', 'جورج', '乔治', '게올', '요르', 'georgios'],
        'John': ['john', 'juan', 'jean', 'jan', 'joão', 'giovanni', 'یوحنا', 'خوان', '约翰', 'フアン', '후안', 'castile', 'kastylijski', 'castilla', 'castille', 'castilië', 'castela'],
        'Louis': ['louis', 'luís', 'luigi', 'ludwig', 'ludvík', 'لويس', '路易', 'ルイ', '루이'],
        'Peter': ['peter', 'pedro', 'pietro', 'pieter', 'petr', 'piotr', 'بطرس', '彼得', 'ピョートル', '표트르', 'petro'],
        'Frederick': ['frederick', 'frederico', 'federico', 'friedrich', 'fridrich', 'fryderyk', 'frédéric', 'فريدريش', '腓特烈', 'フリードリヒ', '프리드리히'],
    }
    
    # Check for direct inclusion or minor typos (first 4 chars)
    words = re.findall(r'\w+', name)
    for word in words:
        if len(word) < 3: continue
        for group, keywords in groups.items():
            for kw in keywords:
                if kw in word or word[:4] in kw:
                    return group
    
    # Fallback: check whole name for keywords
    for group, keywords in groups.items():
        for kw in keywords:
            if kw in name:
                return group
    return None

def process():
    # Load entity reference
    entities = {}
    with open('d:/IIT MADRAS/TDS/GA4/16/q-cross-lingual-entity-disambiguation-server (1)/entity_reference.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            eid = row['entity_id']
            era_str = row['era']
            if 'BC' in era_str:
                years = re.findall(r'\d+', era_str)
                row['start_year'] = -int(years[0])
                row['end_year'] = -int(years[1]) if len(years) > 1 else row['start_year'] + 50
            else:
                years = re.findall(r'\d+', era_str)
                row['start_year'] = int(years[0])
                row['end_year'] = int(years[1]) if len(years) > 1 else row['start_year'] + 50
            
            # Special case for Alexander group year matching
            if eid == 'E011': # BC years are written as positive 356 in docs
                row['start_year'] = 300
                row['end_year'] = 400
                
            row['group'] = get_name_group(row['canonical_name'])
            entities[eid] = row

    results = []
    with open('d:/IIT MADRAS/TDS/GA4/16/q-cross-lingual-entity-disambiguation-server (1)/documents.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            doc = json.loads(line)
            doc_id = doc['doc_id']
            name = doc['mentioned_name']
            year = doc['year']
            region = doc['source_region']
            
            group = get_name_group(name)
            
            # Find candidate within group that fits year best
            candidates = []
            for eid, ent in entities.items():
                if group and ent['group'] == group:
                    candidates.append(ent)
                elif not group:
                    # If no group found, all are candidates
                    candidates.append(ent)
            
            if not candidates:
                # Emergency fallback: all entities
                candidates = list(entities.values())
            
            best_id = None
            min_dist = float('inf')
            
            for ent in candidates:
                # Calculate "distance" to reign
                # If year is within [start-20, end+20], distance is low
                if ent['start_year'] - 20 <= year <= ent['end_year'] + 20:
                    mid = (ent['start_year'] + ent['end_year']) / 2
                    dist = abs(year - mid)
                    # Region bonus
                    if ent['region'].lower() in region.lower() or region.lower() in ent['region'].lower():
                        dist -= 100 
                else:
                    mid = (ent['start_year'] + ent['end_year']) / 2
                    dist = abs(year - mid) + 1000 # penalized
                
                if dist < min_dist:
                    min_dist = dist
                    best_id = ent['entity_id']
            
            # Refine specific duplicates / ambiguous symbols
            if group == 'Alexander':
                if 'II' in name or '2' in name or '二' in name: best_id = 'E002'
                elif 'I' in name or '1' in name or '一' in name:
                    if 'II' not in name: best_id = 'E003'
                elif 'Great' in name or 'Magno' in name or 'Великий' in name or year < 1000:
                    best_id = 'E011'
            
            if group == 'Louis':
                if 'XIV' in name: best_id = 'E014'

            results.append({'doc_id': doc_id, 'entity_id': best_id})

    # Write output CSV
    with open('d:/IIT MADRAS/TDS/GA4/16/output.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['doc_id', 'entity_id'])
        writer.writeheader()
        writer.writerows(results)

if __name__ == '__main__':
    process()
