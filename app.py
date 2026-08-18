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
# 2. قائمة جميع روابط الـ PDF الـ 37 الحقيقية من Dropbox
# ------------------------------------------------------------------
DROPBOX_PDFS = {
    "Règlement S1A - Titre I": "https://www.dropbox.com/scl/fi/0s8pe3sfugugujyxzby2d/R-glement-S1A-Titre-I-version-03-VS.pdf?rlkey=ldghn6rtfu1tqyavmyiwtct67&st=uqwy0fun&dl=1",
    "Règlement RG S1A titre II facs 0": "https://www.dropbox.com/scl/fi/lay3km0jcb0zaj79na4we/RG-S1A-titre-II-facs-0-zc-VF-sign.pdf?rlkey=jdv71mtl0pwmmmk0pbbikg4l9&st=b5onjdys&dl=1",
    "Règlement RG S1A titre II facs 1": "https://www.dropbox.com/scl/fi/ur40sjzzcd4yieroqkwm4/RG-S1A-titre-II-facs-1-zc-VF-sign.pdf?rlkey=kctli4qe6pawkb4tdvn9l21ga&st=cmvjgbqh&dl=1",
    "Règlement RG S1A titre II facs 2": "https://www.dropbox.com/scl/fi/6658qj1h9n9uoymtepjlb/RG-S1A-titre-II-facs-2-zc-VF-sign.pdf?rlkey=3uj99qoo6nfajbivmgufwp4dd&st=a404z41c&dl=1",
    "Règlement RG S1A titre II facs 3": "https://www.dropbox.com/scl/fi/1aa5kxf2tuu7n3gy9a7xm/RG-S1A-titre-II-facs-3-zc-VF-sign.pdf?rlkey=87hahcpsq3v6vt6i6a8hp5z20&st=5je2tbx3&dl=1",
    "Règlement RG S1A titre II facs 4": "https://www.dropbox.com/scl/fi/sanjb1cwymp2or4jd0fq7/RG-S1A-titre-II-facs-4-zc-VF-sign.pdf?rlkey=u7yps9o0hhapxajwivw65btkp&st=gln1ort3&dl=1",
    "Règlement RG S7A fasc 8": "https://www.dropbox.com/scl/fi/7cm8c84eeeze6s6plph23/RG-S7A-fasc-8-MA-80-VF.pdf?rlkey=9yvnaeecv6qvr2pwfok8843qe&st=20nclju8&dl=1",
    "Règlement RG S7A fasc 14": "https://www.dropbox.com/scl/fi/vxdc6wdquh7yv9wluufd6/RG-S7A-fasc-14-RGV-zc-V02.pdf?rlkey=owfhicrilo2v8fee7f3n692cy&st=v2533d2f&dl=1",
    "Règlement S0": "https://www.dropbox.com/scl/fi/6g0viss15j5wh7w6d3ktg/S0.pdf?rlkey=onrh1kjfuj1wr5acvq87qxpl3&st=p83lkbn6&dl=1",
    "Règlement S1B": "https://www.dropbox.com/scl/fi/s5368dmmk81pkuchjzl2a/S1B.pdf?rlkey=6ppr7t8ootapl089e3putgjaa&st=yxkfc0jw&dl=1",
    "Règlement S1D": "https://www.dropbox.com/scl/fi/ta0fyaxs49la3hq0b0hio/S1D.pdf?rlkey=uujnwuwr5y4218p5si6ficm9a&st=beqkdphk&dl=1",
    "Règlement S1E": "https://www.dropbox.com/scl/fi/qk4lo1q82whd6l0uilaob/S1E.pdf?rlkey=m1ks2st4jevmk1sjyzjgvxgo6&st=niv1zixo&dl=1",
    "Règlement S2A": "https://www.dropbox.com/scl/fi/8kvltmdnas11rfkbf95ej/S2A.pdf?rlkey=6labn4o0ef76a07lxxrtay204&st=0jvxkpel&dl=1",
    "Règlement S2B": "https://www.dropbox.com/scl/fi/emv4ly26f1sg7obmmce28/S2B.pdf?rlkey=fa892985ogxj3nfxgyna5x8aq&st=fcwl9rnc&dl=1",
    "Règlement S2C": "https://www.dropbox.com/scl/fi/lbpfh8dxjqtyn5hmvtenx/S2C.pdf?rlkey=d8q9fi9q76fwsa8ijhpqdfl4x&st=gc6f50hh&dl=1",
    "Règlement S2D": "https://www.dropbox.com/scl/fi/wlepyv153sqwnh9suh4to/S2D.pdf?rlkey=vrbry95wzdts9ll7jcpq7mou8&st=lbzzur00&dl=1",
    "Règlement S3A": "https://www.dropbox.com/scl/fi/zrw97rtsxii6oa4yg0exy/S3A.pdf?rlkey=isw2t00hy9zuk69zjjvuslscj&st=7y3tmd9e&dl=1",
    "Règlement S3B": "https://www.dropbox.com/scl/fi/6jgwlt5h316ovvi8qv0ke/S3B.pdf?rlkey=jnm7yvjy4tu7bzyiq0skvnd2q&st=noqf7i7o&dl=1",
    "Règlement S4A": "https://www.dropbox.com/scl/fi/ublpmtcw9i332moi65dax/S4A.pdf?rlkey=rhy0uw4o4hnglapph69m6tv4a&st=wrhc3u2d&dl=1",
    "Règlement S5A": "https://www.dropbox.com/scl/fi/j8uufjxn06m0wwnsoqq9k/S5A.pdf?rlkey=mztk5n9hes6b0dcrhftqv4b1k&st=hzbakz9s&dl=1",
    "Règlement S5C": "https://www.dropbox.com/scl/fi/k3ayx1z8otkns2a3zxwt4/S5C.pdf?rlkey=flrbs33vcco6unjapfwbzfz5q&st=w0vyvt78&dl=1",
    "Règlement S5D": "https://www.dropbox.com/scl/fi/evd3gpolbo14r0maj0ha0/S5D.pdf?rlkey=ixwe3wb5gs821ijkckjdin62w&st=hhlz6dl7&dl=1",
    "Règlement S5E": "https://www.dropbox.com/scl/fi/nhn45ism33x20c5ju9z8h/S5E.pdf?rlkey=al5sips3wy1zov0l156t47h54&st=5kww1347&dl=1",
    "Règlement S5F": "https://www.dropbox.com/scl/fi/dpm41adzs7q2g1dy5jvqc/S5F.pdf?rlkey=9ydirtwegpt6maqkhtx420jm1&st=6ay5no09&dl=1",
    "Règlement S5G": "https://www.dropbox.com/scl/fi/e8p8pc538a2guhuobmnec/S5G.pdf?rlkey=4q8deygrvce0is2sp8qjq1vaw&st=xem96q4t&dl=1",
    "Règlement S6A": "https://www.dropbox.com/scl/fi/j6mtshjl8i7btlz97tzk2/S6A.pdf?rlkey=bigj9factx0d7odhbphjwbbp4&st=068fya5x&dl=1",
    "Règlement S6B": "https://www.dropbox.com/scl/fi/elf2cnnrz9nxe7pt9v887/S6B.pdf?rlkey=nsbqob104bmyuvgal0n6jq2ax&st=1nbtx9h3&dl=1",
    "Règlement S7A-1-P": "https://www.dropbox.com/scl/fi/a9tdxz3o7195y2yyqa12c/S7A-1-P.pdf?rlkey=u33nws3syb02fcbm8dmk2eqq8&st=xxfgruvj&dl=1",
    "Règlement S7A-2-P": "https://www.dropbox.com/scl/fi/twe10nvb3cp4f0wpyaw5i/S7A-2-P.pdf?rlkey=wsk8s4ttq6hgmmh2o14e9o2zb&st=ixo7zsz7&dl=1",
    "Règlement S7A-3-P": "https://www.dropbox.com/scl/fi/cdlfletybfrxcjkn0j7w4/S7A-3-P.pdf?rlkey=qrx57eqv4zy2128cz4zypgl5i&st=p82m0wc8&dl=1",
    "Règlement S7A-4-P": "https://www.dropbox.com/scl/fi/vwqbwj5hd447sepqvms8q/S7A-4-P.pdf?rlkey=klr6go13ntqhzym1y2anfujf1&st=lobkdzug&dl=1",
    "Règlement S7C": "https://www.dropbox.com/scl/fi/8zidl2xt4i81g03i5bhgz/S7C.pdf?rlkey=2op6a43a213nkz4rtsph7dj1d&st=cz1svd85&dl=1",
    "Règlement S8A": "https://www.dropbox.com/scl/fi/y9hv8s8isexl97pwqednr/S8A.pdf?rlkey=5kyi226bmd18ob6d8z6thx82z&st=xww7btl2&dl=1",
    "Règlement S8B": "https://www.dropbox.com/scl/fi/it9q0ml1mvfnye5ni6853/S8B.pdf?rlkey=w04bkhp2kdeasyobivbecvx01&st=w6r7f0ok&dl=1",
    "Règlement S9A": "https://www.dropbox.com/scl/fi/4e4wc308eza6ra2yv9vyv/S9A.pdf?rlkey=l6ckt3yt0jvx0de8o9l6z0w63&st=upyn01pk&dl=1",
    "Règlement S9B": "https://www.dropbox.com/scl/fi/gm148owemf6xxx4vas3q8/S9B.pdf?rlkey=1rgyjlei8gp6265cc9uwp2ah6&st=pxq0lj95&dl=1",
    "Règlement S11": "https://www.dropbox.com/scl/fi/ycv4gxrpgpmyoeci0dhru/S11.pdf?rlkey=8o5uw7p9lyvwfaacy4hi377qg&st=b2louckk&dl=1",
}

