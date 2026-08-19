import streamlit as st
import pypdf
import requests
import io
import urllib.parse
from PIL import Image
import pytesseract

# إعدادات الصفحة
st.set_page_config(page_title="محرك بحث لوائح ONCF", layout="wide", page_icon="🚆")
st.title("🚆 محرك البحث المباشر في لوائح ONCF")
st.markdown("ابحث في المستندات السحابية (يدعم النصوص والصور الممسوحة ضوئياً).")

# ------------------------------------------------------------------
# قائمة الروابط (تم استخدام القائمة الموثوقة التي قمنا بإنشائها سابقاً)
# ------------------------------------------------------------------
DROPBOX_PDFS = {
    "Règlement S1A - Titre I": "https://www.dropbox.com/scl/fi/0s8pe3sfugugujyxzby2d/R-glement-S1A-Titre-I-version-03-VS.pdf?rlkey=ldghn6rtfu1tqyavmyiwtct67&dl=1",
    "Règlement RG S1A titre II facs 0": "https://www.dropbox.com/scl/fi/lay3km0jcb0zaj79na4we/RG-S1A-titre-II-facs-0-zc-VF-sign.pdf?rlkey=jdv71mtl0pwmmmk0pbbikg4l9&dl=1",
    # ... (قم بلصق باقي الروابط الصحيحة هنا من القائمة التي رتبناها سابقاً) ...
    "CG S0 n°1.pdf": "https://www.dropbox.com/scl/fi/fjbpyqala3tv0kzvggwet/CG-S0-n-1.pdf?rlkey=t13rntcxf4fteb2rhj7ko8yh1&dl=1",
    "CG S2C n7 exploitation du systeme de detection des boites chaudes (DBC) sol et embarque, et du systeme de detection de freins bloques (DFB) V05.pdf": "https://www.dropbox.com/scl/fi/hxftftoo44kbj9r4mg2a0/CG-S2C-n7-exploitation-du-systeme-de-detection-des-boites-chaudes-DBC-sol-et-embarque-et-du-systeme-de-detection-de-freins-bloques-DFB-V05.pdf?rlkey=9ixzcfv0c47jpsqkpwujxkg23&dl=1",
    # تأكد من وجود جميع الروابط هنا
}

@st.cache_data(show_spinner=False)
def load_and_index_from_dropbox():
    """تحميل وفهرسة الملفات مع دعم OCR للملفات الممسوحة"""
    search_index = []
    
    progress_container = st.empty()
    status_container = st.empty()
    
    total_files = len(DROPBOX_PDFS)
    
    for i, (doc_name, url) in enumerate(DROPBOX_PDFS.items()):
        progress_container.progress((i + 1) / total_files)
        status_container.text(f"جاري المعالجة: {doc_name} ({i+1}/{total_files})")
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                pdf_file = io.BytesIO(response.content)
                reader = pypdf.PdfReader(pdf_file)
                
                for page_num, page in enumerate(reader.pages, start=1):
                    text = page.extract_text()
                    
                    # 🔍 التحقق مما إذا كان النص فارغاً (ملف ممسوح ضوئياً)
                    if not text or len(text.strip()) < 10:
                        try:
                            # تحويل الصفحة إلى صورة وتطبيق OCR
                            images = page.images
                            if images:
                                # أخذ أول صورة في الصفحة (عادة ما تكون الصفحة كاملة)
                                img_data = images[0].data
                                image = Image.open(io.BytesIO(img_data))
                                # استخراج النص باستخدام Tesseract (اللغة الفرنسية والعربية)
                                ocr_text = pytesseract.image_to_string(image, lang='fra+ara')
                                text = ocr_text
                        except Exception as ocr_err:
                            pass  # تجاهل أخطاء OCR والاستمرار
                    
                    if text and len(text.strip()) > 5:
                        search_index.append({
                            "doc_name": doc_name,
                            "page": page_num,
                            "text": text,
                            "original_url": url
                        })
            
        except Exception as e:
            st.warning(f"️ تعذر معالجة {doc_name}: {str(e)[:80]}")
            
    progress_container.empty()
    status_container.empty()
    return search_index

# شريط البحث
query = st.text_input("🔍 أدخل كلمة البحث أو رقم المادة:")

if query:
    index_data = load_and_index_from_dropbox()
    
    results = []
    query_lower = query.lower()
    
    for item in index_data:
        if query_lower in item["text"].lower():
            results.append(item)
            
    st.write(f"### 📋 النتائج ({len(results)}):")
    
    if not results:
        st.warning("لم يتم العثور على نتائج.")
    else:
        for res in results:
            snippet = res["text"][:300].replace("\n", " ") + "..."
            encoded_url = urllib.parse.quote(res["original_url"], safe='')
            viewer_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={encoded_url}#page={res['page']}"

            with st.expander(f" {res['doc_name']} — ص {res['page']}"):
                st.write(f"**المقتطف:** {snippet}")
                st.markdown(f"[🔗 فتح المستند على الصفحة {res['page']}]({viewer_url})")
else:
    st.info(" اكتب للبحث في جميع اللوائح.")
