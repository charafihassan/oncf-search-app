import streamlit as st
import pypdf
import requests
import io
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="محرك بحث لوائح ONCF", layout="wide", page_icon="🚆")

st.title("🚆 محرك البحث المباشر في لوائح ONCF")
st.markdown("ابحث في المستندات السحابية وسيتم توجيهك للمادة والصفحة مباشرة.")

# ------------------------------------------------------------------
# 2. قائمة روابط ملفات الـ PDF الحقيقية على Dropbox
# ------------------------------------------------------------------
DROPBOX_PDFS = {
    "Règlement S9B": "https://www.dropbox.com/scl/fi/gm148owemf6xxx4vas3q8/S9B.pdf?rlkey=1rgyjlei8gp6265cc9uwp2ah6&st=1edpxuqv&dl=1",
    "Règlement S3A": "https://www.dropbox.com/scl/fi/zrw97rtsxii6oa4yg0exy/S3A.pdf?rlkey=isw2t00hy9zuk69zjjvuslscj&st=o4ixucvu&dl=1",
    "Règlement S1E": "https://www.dropbox.com/scl/fi/qk4lo1q82whd6l0uilaob/S1E.pdf?rlkey=m1ks2st4jevmk1sjyzjgvxgo6&st=mv3lx6qf&dl=1",
    "Règlement S2A": "https://www.dropbox.com/scl/fi/8kvltmdnas11rfkbf95ej/S2A.pdf?rlkey=6labn4o0ef76a07lxxrtay204&st=sp7q2v02&dl=1",
    "Règlement S7A": "https://www.dropbox.com/scl/fi/a9tdxz3o7195y2yyqa12c/S7A-1-P.pdf?rlkey=u33nws3syb02fcbm8dmk2eqq8&st=wbaf8hdk&dl=1",
}

@st.cache_resource
def load_and_index_from_dropbox():
    """تحميل المستندات من Dropbox وقراءتها في الذاكرة"""
    search_index = []
    
    for doc_name, url in DROPBOX_PDFS.items():
        download_url = url.replace("dl=0", "dl=1")
        if "dl=1" not in download_url:
            download_url += "&dl=1" if "?" in download_url else "?dl=1"
        
        try:
            response = requests.get(download_url, timeout=30)
            if response.status_code == 200:
                pdf_file = io.BytesIO(response.content)
                reader = pypdf.PdfReader(pdf_file)
                
                for page_num, page in enumerate(reader.pages, start=1):
                    text = page.extract_text()
                    if text:
                        search_index.append({
                            "doc_name": doc_name,
                            "page": page_num,
                            "text": text,
                            "original_url": url
                        })
        except Exception as e:
            st.error(f"خطأ أثناء قراءة {doc_name}: {e}")
            
    return search_index

# شريط البحث
query = st.text_input("🔍 أدخل كلمة البحث أو رقم المادة (مثال: secours par l'arrière / article 203 / freinage):")

with st.spinner("جاري قراءة وتحليل الملفات من Dropbox..."):
    index_data = load_and_index_from_dropbox()

if query:
    results = []
    query_lower = query.lower()
    
    for item in index_data:
        if query_lower in item["text"].lower():
            results.append(item)
            
    st.write(f"### 📋 النتائج المعثور عليها ({len(results)}):")
    
    if not results:
        st.warning("لم يتم العثور على أي نتيجة مطابقة في الملفات.")
    else:
        for res in results:
            doc_name = res["doc_name"]
            page_num = res["page"]
            snippet = res["text"][:350].replace("\n", " ") + "..."
            
            # إعداد رابط البث المباشر المباشر بدون تنزيل
            raw_url = res["original_url"].replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "dl=1")
            
            # ترميز الرابط لاستخدامه في قارئ PDF.js
            encoded_pdf_url = urllib.parse.quote(raw_url, safe='')
            pdf_js_viewer_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={encoded_pdf_url}#page={page_num}"

            with st.expander(f"📖 {doc_name} — الصفحة {page_num}"):
                st.write(f"**المقتطع النصي:** {snippet}")
                
                # رابط خارجي مباشر يفتح القارئ المتقدم في تبويب جديد على الصفحة بالضبط
                st.markdown(f"👉 [**🔗 اضغط هنا لفتح {doc_name} على الصفحة {page_num} في نافذة كاملة**]({pdf_js_viewer_url})", unsafe_allow_html=True)
                
                st.markdown("---")
                st.caption(f"📺 المعاينة المباشرة للصفحة {page_num}:")
                
                # العرض المدمج باستخدام القارئ المتقدم القادر على تجاوز حظر Dropbox
                pdf_iframe = f'<iframe src="{pdf_js_viewer_url}" width="100%" height="600" frameborder="0"></iframe>'
                st.markdown(pdf_iframe, unsafe_allow_html=True)
else:
    st.info("👆 اكتب أي كلمة أو رقم مادة في شريط البحث أعلاه لبدء استخراج النتائج.")