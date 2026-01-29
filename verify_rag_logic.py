import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import pandas as pd
import json
import os

# Mock the consult logic for rapid testing without starting a full server
def test_consult_logic(symptoms, history, age_weight):
    print(f"\n--- Testing RAG for: {symptoms} ---")
    
    # 1. Load Data
    csv_path = "backend/data/master_drugs_data.csv"
    mapping_path = "backend/data/symptoms_mapping.json"
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    
    df = pd.read_csv(csv_path)
    with open(mapping_path, "r", encoding="utf-8") as f:
        symptoms_mapping = json.load(f)
        
    # 2. Translation logic
    keywords_ar = [s.strip() for s in symptoms.split(',')]
    keywords_en = []
    for kw in keywords_ar:
        if kw in symptoms_mapping:
            keywords_en.extend([k.strip() for k in symptoms_mapping[kw].split(',')])
        else:
            keywords_en.append(kw)
            
    history_ar = [h.strip() for h in history.split(',')]
    history_en = []
    for h in history_ar:
        if h in symptoms_mapping:
            history_en.extend([k.strip() for k in symptoms_mapping[h].split(',')])
        else:
            history_en.append(h)
            
    print(f"Translated Keywords: {keywords_en}")
    
    # 3. RAG Search
    relevant_drugs = []
    search_terms = keywords_en + history_en
    for _, row in df.iterrows():
        trade = str(row["Trade Name"]).lower()
        scientific = str(row["Scientific Name"]).lower()
        if any(term in trade or term in scientific for term in search_terms):
            relevant_drugs.append(row.to_dict())
        if len(relevant_drugs) >= 5:
            break
            
    # 4. Context Building
    context = ""
    if relevant_drugs:
        print(f"Found {len(relevant_drugs)} relevant drugs in master list.")
        for d in relevant_drugs:
            context += f"- {d['Trade Name']} ({d['Scientific Name']}): {d['Dosage Form']}, Strength: {d['Strength']}\n"
            if pd.notna(d['Patient Leaflet (AR)']):
                print(f"✅ Leaflet found for: {d['Trade Name']}")
                context += f"  Official Instructions: {str(d['Patient Leaflet (AR)'])[:200]}...\n"
            else:
                print(f"❌ No leaflet for: {d['Trade Name']}")
    
    # 5. Model Inference (Production Prompt Test)
    print("Initializing model for localized inference test...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", device_map="cpu")
    
    system_prompt = f"""You are a Smart Saudi Pharmacist (الصيدلي السعودي الذكي) grounded in official SFDA data.
Use the following SFDA data context to provide pharmaceutical advice strictly in ARABIC.
STRICT RULES:
1. ONLY recommend drugs mentioned in the context if they are safe for the user's symptoms and history.
2. Structure your response with the following Arabic headings:
   💊 الدواء الموصى به:
   📏 الجرعة المقترحة (بناءً على {age_weight}):
   ⚠️ تحذيرات هامة (الآثار الجانبية أو التفاعلات):
3. Respond ONLY in Arabic.
4. End with "✅ حالة الهيئة: تم التحقق في قاعدة بيانات هيئة الغذاء والدواء الرسمية."

Context:
{context}
"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "ما هو الدواء والجرعة التي تنصح بها؟"}
    ]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt")
    
    print("Generating response (8-core optimized behavior)...")
    torch.set_num_threads(8)
    generated_ids = model.generate(**model_inputs, max_new_tokens=512)
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    print("\n--- AI Response ---")
    print(response.split("assistant\n")[-1])

if __name__ == "__main__":
    # Test case 3: Fever (Classic Paracetamol case)
    test_consult_logic("حرارة مرتفعة / حمى", "لا يوجد", "30 سنة")
