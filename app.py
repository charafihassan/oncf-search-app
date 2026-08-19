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
    "CG S0 n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/fjbpyqala3tv0kzvggwet/CG-S0-n-1.pdf?rlkey=t13rntcxf4fteb2rhj7ko8yh1",
    "CG S0 N°16.pdf": "https://dl.dropboxusercontent.com/scl/fi/9u20787xzpbqpgtxdl76f/CG-S0-N-16.pdf?rlkey=ed5h63dm0bhht4lgb1b0s46jc",
    "CG S0 N°25.pdf": "https://dl.dropboxusercontent.com/scl/fi/7tds2ndmdkf218i45id2z/CG-S0-N-25.pdf?rlkey=2r3kmbb5dtouv6igzyol7hjh8",
    "CG S0 N°27.pdf": "https://dl.dropboxusercontent.com/scl/fi/pdiec29yv4wqrqzxcp77d/CG-S0-N-27.pdf?rlkey=5icg6qa3dix30k8f9e2weycio",
    "CG S0 N°4 2018.pdf": "https://dl.dropboxusercontent.com/scl/fi/y9gvybys163cwfu25luxr/CG-S0-N-4-2018.pdf?rlkey=pjkg2h1su5on4vgiylkwyqzsw",
    "CG S10B n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/0l922czmj8d5bs2qq4vhm/CG-S10B-n-1.pdf?rlkey=uxkoc2gtih33iwfc5q25tvkyp",
    "CG S1B n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/ac7691hcnwyvpih8m7948/CG-S1B-n-1.pdf?rlkey=kwheypmfgn4dpcc0jvidb4or5",
    "CG S11 n° 1.pdf": "https://dl.dropboxusercontent.com/scl/fi/itoc8eyftogefsba53mw1/CG-S11-n-1.pdf?rlkey=h8293n06ngapryfcxxm7g5fd8",
    "CG S2A n14.PDF": "https://dl.dropboxusercontent.com/scl/fi/ufi6o8u2qzmhmmokowrkf/CG-S2A-n14.PDF?rlkey=69ddq73enpkcpdxu0xi6xqjck",
    "CG S2A n°1 Ch3.pdf": "https://dl.dropboxusercontent.com/scl/fi/oq4rtmk7x56zoydtevx8f/CG-S2A-n-1-Ch3.pdf?rlkey=rjceoaqoirgtl65k74vfmauek",
    "CG S2A n°1 Chap1.pdf": "https://dl.dropboxusercontent.com/scl/fi/7myghrnm3ocda6juedawf/CG-S2A-n-1-Chap1.pdf?rlkey=chz6scg0g7jlligcxcicf0q1u",
    "CG S2A n°15.pdf": "https://dl.dropboxusercontent.com/scl/fi/dzltmjred6ai1gnil7lls/CG-S2A-n-15.pdf?rlkey=gyhu1x58zx3nvqrzq872eo4br",
    "CG S2A n17.pdf": "https://dl.dropboxusercontent.com/scl/fi/0x4op64ythky90pyaabro/CG-S2A-n17.pdf?rlkey=3f09gc5ordlnrd58viwh5lezp",
    "CG S2A N°18.pdf": "https://dl.dropboxusercontent.com/scl/fi/r93px9qxtv6dhv34hzozh/CG-S2A-N-18.pdf?rlkey=q6kv69awbtfvx4ahc40tpa719",
    "CG S2A n°5 Chap 1.pdf": "https://dl.dropboxusercontent.com/scl/fi/gctg5a0sbvp7ly34hpcgj/CG-S2A-n-5-Chap-1.pdf?rlkey=e6hnmdujs2oug60n83co15o9g",
    "CG S2A n°5 chap 2.pdf": "https://dl.dropboxusercontent.com/scl/fi/or3wk1by3ljhrh2cir4rn/CG-S2A-n-5-chap-2.pdf?rlkey=o5m70ozwp7yoadwhk9nanltgz",
    "CG S2A n°5 chap 3.pdf": "https://dl.dropboxusercontent.com/scl/fi/2l6rybamafy6zybx94794/CG-S2A-n-5-chap-3.pdf?rlkey=g19kiltnx71wxq8pz9eh5a8xo",
    "CG S2A n°6.pdf": "https://dl.dropboxusercontent.com/scl/fi/wxe4vscywbdejrdd9vu0o/CG-S2A-n-6.pdf?rlkey=im1v9c5ymwr1d50hi899yaprr",
    "CG S2A n°8.pdf": "https://dl.dropboxusercontent.com/scl/fi/zi4ghvnjl2rrqrcx5f1m0/CG-S2A-n-8.pdf?rlkey=tdwvdpmx4y9nro2tk7vlg0ml4",
    "CG S2A N°9.pdf": "https://dl.dropboxusercontent.com/scl/fi/zos9wauqlx430p9aetdmw/CG-S2A-N-9.pdf?rlkey=ilyou0kj9hut315vtndimpt9w",
    "CG S2B n°1 - V03.pdf": "https://dl.dropboxusercontent.com/scl/fi/1jbpzfohd411xxrr62n2f/CG-S2B-n-1-V03.pdf?rlkey=nbxvtnqf1q86x4xlpzlw6jr8x",
    "CG S2B N°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/7ydgx1lfqydzbbsff6vmi/CG-S2B-N-2.pdf?rlkey=jma2gkz9zqy2063ga1g1w9b4v",
    "CG S2B n°3.pdf": "https://dl.dropboxusercontent.com/scl/fi/hnou8ap2er8atolpnami8/CG-S2B-n-3.pdf?rlkey=onrfmymdzsch74gixwyw0lrzu",
    "CG S2B n°4.pdf": "https://dl.dropboxusercontent.com/scl/fi/5x6ccsoudkgtxc75y8yvm/CG-S2B-n-4.pdf?rlkey=k62lw7pvvbuhbs3jkoimbpzh2",
    "CG S2C n4 - Incident sur LGV VF zc signé.pdf": "https://dl.dropboxusercontent.com/scl/fi/74v2jh25kp7hgkmtrbhyb/CG-S2C-n4-Incident-sur-LGV-VF-zc-sign.pdf?rlkey=budowp82713myskfcijg0k9iv",
    "CG S2C n5 - Reconnaissance sur LGV VF zc signé.pdf": "https://dl.dropboxusercontent.com/scl/fi/kat1uavr03vvfnjt7iers/CG-S2C-n5-Reconnaissance-sur-LGV-VF-zc-sign.pdf?rlkey=e6nly8hcperpz4qnooxnitf7i",
    "CG S2C n8 - Manuel incident VF signé.pdf": "https://dl.dropboxusercontent.com/scl/fi/2ogvhs66p1q20taq6f5t3/CG-S2C-n8-Manuel-incident-VF-sign.pdf?rlkey=a6250vu3i1m68nh12lz3mu76a",
    "CG S2C n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/he7yc336zd5a6t9ejy7l1/CG-S2C-n-1.pdf?rlkey=54i3almjz4l2cxcqmogt78cjr",
    "CG S2C n°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/4blgji0whqtdv2j9jwr18/CG-S2C-n-2.pdf?rlkey=be6hqgv8kjnxa9mxzkhu8wgnh",
    "CG S2C n7 exploitation du systeme de detection des boites chaudes (DBC) sol et embarque, et du systeme de detection de freins bloques (DFB) V05.pdf": "https://dl.dropboxusercontent.com/scl/fi/hxftftoo44kbj9r4mg2a0/CG-S2C-n7-exploitation-du-systeme-de-detection-des-boites-chaudes-DBC-sol-et-embarque-et-du-systeme-de-detection-de-freins-bloques-DFB-V05.pdf?rlkey=9ixzcfv0c47jpsqkpwujxkg23",
    "CG S2C n°3.pdf": "https://dl.dropboxusercontent.com/scl/fi/l4oj8gzhxwex928y9mz7s/CG-S2C-n-3.pdf?rlkey=pctni0fb089tqstz696i3ditl",
    "CG S2D n°2 - Points facilement repérables zc VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/x6r5fidwkdi5o0aacqh5u/CG-S2D-n-2-Points-facilement-rep-rables-zc-VF.pdf?rlkey=kn5x1u3t0vjfvsfpftxj4t70u",
    "CG S2D n°3 derangement systèmes embarqués zc VF signé.pdf": "https://dl.dropboxusercontent.com/scl/fi/1j7285ayllkc4z9sw05og/CG-S2D-n-3-derangement-syst-mes-embarqu-s-zc-VF-sign.pdf?rlkey=cglhcs6j2g33gvylhfr2ewrvr",
    "CG S6A n10 -Tome I - VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/y4lt3u2kg5ekx2cnrp0p7/CG-S6A-n10-Tome-I-VF.pdf?rlkey=8lg9il3xaytd6m78vqjc1d8yc",
    "CG S6A n10 -Tome II - vf zc signé.pdf": "https://dl.dropboxusercontent.com/scl/fi/y9c03iears3c3fvyvf1d3/CG-S6A-n10-Tome-II-vf-zc-sign.pdf?rlkey=4zdyd618v5dhugkb98nmlck25",
    "CG S6A n4 2018 zc vf.pdf": "https://dl.dropboxusercontent.com/scl/fi/c5ibxtsfoavh6uwjn6ore/CG-S6A-n4-2018-zc-vf.pdf?rlkey=oce7ctgypcvcguj4wce4oc00g",
    "CG S6A n°11.pdf": "https://dl.dropboxusercontent.com/scl/fi/vqkedcbzy6qeded656qx4/CG-S6A-n-11.pdf?rlkey=vr14vnufvenb1aex6u8cy68pj",
    "CG S6A n°13.pdf": "https://dl.dropboxusercontent.com/scl/fi/i9pkfzuteszwioum82i82/CG-S6A-n-13.pdf?rlkey=g7oibxc522dsiprkpwo6ojrlc",
    "CG S6A n°8.pdf": "https://dl.dropboxusercontent.com/scl/fi/pho0o4htkpry56qg71wb7/CG-S6A-n-8.pdf?rlkey=jco98mjplq610f4s421n4hx3s",
    "CG S6B N°4.pdf": "https://dl.dropboxusercontent.com/scl/fi/cgxlbpw9kgjz6i3nbf781/CG-S6B-N-4.pdf?rlkey=xjrh877yw31j705b2pxvs99lm",
    "CG S7A N°9.pdf": "https://dl.dropboxusercontent.com/scl/fi/yt977d1izvpylukb3qbku/CG-S7A-N-9.pdf?rlkey=r6tkcfhzzew15hso10ufcuu95",
    "CG S9A N°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/h0v46g0hsga725m62ho2g/CG-S9A-N-1.pdf?rlkey=31wjoewmlfjypx8axo8uu512s",
    "CG S9A N°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/l78t7ob95cyg98ui3g1go/CG-S9A-N-2.pdf?rlkey=inchm8v20ebpckq57v8xxt68o",
    "CG S9B N°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/96555trg42gp3nb7z5ijv/CG-S9B-N-1.pdf?rlkey=tilne9l0kwwmztnudtpgo1jd6",
    "CG S9B N°4.pdf": "https://dl.dropboxusercontent.com/scl/fi/lvckxbpukaspia9y6g4ep/CG-S9B-N-4.pdf?rlkey=5za02snzq3f6keslift0hemlz",
    "CG S9B N°5.pdf": "https://dl.dropboxusercontent.com/scl/fi/llwj3vxlqw097z3dpazc0/CG-S9B-N-5.pdf?rlkey=j77l6nc7diak04iabcpqpqomp",
    "CG S9B N°6 2018 zc VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/j32j9x1ucbk9i5ulbnefr/CG-S9B-N-6-2018-zc-VF.pdf?rlkey=s75y17qcl08lmjsun3821v3t9",
    "CGP S0 n 1-19 mise en application docs LGV et LC.pdf": "https://dl.dropboxusercontent.com/scl/fi/piuikh961vx42ddslpmxe/CGP-S0-n-1-19-mise-en-application-docs-LGV-et-LC.pdf?rlkey=mnd4esk951g31cd9yqc6tlkmh",
    "CGP S0n7 - v01 - VF signée.pdf": "https://dl.dropboxusercontent.com/scl/fi/awll7kn9c5x1s35bb2yvz/CGP-S0n7-v01-VF-sign-e.pdf?rlkey=5mfalx6tvxq2lkkx6afvxh2kp",
    "CGP S10B n°3.pdf": "https://dl.dropboxusercontent.com/scl/fi/mom2et4t3b08nu2sgmo45/CGP-S10B-n-3.pdf?rlkey=2donjjpqck7n318dhyrdum6kj",
    "CGP S1A n4 2018.pdf": "https://dl.dropboxusercontent.com/scl/fi/9wwi2fg33ha9qo6qjhvdk/CGP-S1A-n4-2018.pdf?rlkey=4bglc9c8c55obqrhvavlgbvnb",
    "CGP S1A n°1 système de vigilance.pdf": "https://dl.dropboxusercontent.com/scl/fi/86qg6toiv6663e3yjvfqy/CGP-S1A-n-1-syst-me-de-vigilance.pdf?rlkey=4pnvkcmia843pm5bwckb8higx",
    "CGP S1F n2 VF 2018 v2 VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/m0pdqvqf59vol4e2k1y85/CGP-S1F-n2-VF-2018-v2-VF.pdf?rlkey=a0ef1utudsimnx76716n4omoa",
    "CGP S2C n11 alarme DBC dispos complémentaires VS.pdf": "https://dl.dropboxusercontent.com/scl/fi/nq1fvnhsydkcwav7hpzaj/CGP-S2C-n11-alarme-DBC-dispos-compl-mentaires-VS.pdf?rlkey=gpfd3xnwcnaadhiidu5fgziom",
    "CGP S2C n°6.pdf": "https://dl.dropboxusercontent.com/scl/fi/o6wbgam9mklw9jfmq9wgt/CGP-S2C-n-6.pdf?rlkey=bu24fficf6lk9sfc76d5nv1jt",
    "CGP S2D n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/jqfnln1i5s8p17yk9ll58/CGP-S2D-n-1.pdf?rlkey=yy5awmusgqp39ch7zmicmjpaa",
    "CGP S7A N°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/w8cv4mj5jzdz7ns9uoby9/CGP-S7A-N-2.pdf?rlkey=6idcjx14qjfnitj0kfmihk7ql",
    "CGP S2C n°10 Essai nv seuils DBC BOUGUEDRA VS.pdf": "https://dl.dropboxusercontent.com/scl/fi/bj5iu9btxow67owkla3ey/CGP-S2C-n-10-Essai-nv-seuils-DBC-BOUGUEDRA-VS.pdf?rlkey=yqzlemgna8efhy4rv2uxb7mzy",
    "CGP S2C N°9 Seuils alarme DBC ASILAH.pdf": "https://dl.dropboxusercontent.com/scl/fi/i1xouljwkmd7esmdq14or/CGP-S2C-N-9-Seuils-alarme-DBC-ASILAH.pdf?rlkey=d3rkl3h3m6c7a7uy0zpbcnbrh",
    "CGP S4A n1 - V02.pdf": "https://dl.dropboxusercontent.com/scl/fi/ir69zmuga0mc1kxqrb1vt/CGP-S4A-n1-V02.pdf?rlkey=s897o7cier5vhzbbuf2z9m246",
    "CGP S2D n4 Tamponnement de chiens VS.pdf": "https://dl.dropboxusercontent.com/scl/fi/b0vv4tdfxrtp9kix1i8fy/CGP-S2D-n4-Tamponnement-de-chiens-VS.pdf?rlkey=jtxxft16ype7q2sh81z5zfns7",
    "CGP S7A N 6 circulation a 100km-h des machines seules.pdf": "https://dl.dropboxusercontent.com/scl/fi/5ia1htxz82179h99wfuhk/CGP-S7A-N-6-circulation-a-100km-h-des-machines-seules.pdf?rlkey=fre7ofrbmxa222djdh7s714el",
    "CGP S7A n10 dépassement 65 kmh en UM essais E1450.pdf.pdf": "https://dl.dropboxusercontent.com/scl/fi/b33dfi9ikshgu2d47vzey/CGP-S7A-n10-d-passement-65-kmh-en-UM-essais-E1450.pdf.pdf?rlkey=h89sfwjuh39403noljetr5bra",
    "CGP S7A n°7 - VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/3txjbouzob2tt1gi4rutt/CGP-S7A-n-7-VF.pdf?rlkey=w0g9z6zcc4wt31ri6ul1w7msc",
    "NG S 1A n1 - VISA 2021-VF signé.pdf": "https://dl.dropboxusercontent.com/scl/fi/2cpe7m9ijcl6tbczm6390/NG-S-1A-n1-VISA-2021-VF-sign.pdf?rlkey=iidrjeyeasgtxnlnghyveihd9",
    "NG S0 n°1.Directive d'app Reg S0.pdf": "https://dl.dropboxusercontent.com/scl/fi/ur51y9l22pyiurceq6iz4/NG-S0-n-1.Directive-d-app-Reg-S0.pdf?rlkey=t9g3qa5vur67lxbofgu2gn81j",
    "NG S0A n1 - V03 du 25 10 2024 VS.pdf": "https://dl.dropboxusercontent.com/scl/fi/rl2xqrf9yz8rylrolyegx/NG-S0A-n1-V03-du-25-10-2024-VS.pdf?rlkey=vlxybvu224qphhh03n95x1y9u",
    "NG S11 n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/mvpqyeee14kf1ew1fhms9/NG-S11-n-1.pdf?rlkey=tmrxt8xvyzjh13zj4te6rvgjd",
    "NG S1D n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/6i3hb1ku18crbottz22y5/NG-S1D-n-1.pdf?rlkey=qrqc13p3x9ardbdwzq2i6oy3a",
    "NG S2C N2 VF - Règles implantation DBC signé.pdf": "https://dl.dropboxusercontent.com/scl/fi/urofe7hbntvxkjakvp3zp/NG-S2C-N2-VF-R-gles-implantation-DBC-sign.pdf?rlkey=goxmxtuw0vv11nvrl3ls2zosb",
    "NG S3B.pdf": "https://dl.dropboxusercontent.com/scl/fi/35tn9glp6ck9admd8gjyj/NG-S3B.pdf?rlkey=ptp3bpsv8d7fpeqqik28jabiv",
    "NG S6B n20 zc vf signé.pdf": "https://dl.dropboxusercontent.com/scl/fi/1bz7tf5yc5yt1j0uc7gf6/NG-S6B-n20-zc-vf-sign.pdf?rlkey=b2rwd3mluo45xn5dlzkqpi85x",
    "NG S7C n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/52ig5995dwr1f9yemkqik/NG-S7C-n-1.pdf?rlkey=hppcown3uk8u50948dwz6wbwi",
    "NG S8A n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/p5gkbukg11snz8ac25rdz/NG-S8A-n-1.pdf?rlkey=arqekj9pf0itf17wc99sjf217",
    "NG S6A n10 V00 vf zc signé.pdf": "https://dl.dropboxusercontent.com/scl/fi/36p13uwpr6kg7bcitw444/NG-S6A-n10-V00-vf-zc-sign.pdf?rlkey=9zpr9zpr5fp58eiydbv8ddoy3",
    "NG S8A N°2 designation des chefs de manoeuvre circuit de validation des consignes locales S8A.pdf": "https://dl.dropboxusercontent.com/scl/fi/svm6l1vk7dse5jlslqfpo/NG-S8A-N-2-designation-des-chefs-de-manoeuvre-circuit-de-validation-des-consignes-locales-S8A.pdf?rlkey=7hjk7z9k6z8b12405zu6aaslu",
    "NG S8B n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/pltqzqinxz91zu6a6uvqp/NG-S8B-n-1.pdf?rlkey=52kf8cs6zu52wtaw1hkhrwd96",
    "NG TR26e n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/1z9yitf8z50ur4qm6o0w6/NG-TR26e-n-1.pdf?rlkey=mjf9immplkjmyzgao0ib4t5cc",
    "CG S10B n°2 (a signé).pdf": "https://dl.dropboxusercontent.com/scl/fi/r0oo1xbd1ifzxhcjbu07r/CG-S10B-n-2-a-sign.pdf?rlkey=gly3ayj78jmtslbwiyw1tqhra",
    "CG S10B n4 - 2019 VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/9fz8cc0vb01a68gvxfc25/CG-S10B-n4-2019-VF.pdf?rlkey=rdtoc8tep9zy0slmr5karryqc",
    "00 CDP TR46a N°12 VF 23 092 016.pdf": "https://dl.dropboxusercontent.com/scl/fi/amfygan9mz85syfs4v3hv/00-CDP-TR46a-N-12-VF-23-092-016.pdf?rlkey=y78a724su5z8beu8a08c7uyvc",
    "CC S2B n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/zycm6vmai5jcyqeve1cwb/CC-S2B-n-1.pdf?rlkey=kqn4izr6d1pqt1wrsw26su7fb",
    "CD S0 N43 Liste des ZAL ZAR ZDA GSM-R.pdf": "https://dl.dropboxusercontent.com/scl/fi/h54c7j47isrmr089o45zz/CD-S0-N43-Liste-des-ZAL-ZAR-ZDA-GSM-R.pdf?rlkey=rl9cqh2ew5qs6l2xc0p5dz9xf",
    "CD S0 n°1-2020 mise en application de la CD S6A 33.pdf": "https://dl.dropboxusercontent.com/scl/fi/9rc1iwoxsdquukxjfu4d1/CD-S0-n-1-2020-mise-en-application-de-la-CD-S6A-33.pdf?rlkey=iwzpt1olv869g0skj94vwcksk",
    "CD S0 n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/zpcthd3dsil46zr7auv6h/CD-S0-n-1.pdf?rlkey=s6cdlebc5rtd39hwvw96jqrv1",
    "CD S0 n°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/u5rp3mdg0k0f92dvb0d9a/CD-S0-n-2.pdf?rlkey=cjbstrm772mst0qtlnm9h905o",
    "CD S0 n°31 R9.pdf": "https://dl.dropboxusercontent.com/scl/fi/ipr5zzxiwunl9p3m2b4xh/CD-S0-n-31-R9.pdf?rlkey=vkp33ynu5pcn0sa4e9vint2gv",
    "CD S0 n°33.pdf": "https://dl.dropboxusercontent.com/scl/fi/8ytkwsuc7lykwi61aaimx/CD-S0-n-33.pdf?rlkey=8fc9wz2rzft27l6dofjy199j8",
    "CD S0 n°34.pdf": "https://dl.dropboxusercontent.com/scl/fi/knw09lw3fy09uoin4admm/CD-S0-n-34.pdf?rlkey=dxa8u2urlr7qt7w3323r1c0lx",
    "CD S0 n°36.pdf": "https://dl.dropboxusercontent.com/scl/fi/h0qc0dyeo8hxe6lfepczd/CD-S0-n-36.pdf?rlkey=zav4gymx4aakhy6hameu01jyv",
    "CD S0 n°37.pdf": "https://dl.dropboxusercontent.com/scl/fi/jaax1c9m6lh54zkij10kh/CD-S0-n-37.pdf?rlkey=22xhei5iju83m3lo8nyvbf66h",
    "CD S0 n°38.pdf": "https://dl.dropboxusercontent.com/scl/fi/gbqrx78tv58qckfpdbdty/CD-S0-n-38.pdf?rlkey=zp1lmad3c4j1ihlbf12q9t9s8",
    "CD S0 n°35 V3.pdf": "https://dl.dropboxusercontent.com/scl/fi/lk3tz5pemf5psx3ooqhxi/CD-S0-n-35-V3.pdf?rlkey=drpk2eecvh21c4fz4z62fkwid",
    "CD S0 n°39 utilisation des telephones GSM lors de la circulation des draisines et engins assimiles.pdf": "https://dl.dropboxusercontent.com/scl/fi/elffd0zk5efy00yc1fnma/CD-S0-n-39-utilisation-des-telephones-GSM-lors-de-la-circulation-des-draisines-et-engins-assimiles.pdf?rlkey=9t0q2be4ng6ak8dmd42je7zh3",
    "CD S0 n°40 V02 - Dispositions relatives au service des opérateurs de manœuvre de l’ONCF.pdf": "https://dl.dropboxusercontent.com/scl/fi/u69611r1zedk08a5qe1a9/CD-S0-n-40-V02-Dispositions-relatives-au-service-des-op-rateurs-de-man-uvre-de-l-ONCF.pdf?rlkey=t4h702h14fv7ylc2lav7v5r0i",
    "CD S0 n°41 - CHEFS DE GARES CIRCULATION CONTROLE DE PROXIMITE IMMEDIATE.pdf": "https://dl.dropboxusercontent.com/scl/fi/xhlxgodd6iymguuv8iccn/CD-S0-n-41-CHEFS-DE-GARES-CIRCULATION-CONTROLE-DE-PROXIMITE-IMMEDIATE.pdf?rlkey=1bkc0k50j1sot9ck0wnbaj8mo",
    "CD S0 n°42 -  tenue et entretien des gares Circulation..pdf": "https://dl.dropboxusercontent.com/scl/fi/ztsyk2xugd7qv9rf323sm/CD-S0-n-42-tenue-et-entretien-des-gares-Circulation..pdf?rlkey=oqdce7ne3k3s8rybpkl0wd7zh",
    "CD S0 n°5.pdf": "https://dl.dropboxusercontent.com/scl/fi/ib2i13e9aql64u9twap7l/CD-S0-n-5.pdf?rlkey=szajjmy7uias2pboovv7c3hhk",
    "CD S0 n°53 - Utilisation des moyens de communication à bord des cabines de conduite.pdf": "https://dl.dropboxusercontent.com/scl/fi/40jjytd979fk5zi2rbuom/CD-S0-n-53-Utilisation-des-moyens-de-communication-bord-des-cabines-de-conduite.pdf?rlkey=8ui9heulro7rsk7ej568dsen4",
    "CD S0 n°8 .pdf": "https://dl.dropboxusercontent.com/scl/fi/jdyd1ov9izjtab1q41tpu/CD-S0-n-8.pdf?rlkey=wavrr53x4d6qifn4lwq8j17wf",
    "CD S10B N°31 liste des passages a niveau non gardes a systeme automatique des barrieres (S.A.F.A)(R31).pdf": "https://dl.dropboxusercontent.com/scl/fi/9jmjp77c9nlfykwohwcb1/CD-S10B-N-31-liste-des-passages-a-niveau-non-gardes-a-systeme-automatique-des-barrieres-S.A.F.A-R31.pdf?rlkey=tkvcgqui8lx3dt74pguninzt9",
    "CD S10B n°32 - DISPOSITIONS COMPLEMENTAIRES RELATIVES AUX PASSAGES A NIVEAU A FERMETURE AUTOMATIQUE DES BARRIERES.pdf": "https://dl.dropboxusercontent.com/scl/fi/s1j7qk92890r91pwt7k8f/CD-S10B-n-32-DISPOSITIONS-COMPLEMENTAIRES-RELATIVES-AUX-PASSAGES-A-NIVEAU-A-FERMETURE-AUTOMATIQUE-DES-BARRIERES.pdf?rlkey=agnw9h2cn8kzrfwmaml6xjrue",
    "CD S11 n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/qyu0yh2ccdm4ffns6zpv9/CD-S11-n-1.pdf?rlkey=f5f139ibsdaz1jwv1m93ukgqp",
    "CD S11 n°3.pdf": "https://dl.dropboxusercontent.com/scl/fi/7z8v0a8hoi6bzuijtbbux/CD-S11-n-3.pdf?rlkey=pby08wqlegaudvrhee56yx945",
    "CD S11 n°31 conditions d'acces aux sous stations et postes de sectionnement.pdf": "https://dl.dropboxusercontent.com/scl/fi/wp61oxhx7cytkj1pztb1w/CD-S11-n-31-conditions-d-acces-aux-sous-stations-et-postes-de-sectionnement.pdf?rlkey=xtz96pyrceickxazom43202sr",
    "CD S11 n°33 + annexes.pdf": "https://dl.dropboxusercontent.com/scl/fi/10c8fwnrtjolpe8bq50kp/CD-S11-n-33-annexes.pdf?rlkey=tratwkesxe7n66zpcmkxzcwqv",
    "CD S11 n°35.pdf": "https://dl.dropboxusercontent.com/scl/fi/xz2yurjuymw086fpou81z/CD-S11-n-35.pdf?rlkey=352pte1ey9ixh2t6ioss06thi",
    "CD S11 n°36.pdf": "https://dl.dropboxusercontent.com/scl/fi/lf8vodqbzgkka8e075vem/CD-S11-n-36.pdf?rlkey=r5fha78bwgq2hthk50n8hmu7c",
    "CD S11 n°4.pdf": "https://dl.dropboxusercontent.com/scl/fi/ro3jy9eos0r5x1jipphk1/CD-S11-n-4.pdf?rlkey=enabupa17je09n8pjer6i4m0g",
    "CD S11 n°5.pdf": "https://dl.dropboxusercontent.com/scl/fi/x4h90irapxsqejb6riux2/CD-S11-n-5.pdf?rlkey=lsxnsq7onkxzcjd50x0e3n2tx",
    "CD S11 n°7.pdf": "https://dl.dropboxusercontent.com/scl/fi/xnc4em17rmmrsccvcsicp/CD-S11-n-7.pdf?rlkey=3onzwovxg0mb0lgt5ma1ynixt",
    "CD S11-34. Tableaux de coupure d'urgence R20.pdf": "https://dl.dropboxusercontent.com/scl/fi/7rss7n789jpxrqj52ylfi/CD-S11-34.-Tableaux-de-coupure-d-urgence-R20.pdf?rlkey=6j3uri7bkdaamvtsu5i458x9m",
    "CD S1A n°31 VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/fvbeu97kbwnyy6e9ivgca/CD-S1A-n-31-VF.pdf?rlkey=sh1id6nq3dl5e11wi9q9o7p0b",
    "CD S1A N°51_Réception des trains ETCS, réceptionnés sur les voies de service en gare de Salé Tabriquet via l’entrée sud.pdf": "https://dl.dropboxusercontent.com/scl/fi/swk3ejwm3xox6gvwgila5/CD-S1A-N-51_R-ception-des-trains-ETCS-r-ceptionn-s-sur-les-voies-de-service-en-gare-de-Sal-Tabriquet-via-l-entr-e-sud.pdf?rlkey=27vzymbrdvspnxy50f56yc4lx",
    "CD S1A n°71.pdf": "https://dl.dropboxusercontent.com/scl/fi/6nln85oqqkde0hu9f4t04/CD-S1A-n-71.pdf?rlkey=ifefmbbu940tvs2wt5bwe7tr3",
    "CD S2A n35 CIRCULATION DES TRAINS TRANSPORTANT DES PRODUITS INFLAMMABLES DANS LE TUNNEL SITUE ENTRE RABAT VILLE ET SALE TABRIQUET.pdf": "https://dl.dropboxusercontent.com/scl/fi/xm4q4svlf6i2ffrp8e135/CD-S2A-n35-CIRCULATION-DES-TRAINS-TRANSPORTANT-DES-PRODUITS-INFLAMMABLES-DANS-LE-TUNNEL-SITUE-ENTRE-RABAT-VILLE-ET-SALE-TABRIQUET.pdf?rlkey=d910c85jz0nbrrhsho6iwf6oc",
    "CD S2A n37.pdf": "https://dl.dropboxusercontent.com/scl/fi/dqt5svx8re25bgbfczuck/CD-S2A-n37.pdf?rlkey=uncs5r3m2oy85xgqrayvdtaxr",
    "CD S2A N38 V01 - Mesures à prendre en cas d’interruption de trafic de longue durée sur la ligne classique.pdf": "https://dl.dropboxusercontent.com/scl/fi/06zxyfjy00kqtwaoowqqn/CD-S2A-N38-V01-Mesures-prendre-en-cas-d-interruption-de-trafic-de-longue-dur-e-sur-la-ligne-classique.pdf?rlkey=x9ssthh714lg65v44rhubw361",
    "CD S2A n41-Circulation des trains de Fret le jour entre Casa et Sidi Ichou et retour.pdf": "https://dl.dropboxusercontent.com/scl/fi/5tfk8n1eh086pzh8mnkwy/CD-S2A-n41-Circulation-des-trains-de-Fret-le-jour-entre-Casa-et-Sidi-Ichou-et-retour.pdf?rlkey=qgqve9zx87xpv9izlatq5m6b7",
    "CD S2A n42 - circulation des wagons porte Auto type TAL 489F.pdf": "https://dl.dropboxusercontent.com/scl/fi/2u9cb5ugs8p01od1s8ibc/CD-S2A-n42-circulation-des-wagons-porte-Auto-type-TAL-489F.pdf?rlkey=w2vkp6peyculvgppe2d0kddq2",
    "CD S2A n36 VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/qnjaeip6wlwjh0ddj2i05/CD-S2A-n36-VF.pdf?rlkey=xndkl7q8qwvzrrhjexmcywmfp",
    "CD S2A n51 Circulation des trains assurés par des rames automotrices à 2 niveau (Z2M).pdf": "https://dl.dropboxusercontent.com/scl/fi/91mqsqfbw9ctjpxt2xle9/CD-S2A-n51-Circulation-des-trains-assur-s-par-des-rames-automotrices-2-niveau-Z2M.pdf?rlkey=hpo4vi5pf2bfm420gzq2j0jrh",
    "CD S2A n°11.pdf": "https://dl.dropboxusercontent.com/scl/fi/h1l9c6ox7oarokx67c735/CD-S2A-n-11.pdf?rlkey=qbwj3a4nytd39i5496lzs471v",
    "CD S2A n°12.pdf": "https://dl.dropboxusercontent.com/scl/fi/ffmuxaz22kweck06y5gez/CD-S2A-n-12.pdf?rlkey=1zsgxwqldhmni0hi63r4d9oki",
    "CD S2A n°13.pdf": "https://dl.dropboxusercontent.com/scl/fi/m1tvbore9dfygwlwk7f9j/CD-S2A-n-13.pdf?rlkey=vucon0tm1xmpql7a92zqvtm33",
    "CD S2A n°16.pdf": "https://dl.dropboxusercontent.com/scl/fi/wcbk7togfe0x8vk47wh5y/CD-S2A-n-16.pdf?rlkey=mfw0dykfcnfhyj55gs15hd8ex",
    "CD S2A n°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/u41yqksa96h9pav10qmfj/CD-S2A-n-2.pdf?rlkey=8r67ojzmbi6e1zowqz3cocf9v",
    "CD S2A n°21.pdf": "https://dl.dropboxusercontent.com/scl/fi/fr9vbwkp6sr8xvwljqhsq/CD-S2A-n-21.pdf?rlkey=jqk96gf3out2ltvi1bmmaiwun",
    "CD S2A n°24.pdf": "https://dl.dropboxusercontent.com/scl/fi/3bnvyku7gw3qi2p1ir1m5/CD-S2A-n-24.pdf?rlkey=7a4jbc85l8umxed6iizjchoj8",
    "CD S2A n°31.pdf": "https://dl.dropboxusercontent.com/scl/fi/eq5feoxv5jme5tmpp2csy/CD-S2A-n-31.pdf?rlkey=pf8qqdehnw7nrrctkoq8lqx0r",
    "CD S2A n°32  Finale.pdf": "https://dl.dropboxusercontent.com/scl/fi/b3r2k1cvpw6pfem5do3zo/CD-S2A-n-32-Finale.pdf?rlkey=ghewefhr29f49su3dxbitjdqq",
    "CD S2A n°34 EXPLOITATION DE LA GARE ET DU RACCORDEMENT BENI OUKIL (V02).pdf": "https://dl.dropboxusercontent.com/scl/fi/sph1mxhkepsq1rsf02alu/CD-S2A-n-34-EXPLOITATION-DE-LA-GARE-ET-DU-RACCORDEMENT-BENI-OUKIL-V02.pdf?rlkey=0xw0ia1fcxdj9zxnzu2lw0379",
    "CD S2A n°4.pdf": "https://dl.dropboxusercontent.com/scl/fi/ybfwvyofsc2xnubzajqmh/CD-S2A-n-4.pdf?rlkey=5uv23bpii6sza4lb4bi5av0yn",
    "CD S2A n°6.pdf": "https://dl.dropboxusercontent.com/scl/fi/peoitxnk8x8t6jezli2op/CD-S2A-n-6.pdf?rlkey=l6pg5rz61m9ecgh1cr29ubytv",
    "CD S2A n°7.pdf": "https://dl.dropboxusercontent.com/scl/fi/p8nt0051tq602g47l2dqo/CD-S2A-n-7.pdf?rlkey=ood8eh8h1hijgfhk7xhf8eqa1",
    "CD S2A n°8.pdf": "https://dl.dropboxusercontent.com/scl/fi/nv9q2q0ykxs86yw60hf3p/CD-S2A-n-8.pdf?rlkey=qr7qfp92dwxv9kiw8sk7wpwqz",
    "CD S2A n°9.pdf": "https://dl.dropboxusercontent.com/scl/fi/t14eie1swjkdyus75mke0/CD-S2A-n-9.pdf?rlkey=5r3adnqsmauuqfg5dctthtkia",
    "CD S2C n°3.pdf": "https://dl.dropboxusercontent.com/scl/fi/cchk2a7wqf78y84fc183q/CD-S2C-n-3.pdf?rlkey=zxadyz0fnduuobcriavs32wa2",
    "CD S2B n°31 -  LTV sur LC VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/0lq7o3vx6zhb936792hib/CD-S2B-n-31-LTV-sur-LC-VF.pdf?rlkey=nugmxxs6f45vb9dzwynpu5x1m",
    "CD S2B n°32 LTV sur LGV.pdf": "https://dl.dropboxusercontent.com/scl/fi/ig0eoncu7uozm72e1h8l0/CD-S2B-n-32-LTV-sur-LGV.pdf?rlkey=b2kjipo1l811m6ffr4dga3ie7",
    "CD S2C n°4.pdf": "https://dl.dropboxusercontent.com/scl/fi/enzhsud1slgs7jzqy5bx7/CD-S2C-n-4.pdf?rlkey=28u7q6xvylhqjz8akacewgw96",
    "CD S2C n°35 service de la circulation des trains en gare de casa port V01.pdf": "https://dl.dropboxusercontent.com/scl/fi/7pqclx4lnr9ozwmwk9wdv/CD-S2C-n-35-service-de-la-circulation-des-trains-en-gare-de-casa-port-V01.pdf?rlkey=klkwg5gc3q0e5m4fu7fr3j9va",
    "CD S2C n°37 Autorisation de départ en gare de Ain Sebaâ - abrogé.pdf": "https://dl.dropboxusercontent.com/scl/fi/ahzuy47mu14xghr96rjt2/CD-S2C-n-37-Autorisation-de-d-part-en-gare-de-Ain-Seba-abrog.pdf?rlkey=u28qk66ciyw1dy37ewe5gbg45",
    "CD S2C n°51 - Système de détéction d'incendie  - V2f - validée.pdf": "https://dl.dropboxusercontent.com/scl/fi/pjn6rflwc0w9vb19oq25x/CD-S2C-n-51-Syst-me-de-d-t-ction-d-incendie-V2f-valid-e.pdf?rlkey=2sctxgfke2ad9ln0p9bi86v0c",
    "CD S2C n°52 - Dispositions complémentaires relatives aux arrêts.pdf": "https://dl.dropboxusercontent.com/scl/fi/3uvwr6h2hj4tmcqnsehre/CD-S2C-n-52-Dispositions-compl-mentaires-relatives-aux-arr-ts.pdf?rlkey=o2uh5mr921g2u7253ih73y62a",
    "CD S2C n°6.pdf": "https://dl.dropboxusercontent.com/scl/fi/4ckofh1zh93xv5x129ccb/CD-S2C-n-6.pdf?rlkey=vv9uoo9pr4onmanrg0yiny7xh",
    "CD S2C n°8.pdf": "https://dl.dropboxusercontent.com/scl/fi/tpsfy0iwylhx9re96o15a/CD-S2C-n-8.pdf?rlkey=o3jsrr3zd1d77hjzrigeevw8m",
    "CD S2C n°72 V01 Conditions Transport Matières Dangereuses.pdf": "https://dl.dropboxusercontent.com/scl/fi/wy1epgbmemf7ij3h4536s/CD-S2C-n-72-V01-Conditions-Transport-Mati-res-Dangereuses.pdf?rlkey=qo3lsz81ll0lkcwvo3nito110",
    "CD S2C n°73 Conditions de chargement et de circulation des trains transportant les LRS V2.pdf": "https://dl.dropboxusercontent.com/scl/fi/t64vh5iw2z2lflmrpaa7e/CD-S2C-n-73-Conditions-de-chargement-et-de-circulation-des-trains-transportant-les-LRS-V2.pdf?rlkey=b09rbj8tiln0xah0sbydptjew",
    "CD S2D n°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/n4lj5kaeqq65w3fu5xx9c/CD-S2D-n-2.pdf?rlkey=6l0ab4lx4x4phwyr45d01rxbs",
    "CD S2D n°3.pdf": "https://dl.dropboxusercontent.com/scl/fi/tprkt2j7t54jcmp47bha1/CD-S2D-n-3.pdf?rlkey=44qzn6haxt6e22389yafr3wm0",
    "CD S3B n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/w9ir7b1bsz9px3f0bpnhu/CD-S3B-n-1.pdf?rlkey=uxko8eqbb7sf7g0n99yvmqe0g",
    "CD S6A N41.pdf": "https://dl.dropboxusercontent.com/scl/fi/jmlmc5tywov62vwjinmt9/CD-S6A-N41.pdf?rlkey=3sm2yh4y167rkhh65jvf3uo11",
    "CD S6A n°1-28.pdf": "https://dl.dropboxusercontent.com/scl/fi/n5j8r8bjci368kghg3v7s/CD-S6A-n-1-28.pdf?rlkey=afrcpf86forp9jx4o250i8kj4",
    "CD S6A n°31.pdf": "https://dl.dropboxusercontent.com/scl/fi/liu6sh9djsai0e5wlyd3z/CD-S6A-n-31.pdf?rlkey=zbc8rbqod06q886fdmn3kdptz",
    "CD S6A n°32.pdf": "https://dl.dropboxusercontent.com/scl/fi/o92lt5qyefvulqz7s6ilh/CD-S6A-n-32.pdf?rlkey=amfwg4oqyah9azqckdsfiv50q",
    "CD S6A n°34.pdf": "https://dl.dropboxusercontent.com/scl/fi/blbcihpxvlcgj1qc8xryi/CD-S6A-n-34.pdf?rlkey=07rvbrngdsonoscpyj4kc3j2g",
    "CD S6B n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/k0gv8svqn9ulg1x8jaca6/CD-S6B-n-1.pdf?rlkey=5x2c0qb3pg91uhqbh2f6xsuxa",
    "CD S6A n°33 V04 - Schémas Synthétiques des Installations des sections de lignes télécommandées.pdf": "https://dl.dropboxusercontent.com/scl/fi/en5qbsybjnyzqzaw0kzwu/CD-S6A-n-33-V04-Sch-mas-Synth-tiques-des-Installations-des-sections-de-lignes-t-l-command-es.pdf?rlkey=uze4nlrhco91ahmlyor3qtdnw",
    "CD S6A n°35.pdf": "https://dl.dropboxusercontent.com/scl/fi/178wfu2tbki0tqtz7wcti/CD-S6A-n-35.pdf?rlkey=iwitybei32fle8ue2rwpsvbi2",
    "CD S6A n°36 VF.pdf": "https://dl.dropboxusercontent.com/scl/fi/7rex6zxonsih906itsd6v/CD-S6A-n-36-VF.pdf?rlkey=ja607by2m6px2124oxgsh6613",
    "CD S6A n°39 postes a manettes libres a commande electrique des aiguilles.pdf": "https://dl.dropboxusercontent.com/scl/fi/vnm6q1x63z3r7dsx3ewlr/CD-S6A-n-39-postes-a-manettes-libres-a-commande-electrique-des-aiguilles.pdf?rlkey=f81c06htce5txyqrn6udn9n8r",
    "CD S6B n°31 V01.pdf": "https://dl.dropboxusercontent.com/scl/fi/39uams2kjty5iep5yjujm/CD-S6B-n-31-V01.pdf?rlkey=qrqglgn63bmaayf1o3grretif",
    "CD S6B n°32 final.pdf": "https://dl.dropboxusercontent.com/scl/fi/4xiw4y0koex8oa68qxpmu/CD-S6B-n-32-final.pdf?rlkey=y55zd99gnohe7kxcu1id6gbcy",
    "CD S6B N°33.pdf": "https://dl.dropboxusercontent.com/scl/fi/v1evguspq83m1cwesz94g/CD-S6B-N-33.pdf?rlkey=6m98loxcellzheu0v0414ixwg",
    "CD S7A n°10.pdf": "https://dl.dropboxusercontent.com/scl/fi/t8x868g7zjjsx5jcjoqoi/CD-S7A-n-10.pdf?rlkey=soefglupcjuslnq288eg7a9b8",
    "CD S7A n°11.pdf": "https://dl.dropboxusercontent.com/scl/fi/1smrrcujk7p0oimrnbgld/CD-S7A-n-11.pdf?rlkey=zaqz36sqj5c4pkl7j0d3xdr89",
    "CD S7A N°13 Version 42.pdf": "https://dl.dropboxusercontent.com/scl/fi/rsqd3upyrylfizqk94o7d/CD-S7A-N-13-Version-42.pdf?rlkey=jf2nw35acxlimi1opnt6aw517",
    "CD S7A n°2 Longeur utiles des voies de réception et des voies de garage des gares (R10).pdf": "https://dl.dropboxusercontent.com/scl/fi/mr4gx7w445kioug0enr83/CD-S7A-n-2-Longeur-utiles-des-voies-de-r-ception-et-des-voies-de-garage-des-gares-R10.pdf?rlkey=v0ady0d6hjru1a3awenewem8n",
    "CD S7C n°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/2w4iqfodpz56rmjjwisw5/CD-S7C-n-2.pdf?rlkey=xfvjwwgbunwgurqhvwldrks86",
    "CD S7A n°7.pdf": "https://dl.dropboxusercontent.com/scl/fi/m8va0b1k0lban0jry4x07/CD-S7A-n-7.pdf?rlkey=jpl1cst0m4qzja1xcfnso606w",
    "CD T46a n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/edy61jhd1xejf7ohbnwn9/CD-T46a-n-1.pdf?rlkey=7ewzzb4xcgedvt7v4da2y4kv7",
    "CD T46a n°10.pdf": "https://dl.dropboxusercontent.com/scl/fi/69ruo7uunnkw6dbqo2lia/CD-T46a-n-10.pdf?rlkey=vghrlgiqhb1elbwjrv9hd6k6o",
    "CD T46a n°3.pdf": "https://dl.dropboxusercontent.com/scl/fi/2qva9ed29vzh4v0whhlyk/CD-T46a-n-3.pdf?rlkey=idscilwm5xumbdf2rfhhiwuww",
    "CD TR 26a n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/dzzx758sp088955hkpams/CD-TR-26a-n-1.pdf?rlkey=4sy7vy1osyheus5rj3xqvvg45",
    "CD TR 26a n°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/8xeg99cqoic4gt0rlvbei/CD-TR-26a-n-2.pdf?rlkey=927q4zk7zd6uirpfnmty9r02b",
    "CD TR 31a n°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/zgbkq72ng9gregesa0o8c/CD-TR-31a-n-2.pdf?rlkey=emffb1ueknjqo86kt6dwmsykx",
    "CD TR 31a.pdf": "https://dl.dropboxusercontent.com/scl/fi/b19uylx55rryk24hxawcp/CD-TR-31a.pdf?rlkey=2od7eg55l5u39662lyz3cy4m0",
    "CD TR 46a n°11.pdf": "https://dl.dropboxusercontent.com/scl/fi/7ym9umxwjdcoud0cb0m5u/CD-TR-46a-n-11.pdf?rlkey=efk9kgdpoupd8spladdft7hvf",
    "CDP S0 n° 51  Camera-- VF Validée le 28-12-2016.pdf": "https://dl.dropboxusercontent.com/scl/fi/904vkmoi7v6u8ee7vkj44/CDP-S0-n-51-Camera-VF-Valid-e-le-28-12-2016.pdf?rlkey=7r912s3e1ro7a9pvuyb5bn6yz",
    "CDP S2A n°10.pdf": "https://dl.dropboxusercontent.com/scl/fi/rdosfluwjqzwzhce2i5xk/CDP-S2A-n-10.pdf?rlkey=03df7hu4qnrmfkmykqmuh17qf",
    "CDP S2A n°25.pdf": "https://dl.dropboxusercontent.com/scl/fi/y04xdh1kwrw8s31f8ffh0/CDP-S2A-n-25.pdf?rlkey=x29l1nczkwwqwmve63wgljm4u",
    "CDP S2C n°1 (1).pdf": "https://dl.dropboxusercontent.com/scl/fi/b5m0szzznf6oygwd2hbvd/CDP-S2C-n-1-1.pdf?rlkey=85u8kiiszja3v2sta462zsdxs",
    "CDP S2A N°33 V01.pdf": "https://dl.dropboxusercontent.com/scl/fi/c8cnnt7prty75058wdlnr/CDP-S2A-N-33-V01.pdf?rlkey=1fnibjmphuco4hzcgggfhu9ur",
    "CDP S2C n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/qco4hvgji9u53uaub5hcm/CDP-S2C-n-1.pdf?rlkey=qjawfep21ubum8vu807nqboin",
    "CDP S2C n°10.pdf": "https://dl.dropboxusercontent.com/scl/fi/9zbc65o25emnv1e53oh1q/CDP-S2C-n-10.pdf?rlkey=f3rd7kro80co2yrwexub959ko",
    "CDP S2C n°11.pdf": "https://dl.dropboxusercontent.com/scl/fi/05sk3l7k295rl0xhqlmtz/CDP-S2C-n-11.pdf?rlkey=cuwz92pea9atknq33lgz6hcpo",
    "CDP S3C n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/pals0zoyc3chflqhxbalk/CDP-S3C-n-1.pdf?rlkey=7whh831icra7tidhk4nvx94md",
    "CDP S7A n°1-95.pdf": "https://dl.dropboxusercontent.com/scl/fi/ywd04vxzu884r6zf8386v/CDP-S7A-n-1-95.pdf?rlkey=ormkz5rtgxf966xjauju650bz",
    "CDP S7A n°15.pdf": "https://dl.dropboxusercontent.com/scl/fi/0ekgjz9m6gvckner7v0so/CDP-S7A-n-15.pdf?rlkey=fkiw5muv6358speg6ytespjeg",
    "CDP TR 46a n°72.pdf": "https://dl.dropboxusercontent.com/scl/fi/gq3kg4ze571yit3jxqgi4/CDP-TR-46a-n-72.pdf?rlkey=0a9du18arp6pws9u06b1qjrrj",
    "CDP TR 46a n°8.pdf": "https://dl.dropboxusercontent.com/scl/fi/zzhyf7ju9gj2hi0n2znr1/CDP-TR-46a-n-8.pdf?rlkey=t4g2eea70ympg3jcelloito4a",
    "CDs S2B n°1 (1).pdf": "https://dl.dropboxusercontent.com/scl/fi/upi5c97wybnxy8k0ob2cc/CDs-S2B-n-1-1.pdf?rlkey=df6tmigx32zb6zb52ybu6q6fd",
    "CD S6A n°38 dispositions complementaires relatives a l'exploitation des IHM N0-PC et CTC.pdf": "https://dl.dropboxusercontent.com/scl/fi/vdd22g4a30h9dx0d7s7bs/CD-S6A-n-38-dispositions-complementaires-relatives-a-l-exploitation-des-IHM-N0-PC-et-CTC.pdf?rlkey=urrqmhkzngd8l7p7yo1js7c0w",
    "CONCIGNE DIRECTION S11N36 (003).pdf": "https://dl.dropboxusercontent.com/scl/fi/783fo0i6u4lhwv2a0mmhq/CONCIGNE-DIRECTION-S11N36-003.pdf?rlkey=wa7fyi44n4fagk61xds9jqt2l",
    "NG TR26e n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/4zlo965p6shjvjhvkh273/NG-TR26e-n-1.pdf?rlkey=bldrnyrptfzqw9ce2atgqvm9r",
    "CD S6A n°40 Manuelle d'utilisation de l'interface graphique du CTC 1000.pdf": "https://dl.dropboxusercontent.com/scl/fi/d13t6gf86g4qg2s9be4ar/CD-S6A-n-40-Manuelle-d-utilisation-de-l-interface-graphique-du-CTC-1000.pdf?rlkey=j1w4a5cpaice3d12tzed0r9wg",
    "CD S7A n°4.pdf": "https://dl.dropboxusercontent.com/scl/fi/mv407qe0pisa77v7fhec6/CD-S7A-n-4.pdf?rlkey=ierzy4vgmrwzd7aaegmnlg13u",
    "CD S7C n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/zyr65u4g5tvbno6pbe8i4/CD-S7C-n-1.pdf?rlkey=sz867w87f9584nb5h8z3j1t62",
    "CD S8A n31 - Dispositions relatives à la manœuvre.pdf": "https://dl.dropboxusercontent.com/scl/fi/400cxp3mtqynfkrmy7ukt/CD-S8A-n31-Dispositions-relatives-la-man-uvre.pdf?rlkey=lz7gdcdqtlwiqvqo07vlbk6qs",
    "CD S8A n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/74k9o89zvzrz3njcutfwm/CD-S8A-n-1.pdf?rlkey=q2g01kj9alpgknjltjzgq3hhm",
    "CD S8A n°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/t5yt3d8t3hzrm83jymam3/CD-S8A-n-2.pdf?rlkey=ggkt09u66dlnee2z8y0uq88t1",
    "CD S9B n°1 .pdf": "https://dl.dropboxusercontent.com/scl/fi/lxpzjefeex29leeqtjovh/CD-S9B-n-1.pdf?rlkey=dyfl3q6ogeg10sf9evi2t9c17",
    "CD T46a n°4.pdf": "https://dl.dropboxusercontent.com/scl/fi/dct52xqaaob2ypdcocxyz/CD-T46a-n-4.pdf?rlkey=ige5a0n3af0v1z5csupmz0n0d",
    "CD TR 11c n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/uz3w6uer97lxarph4tqfu/CD-TR-11c-n-1.pdf?rlkey=wms2f8lkdweygcytigjdwamm9",
    "CDP S0 n° 52  Assistance en ligne des conducteurs de ligne.pdf": "https://dl.dropboxusercontent.com/scl/fi/65u1dl136dmyzl508sney/CDP-S0-n-52-Assistance-en-ligne-des-conducteurs-de-ligne.pdf?rlkey=reoqm181x650yx204etocusdw",
    "CDP S2A n°23.pdf": "https://dl.dropboxusercontent.com/scl/fi/e54vhd93ti07jy1ts54r9/CDP-S2A-n-23.pdf?rlkey=4vavndurx6mpepf8t60bsv11e",
    "CDP S0 n°012021.pdf": "https://dl.dropboxusercontent.com/scl/fi/c6ztnbgie4t6wlyceykyj/CDP-S0-n-012021.pdf?rlkey=l2bax5dbwxhxmh1ayehzh6dp2",
    "CDP S0 n°2-2020 mise en application de la CD S6A 38.pdf": "https://dl.dropboxusercontent.com/scl/fi/0p7sth65f8b8nef85ddfg/CDP-S0-n-2-2020-mise-en-application-de-la-CD-S6A-38.pdf?rlkey=67hpjplfvs2usl8nkqo8fj1rm",
    "CDP S6A n°41 V01_Circulation et stationnement sur les circuits de voie dans le périmètre des PCL.pdf": "https://dl.dropboxusercontent.com/scl/fi/uav3mf7awdaxgq9ucnhee/CDP-S6A-n-41-V01_Circulation-et-stationnement-sur-les-circuits-de-voie-dans-le-p-rim-tre-des-PCL.pdf?rlkey=wuhsk91nvz6pu8zeg7s48ypwv",
    "CDP S7A n°1-2004.pdf": "https://dl.dropboxusercontent.com/scl/fi/uvg042bak3d8vljnhohy3/CDP-S7A-n-1-2004.pdf?rlkey=166mcoajcrpslmwxrkc8yhlca",
    "CDP S7A n°9.pdf": "https://dl.dropboxusercontent.com/scl/fi/06eseu6p3xh1ridnhql3o/CDP-S7A-n-9.pdf?rlkey=zvqdbnvaj3hgtf7xc4rodq3cr",
    "CDP S8B n°2.pdf": "https://dl.dropboxusercontent.com/scl/fi/qpaj6j7z2boi3vuedrnou/CDP-S8B-n-2.pdf?rlkey=gcg3r9i7d5u1otra5r5law69l",
    "CDP TR 46a n°7.pdf": "https://dl.dropboxusercontent.com/scl/fi/nmot9bp9fvltf6l3dka4h/CDP-TR-46a-n-7.pdf?rlkey=k84v1fc1kuitwzu60rn897xc9",
    "CDs S2B n°1.pdf": "https://dl.dropboxusercontent.com/scl/fi/mie6y4hyd07ueu5voavpg/CDs-S2B-n-1.pdf?rlkey=9e4gg9eexfhcuiqz6mbg8xzgh"
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
