import streamlit as st
import pypdf
import requests
import io
import urllib.parse
import json
from PIL import Image

# محاولة استيراد OCR بشكل آمن
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ------------------------------------------------------------------
# 1. إعدادات الصفحة والجلسة
# ------------------------------------------------------------------
st.set_page_config(page_title="محرك بحث لوائح ONCF", layout="wide", page_icon="🚆")
st.title("🚆 محرك البحث المباشر في لوائح ONCF")

# تهيئة حالة الجلسة للفهرس
if "search_index" not in st.session_state:
    st.session_state.search_index = None
    st.session_state.is_indexing = False

# ------------------------------------------------------------------
# 2. تحميل الروابط من JSON
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_dropbox_links():
    try:
        with open("DROPBOX_PDFS.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        clean_links = {}
        for name, url in raw_data.items():
            clean_name = name.strip()
            clean_url = url.strip().replace("&dl=0", "&dl=1").replace("?dl=0", "?dl=1")
            if "dl=1" not in clean_url:
                sep = "&" if "?" in clean_url else "?"
                clean_url += f"{sep}dl=1"
            clean_links[clean_name] = clean_url
        return clean_links
    except Exception as e:
        st.error(f"❌ خطأ في تحميل الروابط: {e}")
        return {}

DROPBOX_PDFS = load_dropbox_links()

# ------------------------------------------------------------------
# 3. دالة بناء الفهرس (تعمل مرة واحدة فقط)
# ------------------------------------------------------------------
def build_search_index():
    """بناء الفهرس وتخزينه في session_state"""
    if st.session_state.search_index is not None:
        return st.session_state.search_index
        
    st.session_state.is_indexing = True
    search_index = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_files = len(DROPBOX_PDFS)
    
    for i, (doc_name, url) in enumerate(DROPBOX_PDFS.items()):
        progress_bar.progress((i + 1) / total_files)
        status_text.text(f"⏳ جاري الفهرسة: {doc_name} ({i+1}/{total_files})")
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                pdf_file = io.BytesIO(response.content)
                reader = pypdf.PdfReader(pdf_file)
                
                for page_num, page in enumerate(reader.pages, start=1):
                    text = page.extract_text() or ""
                    
                    # تفعيل OCR فقط إذا كان النص قصيراً جداً
                    if len(text.strip()) < 20 and OCR_AVAILABLE:
                        try:
                            images = page.images
                            if images:
                                img_data = max(images, key=lambda x: x.width * x.height).data
                                image = Image.open(io.BytesIO(img_data))
                                ocr_text = pytesseract.image_to_string(image, lang='fra+ara')
                                if len(ocr_text.strip()) > len(text.strip()):
                                    text = ocr_text
                        except Exception:
                            pass
                    
                    if text and len(text.strip()) > 10:
                        search_index.append({
                            "doc_name": doc_name,
                            "page": page_num,
                            "text": text,
                            "original_url": url
                        })
        except Exception:
            pass
            
    progress_bar.empty()
    status_text.empty()
    
    st.session_state.search_index = search_index
    st.session_state.is_indexing = False
    st.success(f"✅ تم بناء الفهرس بنجاح! ({len(search_index)} صفحة مفهرسة)")
    return search_index

# ------------------------------------------------------------------
# 4. زر بدء الفهرسة والبحث
# ------------------------------------------------------------------
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input(
        "🔍 أدخل كلمة البحث أو رقم المادة:", 
        placeholder="مثال: secours par l'arrière / article 203 / freinage / DBC"
    )

with col2:
    if st.button("🔄 إعادة بناء الفهرس", use_container_width=True):
        st.session_state.search_index = None
        st.rerun()

# عرض شريط التقدم إذا كانت الفهرسة جارية
if st.session_state.is_indexing:
    index_data = build_search_index()
elif st.session_state.search_index is None:
    # بدء الفهرسة تلقائياً عند أول زيارة
    index_data = build_search_index()
else:
    index_data = st.session_state.search_index

# ------------------------------------------------------------------
# 5. عرض النتائج (فوري لأن الفهرس موجود في الذاكرة)
# ------------------------------------------------------------------
if query and index_data:
    results = [item for item in index_data if query.lower() in item["text"].lower()]
    
    st.write(f"### 📋 النتائج المعثور عليها ({len(results)}):")
    
    if not results:
        st.warning("لم يتم العثور على أي نتيجة مطابقة.")
    else:
        for res in results:
            snippet = res["text"][:350].replace("\n", " ") + "..."
            encoded_url = urllib.parse.quote(res["original_url"], safe='')
            viewer_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={encoded_url}#page={res['page']}"

            with st.expander(f"📖 {res['doc_name']} — الصفحة {res['page']}"):
                st.write(f"**المقتطف:** {snippet}")
                st.markdown(f"[🔗 فتح المستند على الصفحة {res['page']} في نافذة كاملة]({viewer_url})")
                st.caption("📺 معاينة مباشرة:")
                st.markdown(f'<iframe src="{viewer_url}" width="100%" height="600" frameborder="0"></iframe>', unsafe_allow_html=True)
elif not query:
    st.info("👆 اكتب للبحث. سيتم بناء الفهرس تلقائياً عند أول بحث.")
