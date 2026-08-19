import streamlit as st
import pypdf
import requests
import io
import urllib.parse
import json
from PIL import Image

# محاولة استيراد مكتبات OCR بشكل آمن لتجنب توقف التطبيق إذا لم تكن مثبتة
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ------------------------------------------------------------------
# 1. إعدادات الصفحة
# ------------------------------------------------------------------
st.set_page_config(page_title="محرك بحث لوائح ONCF", layout="wide", page_icon="🚆")
st.title("🚆 محرك البحث المباشر في لوائح ONCF")
st.markdown("""
ابحث في المستندات السحابية وسيتم توجيهك للمادة والصفحة مباشرة.  
✅ يدعم الملفات النصية والممسوحة ضوئياً (OCR)
""")

# ------------------------------------------------------------------
# 2. تحميل وتنظيف روابط Dropbox من ملف JSON
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_dropbox_links():
    """تحميل الروابط من ملف JSON وتنظيفها لتكون قابلة للتنزيل المباشر"""
    try:
        with open("DROPBOX_PDFS.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        clean_links = {}
        for name, url in raw_data.items():
            # تنظيف الاسم والرابط من المسافات الزائدة
            clean_name = name.strip()
            clean_url = url.strip()
            
            # ضمان أن الرابط ينتهي بـ dl=1 للتنزيل المباشر
            if "&dl=0" in clean_url:
                clean_url = clean_url.replace("&dl=0", "&dl=1")
            elif "?dl=0" in clean_url:
                clean_url = clean_url.replace("?dl=0", "?dl=1")
            elif "dl=1" not in clean_url:
                separator = "&" if "?" in clean_url else "?"
                clean_url += f"{separator}dl=1"
                
            clean_links[clean_name] = clean_url
            
        return clean_links
    except Exception as e:
        st.error(f"❌ خطأ في تحميل ملف الروابط: {e}")
        return {}

DROPBOX_PDFS = load_dropbox_links()

# ------------------------------------------------------------------
# 3. دالة الفهرسة الذكية (نص عادي + OCR)
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_and_index_from_dropbox():
    """تحميل وفهرسة جميع ملفات PDF مع دعم OCR للصفحات الممسوحة"""
    search_index = []
    
    # واجهة المستخدم للتقدم
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(DROPBOX_PDFS)
    
    for i, (doc_name, url) in enumerate(DROPBOX_PDFS.items()):
        # تحديث شريط التقدم
        progress = (i + 1) / total_files
        progress_bar.progress(progress)
        status_text.text(f"⏳ جاري المعالجة: {doc_name} ({i+1}/{total_files})")
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                pdf_file = io.BytesIO(response.content)
                reader = pypdf.PdfReader(pdf_file)
                
                for page_num, page in enumerate(reader.pages, start=1):
                    text = page.extract_text() or ""
                    
                    # 🔍 التحقق الذكي: هل الصفحة ممسوحة ضوئياً؟
                    is_scanned = len(text.strip()) < 20
                    
                    if is_scanned and OCR_AVAILABLE:
                        try:
                            images = page.images
                            if images:
                                # أخذ أكبر صورة في الصفحة (عادة تكون الصفحة كاملة)
                                img_data = max(images, key=lambda x: x.width * x.height).data
                                image = Image.open(io.BytesIO(img_data))
                                
                                # استخراج النص بالفرنسية والعربية
                                ocr_text = pytesseract.image_to_string(image, lang='fra+ara')
                                if len(ocr_text.strip()) > len(text.strip()):
                                    text = ocr_text
                        except Exception:
                            pass  # تجاهل أخطاء OCR والاستمرار بالنص الأصلي إن وجد
                    
                    # إضافة الصفحة للفهرس فقط إذا احتوت على نص مفيد
                    if text and len(text.strip()) > 10:
                        search_index.append({
                            "doc_name": doc_name,
                            "page": page_num,
                            "text": text,
                            "original_url": url
                        })
            
        except Exception as e:
            st.warning(f"⚠️ تعذر معالجة {doc_name}: {str(e)[:80]}")
            
    # إخفاء شريط التقدم عند الانتهاء
    progress_bar.empty()
    status_text.empty()
    
    return search_index

# ------------------------------------------------------------------
# 4. واجهة البحث والنتائج
# ------------------------------------------------------------------
query = st.text_input(
    "🔍 أدخل كلمة البحث أو رقم المادة:", 
    placeholder="مثال: secours par l'arrière / article 203 / freinage / DBC"
)

if query:
    index_data = load_and_index_from_dropbox()
    
    results = [item for item in index_data if query.lower() in item["text"].lower()]
    
    st.write(f"### 📋 النتائج المعثور عليها ({len(results)}):")
    
    if not results:
        st.warning("لم يتم العثور على أي نتيجة مطابقة في الملفات.")
    else:
        for res in results:
            snippet = res["text"][:350].replace("\n", " ") + "..."
            
            # إعداد رابط المعاينة المباشر
            encoded_url = urllib.parse.quote(res["original_url"], safe='')
            viewer_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={encoded_url}#page={res['page']}"

            with st.expander(f"📖 {res['doc_name']} — الصفحة {res['page']}"):
                st.write(f"**المقتطف النصي:** {snippet}")
                st.markdown(f"[ اضغط هنا لفتح المستند على الصفحة {res['page']} في نافذة كاملة]({viewer_url})")
                st.markdown("---")
                st.caption("📺 معاينة مباشرة:")
                st.markdown(f'<iframe src="{viewer_url}" width="100%" height="600" frameborder="0"></iframe>', unsafe_allow_html=True)
else:
    st.info("👆 اكتب أي كلمة أو رقم مادة في شريط البحث أعلاه لبدء استخراج النتائج.")
