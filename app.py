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
    "Règlement S1A - Titre I": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/R%C3%A8glement%20S1A%20-%20Titre%20I%20%20version%2003%20VS.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement RG S1A titre II facs 0": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/RG%20S1A%20titre%20II%20facs%200%20zc%20VF%20sign%C3%A9.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement RG S1A titre II facs 1": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/RG%20S1A%20titre%20II%20facs%201%20zc%20VF%20sign%C3%A9.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement RG S1A titre II facs 2": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/RG%20S1A%20titre%20II%20facs%202%20zc%20VF%20sign%C3%A9.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement RG S1A titre II facs 3": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/RG%20S1A%20titre%20II%20facs%203%20zc%20VF%20sign%C3%A9.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement RG S1A titre II facs 4": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/RG%20S1A%20titre%20II%20facs%204%20zc%20VF%20sign%C3%A9.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement RG S7A fasc 8": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/RG%20S7A%20fasc%208%20MA%2080%20VF.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement RG S7A fasc 14": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/RG%20S7A%20fasc%2014%20RGV%20zc%20V02.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S0": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S0.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S1B": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S1B.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S1D": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S1D.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S1E": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S1E.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S2A": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S2A.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S2B": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S2B.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S2C": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S2C.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S2D": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S2D.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S3A": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S3A.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S3B": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S3B.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
    "Règlement S4A": "https://www.dropbox.com/scl/fo/h8le43o5bndhec2b81zyg/AIHHA4y0-Wr8Wnw_xl0fPNg/S4A.pdf?rlkey=g1xxzzbmecegg21vxdpgd6app&dl=1",
}

@st.cache_resource
def load_and_index_from_dropbox():
    """تحميل المستندات من Dropbox وقراءتها في الذاكرة"""
    search_index = []
    
    for doc_name, url in DROPBOX_PDFS.items():
        # التأكد من أن الرابط مباشر للتحميل بقيمة dl=1
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
                            "download_url": download_url,
                            "view_url": url.replace("dl=1", "dl=0")
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
            snippet = res["text"][:400].replace("\n", " ") + "..."
            download_url = res["download_url"]
            view_url = res["view_url"]
            
            # رابط المعاينة المستند على Google Docs Viewer المستقر
            encoded_download_url = urllib.parse.quote(download_url)
            gdocs_viewer_url = f"https://docs.google.com/gview?url={encoded_download_url}&embedded=true"

            with st.expander(f"📖 {doc_name} — الصفحة {page_num}"):
                st.write(f"**المقتطع النصي:** {snippet}")
                
                # أزرار التوجيه المباشر
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"🔗 [**تحميل / فتح المستند كاملاً (Dropbox)**]({view_url})")
                with col2:
                    st.markdown(f"📥 [**تنزيل ملف الـ PDF مباشرة**]({download_url})")
                
                st.markdown("---")
                st.caption(f"📺 معاينة الصفحة (Google Viewer):")
                
                # استخدام Google Docs Viewer المباشر والموثوق للـ IFRAME
                pdf_iframe = f'<iframe src="{gdocs_viewer_url}#page={page_num}" width="100%" height="500" frameborder="0"></iframe>'
                st.markdown(pdf_iframe, unsafe_allow_html=True)
else:
    st.info("👆 اكتب أي كلمة أو رقم مادة في شريط البحث أعلاه لبدء استخراج النتائج.")
