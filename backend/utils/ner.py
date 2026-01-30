import json
import os

# Import sibling utility
try:
    from backend.utils.uk_mapper import UKMapper
except ImportError:
    try:
        from utils.uk_mapper import UKMapper
    except ImportError:
        # Fallback if running from root without proper package context
        from backend.utils.uk_mapper import UKMapper

class ClinicalNER:
    def __init__(self):
        self.symptoms_map = self._load_symptoms()
        self.uk_mapper = UKMapper()

    def _load_symptoms(self):
        paths = [
            "symptoms_mapping.json", # Check root/CWD first
            "data/symptoms_mapping.json", 
            "backend/data/symptoms_mapping.json",
            "../data/symptoms_mapping.json"
        ]
        for p in paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f)
                except:
                    pass
        print("Warning: symptoms_mapping.json not found.")
        return {}

    def extract_entities(self, query):
        """
        Input: Query object (pydantic)
        Output: Dict with standardized entities for RAG
        """
        # 1. Extract & Standardize Symptoms
        raw_symptoms = [s.strip() for s in query.symptoms.split(',')]
        standardized_symptoms = []
        for s in raw_symptoms:
            if s in self.symptoms_map:
                # Map Arabic -> Standard English
                standardized_symptoms.extend([k.strip() for k in self.symptoms_map[s].split(',')])
            else:
                standardized_symptoms.append(s)

        # 2. Extract & Standardize History
        raw_history = [h.strip() for h in query.history.split(',')]
        standardized_history = []
        for h in raw_history:
            if h in self.symptoms_map:
                standardized_history.extend([k.strip() for k in self.symptoms_map[h].split(',')])
            else:
                standardized_history.append(h)

        # 3. Extract & Link Medications (NEL)
        raw_meds = [m.strip() for m in query.medications.split(',')]
        standardized_meds = []
        international_links = {}

        for m in raw_meds:
            if not m: continue
            standardized_meds.append(m) # Add original
            
            # NEL: Check for International Brand Link
            ingredient = self.uk_mapper.resolve(m)
            if ingredient:
                # Link found! Add ingredient to search scope
                standardized_meds.append(ingredient)
                international_links[m] = ingredient

        # Link International Brands found in other fields? (e.g. user typed 'Panadol' in history)
        # Scan history/symptoms for brands too
        all_text_terms = standardized_symptoms + standardized_history
        for term in all_text_terms:
            ingredient = self.uk_mapper.resolve(term)
            if ingredient:
                if term not in international_links:
                    international_links[term] = ingredient
                    # We append ingredient to the search terms to ensure we find the local drug
                    # But we'll do that in the final search_terms construction

        # Construct Master Search Terms
        # Combine all English terms
        search_terms = list(set(standardized_symptoms + standardized_history + standardized_meds))
        
        # Ensure ingredients from links are in search terms
        for ing in international_links.values():
            if ing not in search_terms:
                search_terms.append(ing)

        return {
            "search_terms": search_terms,
            "entities": {
                "symptoms": standardized_symptoms,
                "history": standardized_history,
                "medications": standardized_meds
            },
            "international_links": international_links
        }
