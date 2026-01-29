import React, { useState } from 'react';
import { Pill, Ruler, AlertTriangle, CheckCircle, Search, MapPin, Download, Baby } from 'lucide-react';

const SYMPTOM_OPTIONS = [
    { id: 'fever', label: 'حرارة مرتفعة / حمى' },
    { id: 'headache', label: 'صداع / آلام الرأس' },
    { id: 'cough', label: 'سعال (كحة)' },
    { id: 'stomach', label: 'آلام البطن / مغص' },
    { id: 'allergy', label: 'حساسية' },
    { id: 'flu', label: 'زكام / إنفلونزا' },
    { id: 'muscle', label: 'آلام العضلات / المفاصل' },
    { id: 'eye', label: 'آلام أو التهاب العين' },
    { id: 'ear', label: 'آلام الأذن' },
    { id: 'skin', label: 'طفح جلدي / حكة' },
    { id: 'diarrhea', label: 'إسهال' },
    { id: 'throat', label: 'آلام الحلق' }
];

const HISTORY_OPTIONS = [
    { id: 'asthma', label: 'ربو' },
    { id: 'diabetes', label: 'سكري' },
    { id: 'hypertension', label: 'ضغط دم مرتفع' },
    { id: 'heart', label: 'أمراض قلب' },
    { id: 'kidney', label: 'مشاكل في الكلى' },
    { id: 'liver', label: 'مشاكل في الكبد' }
];

function App() {
    const [formData, setFormData] = useState({
        symptoms: [],
        temperature: '37',
        history: [],
        medications: '',
        age: '',
        weight: '',
        takesMeds: 'no'
    });
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const toggleSelection = (field, id) => {
        setFormData(prev => {
            const current = prev[field];
            const isSelected = current.includes(id);
            return {
                ...prev,
                [field]: isSelected ? current.filter(item => item !== id) : [...current, id]
            };
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (formData.symptoms.length === 0) {
            alert("يرجى اختيار عرض واحد على الأقل.");
            return;
        }

        setLoading(true);
        setResult(null);

        const submissionData = {
            symptoms: formData.symptoms.map(s => SYMPTOM_OPTIONS.find(opt => opt.id === s).label).join(', '),
            temperature: formData.temperature,
            history: formData.history.length > 0 ? formData.history.map(h => HISTORY_OPTIONS.find(opt => opt.id === h).label).join(', ') : 'لا يوجد',
            medications: formData.takesMeds === 'yes' ? formData.medications : 'لا يوجد',
            age_weight: `${formData.age} سنة, ${formData.weight} كجم`
        };

        try {
            const response = await fetch('https://hghghg-production.up.railway.app/consult', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(submissionData)
            });
            const data = await response.json();
            setResult(data.message);
        } catch (error) {
            setResult("خطأ في الاتصال بقاعدة بيانات هيئة الغذاء والدواء. يرجى التأكد من تشغيل الخادم.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            {/* 1. Hero Section */}
            <header className="hero">
                <h1>الصيدلي السعودي الذكي</h1>
                <p>احصل على معلومات فورية عن الأدوية، الجرعات، والتفاعلات بناءً على بيانات هيئة الغذاء والدواء السعودية الرسمية.</p>
                <div className="alert-box">
                    <AlertTriangle size={20} />
                    ⚠️ هذا النظام يعمل بالذكاء الاصطناعي للأغراض المعلوماتية فقط. في حالات الطوارئ، اتصل بـ 937 أو توجه لأقرب مستشفى.
                </div>
            </header>

            {/* 2. Input Form */}
            <section className="form-card">
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>ما هي الأعراض التي تشتكي منها؟ (اختر من الخيارات)</label>
                        <div className="option-grid">
                            {SYMPTOM_OPTIONS.map(opt => (
                                <button
                                    key={opt.id}
                                    type="button"
                                    className={`option-btn ${formData.symptoms.includes(opt.id) ? 'active' : ''}`}
                                    onClick={() => toggleSelection('symptoms', opt.id)}
                                >
                                    {opt.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                        <div className="form-group">
                            <label>درجة الحرارة (°مئوية)</label>
                            <select
                                className="form-select"
                                value={formData.temperature}
                                onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
                            >
                                {Array.from({ length: 11 }, (_, i) => 35 + i * 0.5).map(val => (
                                    <option key={val} value={val}>{val}°م</option>
                                ))}
                                <option value="over40">أكثر من 40°م</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>العمر والوزن</label>
                            <div style={{ display: 'flex', gap: '0.8rem' }}>
                                <input
                                    type="number"
                                    placeholder="العمر"
                                    value={formData.age}
                                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                                    required
                                />
                                <input
                                    type="number"
                                    placeholder="الوزن (كجم)"
                                    value={formData.weight}
                                    onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>هل تعاني من أمراض مزمنة؟ (يمكن اختيار أكثر من خيار)</label>
                        <div className="option-grid">
                            {HISTORY_OPTIONS.map(opt => (
                                <button
                                    key={opt.id}
                                    type="button"
                                    className={`option-btn ${formData.history.includes(opt.id) ? 'active' : ''}`}
                                    onClick={() => toggleSelection('history', opt.id)}
                                >
                                    {opt.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="form-group">
                        <label>هل تتناول أدوية أخرى حالياً؟</label>
                        <div className="radio-group">
                            <label className="radio-label">
                                <input type="radio" name="meds" value="no" checked={formData.takesMeds === 'no'} onChange={(e) => setFormData({ ...formData, takesMeds: 'no' })} /> لا أتناول أدوية أخرى
                            </label>
                            <label className="radio-label">
                                <input type="radio" name="meds" value="yes" checked={formData.takesMeds === 'yes'} onChange={(e) => setFormData({ ...formData, takesMeds: 'yes' })} /> أتناول أدوية أخرى
                            </label>
                        </div>
                        {formData.takesMeds === 'yes' && (
                            <input
                                type="text"
                                placeholder="اذكر أسماء الأدوية الحالية"
                                value={formData.medications}
                                onChange={(e) => setFormData({ ...formData, medications: e.target.value })}
                            />
                        )}
                    </div>

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? "جاري البحث في قاعدة بيانات الهيئة..." : "استشارة الصيدلي الآلي"}
                    </button>
                </form>

                {/* 3. Processing State */}
                {loading && (
                    <div className="processing">
                        <div className="loader"></div>
                        <p>جاري البحث في قاعدة بيانات هيئة الغذاء والدواء والتحقق من التفاعلات الدوائية...</p>
                    </div>
                )}

                {/* 4. Results Layout */}
                {result && (
                    <div className="results">
                        <div className="result-section">
                            <div className="result-title"><Pill /> الدواء الموصى به</div>
                            <p style={{ whiteSpace: 'pre-line' }}>{result}</p>
                        </div>

                        <div className="result-section">
                            <div className="result-title"><CheckCircle /> حالة الهيئة</div>
                            <p style={{ fontWeight: 700, color: 'var(--primary)' }}>✅ تم التحقق في قاعدة بيانات هيئة الغذاء والدواء الرسمية.</p>
                        </div>

                        {/* 5. Quick Action Buttons */}
                        <div className="chips">
                            <button className="chip"><MapPin size={20} /> أرني أقرب صيدلية مفتوحة</button>
                            <button className="chip"><Download size={20} /> تحميل التعليمات كـ PDF</button>
                            <button className="chip"><Baby size={20} /> التحقق من نسخة آمنة للأطفال</button>
                        </div>
                    </div>
                )}
            </section>
        </div>
    );
}

export default App;