@st.cache_resource
def load_and_index_from_dropbox():
    """تحميل المستندات من Dropbox وقراءتها بالكامل باستخدام المنطق الأول المستقر"""
    search_index = []
    
    for doc_name, url in DROPBOX_PDFS.items():
        # التأكد من جعل رابط Dropbox يحمل مباشرة بدلاً من العرض
        download_url = url.replace("dl=0", "dl=1")
        if "dl=1" not in download_url:
            download_url += "&dl=1" if "?" in download_url else "?dl=1"
        
        try:
            # قراءة المادة عبر التنزيل المباشر
            response = requests.get(download_url, timeout=45)
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
            
            # إعداد رابط البث المباشر مع استبدال النطاق ليدعم الفتح المبسط
            raw_url = res["original_url"].replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("dl=0", "dl=1")
            
            # ترميز الرابط لاستخدامه في قارئ PDF.js
            encoded_pdf_url = urllib.parse.quote(raw_url, safe='')
            pdf_js_viewer_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={encoded_pdf_url}#page={page_num}"

            with st.expander(f"📖 {doc_name} — الصفحة {page_num}"):
                st.write(f"**المقتطع النصي:** {snippet}")
                
                # رابط خارجي مباشر يفتح القارئ في تبويب جديد على الصفحة بالضبط
                st.markdown(f"👉 [**🔗 اضغط هنا لفتح {doc_name} على الصفحة {page_num} في نافذة كاملة**]({pdf_js_viewer_url})", unsafe_allow_html=True)
                
                st.markdown("---")
                st.caption(f"📺 المعاينة المباشرة للصفحة {page_num}:")
                
                # العرض المدمج
                pdf_iframe = f'<iframe src="{pdf_js_viewer_url}" width="100%" height="600" frameborder="0"></iframe>'
                st.markdown(pdf_iframe, unsafe_allow_html=True)
else:
    st.info("👆 اكتب أي كلمة أو رقم مادة في شريط البحث أعلاه لبدء استخراج النتائج.")
