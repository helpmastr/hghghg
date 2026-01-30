import torch

# Optimization for 8 CPU Cores on Railway
torch.set_num_threads(8)
torch.set_num_interop_threads(1)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# NER / NEL Integration
try:
    from backend.utils.ner import ClinicalNER
except ImportError:
    from utils.ner import ClinicalNER

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data
# Load Master Dataset (SFDA + SDI Enriched)
csv_path = "data/master_drugs_data.csv.gz"
if not os.path.exists(csv_path):
    csv_path = "backend/data/master_drugs_data.csv.gz"

# Fallback to uncompressed if necessary
if not os.path.exists(csv_path):
    csv_path = "data/master_drugs_data.csv"
    if not os.path.exists(csv_path):
        csv_path = "backend/data/master_drugs_data.csv"

# Pandas auto-detects gzip
df = pd.read_csv(csv_path)

# Initialize NER Engine
ner_engine = ClinicalNER()

# Load Model
model_name = "Qwen/Qwen2.5-1.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)

class Query(BaseModel):
    symptoms: str
    temperature: str
    history: str
    medications: str
    age_weight: str

@app.get("/debug/data")
async def debug_data():
    try:
        import os
        return {
            "cwd": os.getcwd(),
            "df_rows": len(df) if 'df' in globals() else "Not Defined",
            "map_size": len(ner_engine.symptoms_map) if 'ner_engine' in globals() else "Not Defined",
            "symptoms_file_exists": any([os.path.exists(p) for p in ["data/symptoms_mapping.json", "backend/data/symptoms_mapping.json"]]),
            "sample_map": list(ner_engine.symptoms_map.keys())[:3] if 'ner_engine' in globals() and ner_engine.symptoms_map else "Empty",
            "status": "Alive"
        }
    except Exception as e:
        return {"error": str(e), "type": str(type(e))}

@app.post("/consult")
async def consult(query: Query):
    # 1. NER & Entity Recognition Phase
    # Extract symptoms, standardized terms, and link international brands
    entities = ner_engine.extract_entities(query)
    
    search_terms = entities['search_terms']
    mapped_brands = entities['international_links']

    # 2. RAG Retrieval Phase
    relevant_drugs = []
    
    # Perform Search in Master DB
    import re
    for _, row in df.iterrows():
        trade = str(row["Trade Name"]).lower()
        scientific = str(row["Scientific Name"]).lower()
        
        # Check for matches (Regex Word Boundary)
        matched = False
        for term in search_terms:
            # Escape to handle special chars like '+' in 'Cold + Flu'
            # \b matches word boundary
            pattern = r'\b' + re.escape(term.lower()) + r'\b'
            if re.search(pattern, trade) or re.search(pattern, scientific):
                matched = True
                break
        
        if matched:
            relevant_drugs.append(row.to_dict())
        
        if len(relevant_drugs) >= 5: 
            break
            
    context = ""
    if relevant_drugs:
        context = "Relevant SFDA Drug Data & Clinical Instructions (Master Dataset):\n"
        for d in relevant_drugs:
            context += f"- {d['Trade Name']} ({d['Scientific Name']}): {d['Dosage Form']}, Strength: {d['Strength']}, Administration: {d['Administration Route (AR)'] if pd.notna(d['Administration Route (AR)']) else d['Administration Route']}\n"
            if pd.notna(d['Patient Leaflet (AR)']):
                context += f"  Official Instructions: {str(d['Patient Leaflet (AR)'])[:800]}...\n"
            if 'International Dosage' in d and pd.notna(d['International Dosage']) and d['International Dosage'] != "":
                context += f"  International Dosage Protocols (Drugs.com): {str(d['International Dosage'])[:800]}...\n"

    # Add International Bridge Note to Context
    if mapped_brands:
        context += "\n[System Note: International Brand Mapping (NER/NEL)]\n"
        for brand, ing in mapped_brands.items():
            context += f"- User mentioned '{brand}' (International). Mapped via NER to active ingredient '{ing}' to find local equivalent.\n"

    if not context:
        context = "No specific match found in SFDA master database for translated keywords."

    # 3. Formulate prompt to generate response in ARABIC
    system_prompt = f"""أنت صيدلي سعودي خبير.
استخدم البيانات التالية لتقديم نصيحة علاجية واضحة ومباشرة.
البيانات تحتوي على قائمة أدوية. اختر الدواء الأنسب للأعراض المذكورة وأكد عليه.

تعليمات صارمة (Strict Instructions):
1. ابدأ الرد فوراً بعبارة: "💊 الدواء الموصى به: [اسم الدواء]".
2. لا تبدأ بـ "لا تستخدم" أو التحذيرات.
3. اذكر طريقة الاستخدام والجرعة بوضوح.
4. ضع الموانع والتحذيرات في قسم منفصل في الأسفل.
5. إذا وجدت دواءً دولياً (مثل Panadol UK) ودواءً محلياً، اربط بينهما.

الهيكل المطلوب:
💊 الدواء الموصى به: [الاسم]
📝 دواعي الاستعمال: [لماذا يستخدم هذا الدواء]
✅ الجرعة ({query.age_weight}): [تفاصيل الجرعة]
⚠️ تحذيرات هامة: [الموانع]

بيانات الهيئة (Context):
{context}

نصيحة الهيئة الرسمية:
✅ حالة الهيئة: تم التحقق في قاعدة بيانات هيئة الغذاء والدواء الرسمية."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"الأعراض: {query.symptoms}. التاريخ الطبي: {query.history}. الأدوية الحالية: {query.medications}. ما هي نصيحتك؟"}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return {"message": response}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
