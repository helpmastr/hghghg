import sys
import os

# Ensure we can import from backend
sys.path.append(os.getcwd())

from backend.utils.uk_mapper import UKMapper

def test():
    print("Initializing UKMapper...")
    # It should automatically find it in backend/data/ or root
    mapper = UKMapper() 
    
    print(f"Total Mappings Loaded: {len(mapper.mapping)}")
    
    test_cases = ["panadol", "PANADOL", "nicorette", "Ovitrelle", "Omnipaque", "solpadeine", "Solpadeine Soluble"]
    
    for t in test_cases:
        res = mapper.resolve(t)
        hit = "✅" if res else "❌"
        print(f"{hit} '{t}' -> {res}")

if __name__ == "__main__":
    test()
