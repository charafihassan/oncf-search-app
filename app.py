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
# 2. قائمة جميع روابط الـ PDF الصحيحة والمحدثة من Dropbox
# ------------------------------------------------------------------
DROPBOX_PDFS = {
    "Règlement S1A - Titre I": "https://www.dropbox.com/scl/fi/0s8pe3sfugugujyxzby2d/R-glement-S1A-Titre-I-version-03-VS.pdf?rlkey=ldghn6rtfu1tqyavmyiwtct67&dl=1",
    "Règlement RG S1A titre II facs 0": "https://www.dropbox.com/scl/fi/lay3km0jcb0zaj79na4we/RG-S1A-titre-II-facs-0-zc-VF-sign.pdf?rlkey=jdv71mtl0pwmmmk0pbbikg4l9&dl=1",
    "Règlement RG S1A titre II facs 1": "https://www.dropbox.com/scl/fi/ur40sjzzcd4yieroqkwm4/RG-S1A-titre-II-facs-1-zc-VF-sign.pdf?rlkey=kctli4qe6pawkb4tdvn9l21ga&dl=1",
    "Règlement RG S1A titre II facs 2": "https://www.dropbox.com/scl/fi/6658qj1h9n9uoymtepjlb/RG-S1A-titre-II-facs-2-zc-VF-sign.pdf?rlkey=3uj99qoo6nfajbivmgufwp4dd&dl=1",
    "Règlement RG S1A titre II facs 3": "https://www.dropbox.com/scl/fi/1aa5kxf2tuu7n3gy9a7xm/RG-S1A-titre-II-facs-3-zc-VF-sign.pdf?rlkey=87hahcpsq3v6vt6i6a8hp5z20&dl=1",
    "Règlement RG S1A titre II facs 4": "https://www.dropbox.com/scl/fi/sanjb1cwymp2or4jd0fq7/RG-S1A-titre-II-facs-4-zc-VF-sign.pdf?rlkey=u7yps9o0hhapxajwivw65btkp&dl=1",
    "Règlement RG S7A fasc 8": "https://www.dropbox.com/scl/fi/7cm8c84eeeze6s6plph23/RG-S7A-fasc-8-MA-80-VF.pdf?rlkey=9yvnaeecv6qvr2pwfok8843qe&dl=1",
    "Règlement RG S7A fasc 14": "https://www.dropbox.com/scl/fi/vxdc6wdquh7yv9wluufd6/RG-S7A-fasc-14-RGV-zc-V02.pdf?rlkey=owfhicrilo2v8fee7f3n692cy&dl=1",
    "Règlement S0": "https://www.dropbox.com/scl/fi/6g0viss15j5wh7w6d3ktg/S0.pdf?rlkey=onrh1kjfuj1wr5acvq87qxpl3&dl=1",
    "Règlement S1B": "https://www.dropbox.com/scl/fi/s5368dmmk81pkuchjzl2a/S1B.pdf?rlkey=6ppr7t8ootapl089e3putgjaa&dl=1",
    "Règlement S1D": "https://www.dropbox.com/scl/fi/ta0fyaxs49la3hq0b0hio/S1D.pdf?rlkey=uujnwuwr5y4218p5si6ficm9a&dl=1",
    "Règlement S1E": "https://www.dropbox.com/scl/fi/qk4lo1q82whd6l0uilaob/S1E.pdf?rlkey=m1ks2st4jevmk1sjyzjgvxgo6&dl=1",
    "Règlement S2A": "https://www.dropbox.com/scl/fi/8kvltmdnas11rfkbf95ej/S2A.pdf?rlkey=6labn4o0ef76a07lxxrtay204&dl=1",
    "Règlement S2B": "https://www.dropbox.com/scl/fi/emv4ly26f1sg7obmmce28/S2B.pdf?rlkey=fa892985ogxj3nfxgyna5x8aq&dl=1",
    "Règlement S2C": "https://www.dropbox.com/scl/fi/lbpfh8dxjqtyn5hmvtenx/S2C.pdf?rlkey=d8q9fi9q76fwsa8ijhpqdfl4x&dl=1",
    "Règlement S2D": "https://www.dropbox.com/scl/fi/wlepyv153sqwnh9suh4to/S2D.pdf?rlkey=vrbry95wzdts9ll7jcpq7mou8&dl=1",
    "Règlement S3A": "https://www.dropbox.com/scl/fi/zrw97rtsxii6oa4yg0exy/S3A.pdf?rlkey=isw2t00hy9zuk69zjjvuslscj&dl=1",
    "Règlement S3B": "https://www.dropbox.com/scl/fi/6jgwlt5h316ovvi8qv0ke/S3B.pdf?rlkey=jnm7yvjy4tu7bzyiq0skvnd2q&dl=1",
    "Règlement S4A": "https://www.dropbox.com/scl/fi/ublpmtcw9i332moi65dax/S4A.pdf?rlkey=rhy0uw4o4hnglapph69m6tv4a&dl=1",
    "Règlement S5A": "https://www.dropbox.com/scl/fi/j8uufjxn06m0wwnsoqq9k/S5A.pdf?rlkey=mztk5n9hes6b0dcrhftqv4b1k&dl=1",
    "Règlement S5C": "https://www.dropbox.com/scl/fi/k3ayx1z8otkns2a3zxwt4/S5C.pdf?rlkey=flrbs33vcco6unjapfwbzfz5q&dl=1",
    "Règlement S5D": "https://www.dropbox.com/scl/fi/evd3gpolbo14r0maj0ha0/S5D.pdf?rlkey=ixwe3wb5gs821ijkckjdin62w&dl=1",
    "Règlement S5E": "https://www.dropbox.com/scl/fi/nhn45ism33x20c5ju9z8h/S5E.pdf?rlkey=al5sips3wy1zov0l156t47h54&dl=1",
    "Règlement S5F": "https://www.dropbox.com/scl/fi/dpm41adzs7q2g1dy5jvqc/S5F.pdf?rlkey=9ydirtwegpt6maqkhtx420jm1&dl=1",
    "Règlement S5G": "https://www.dropbox.com/scl/fi/e8p8pc538a2guhuobmnec/S5G.pdf?rlkey=4q8deygrvce0is2sp8qjq1vaw&dl=1",
    "Règlement S6A": "https://www.dropbox.com/scl/fi/j6mtshjl8i7btlz97tzk2/S6A.pdf?rlkey=bigj9factx0d7odhbphjwbbp4&dl=1",
    "Règlement S6B": "https://www.dropbox.com/scl/fi/elf2cnnrz9nxe7pt9v887/S6B.pdf?rlkey=nsbqob104bmyuvgal0n6jq2ax&dl=1",
    "Règlement S7A-1-P": "https://www.dropbox.com/scl/fi/a9tdxz3o7195y2yyqa12c/S7A-1-P.pdf?rlkey=u33nws3syb02fcbm8dmk2eqq8&dl=1",
    "Règlement S7A-2-P": "https://www.dropbox.com/scl/fi/twe10nvb3cp4f0wpyaw5i/S7A-2-P.pdf?rlkey=wsk8s4ttq6hgmmh2o14e9o2zb&dl=1",
    "Règlement S7A-3-P": "https://www.dropbox.com/scl/fi/cdlfletybfrxcjkn0j7w4/S7A-3-P.pdf?rlkey=qrx57eqv4zy2128cz4zypgl5i&dl=1",
    "Règlement S7A-4-P": "https://www.dropbox.com/scl/fi/vwqbwj5hd447sepqvms8q/S7A-4-P.pdf?rlkey=klr6go13ntqhzym1y2anfujf1&dl=1",
    "Règlement S7C": "https://www.dropbox.com/scl/fi/8zidl2xt4i81g03i5bhgz/S7C.pdf?rlkey=2op6a43a213nkz4rtsph7dj1d&dl=1",
    "Règlement S8A": "https://www.dropbox.com/scl/fi/y9hv8s8isexl97pwqednr/S8A.pdf?rlkey=5kyi226bmd18ob6d8z6thx82z&dl=1",
    "Règlement S8B": "https://www.dropbox.com/scl/fi/it9q0ml1mvfnye5ni6853/S8B.pdf?rlkey=w04bkhp2kdeasyobivbecvx01&dl=1",
    "Règlement S9A": "https://www.dropbox.com/scl/fi/4e4wc308eza6ra2yv9vyv/S9A.pdf?rlkey=l6ckt3yt0jvx0de8o9l6z0w63&dl=1",
    "Règlement S9B": "https://www.dropbox.com/scl/fi/gm148owemf6xxx4vas3q8/S9B.pdf?rlkey=1rgyjlei8gp6265cc9uwp2ah6&dl=1",
    "Règlement S11": "https://www.dropbox.com/scl/fi/ycv4gxrpgpmyoeci0dhru/S11.pdf?rlkey=8o5uw7p9lyvwfaacy4hi377qg&dl=1",
    "CG S0 n°1.pdf": "https://www.dropbox.com/scl/fi/fjbpyqala3tv0kzvggwet/CG-S0-n-1.pdf?rlkey=t13rntcxf4fteb2rhj7ko8yh1&dl=1",
    "CG S0 N°16.pdf": "https://www.dropbox.com/scl/fi/9u20787xzpbqpgtxdl76f/CG-S0-N-16.pdf?rlkey=ed5h63dm0bhht4lgb1b0s46jc&dl=1",
    "CG S0 N°25.pdf": "https://www.dropbox.com/scl/fi/7tds2ndmdkf218i45id2z/CG-S0-N-25.pdf?rlkey=2r3kmbb5dtouv6igzyol7hjh8&dl=1",
    "CG S0 N°27.pdf": "https://www.dropbox.com/scl/fi/pdiec29yv4wqrqzxcp77d/CG-S0-N-27.pdf?rlkey=5icg6qa3dix30k8f9e2weycio&dl=1",
    "CG S0 N°4 2018.pdf": "https://www.dropbox.com/scl/fi/y9gvybys163cwfu25luxr/CG-S0-N-4-2018.pdf?rlkey=pjkg2h1su5on4vgiylkwyqzsw&dl=1",
    "CG S10B n°1.pdf": "https://www.dropbox.com/scl/fi/0l922czmj8d5bs2qq4vhm/CG-S10B-n-1.pdf?rlkey=uxkoc2gtih33iwfc5q25tvkyp&dl=1",
    "CG S1B n°1.pdf": "https://www.dropbox.com/scl/fi/ac7691hcnwyvpih8m7948/CG-S1B-n-1.pdf?rlkey=kwheypmfgn4dpcc0jvidb4or5&dl=1",
    "CG S11 n° 1.pdf": "https://www.dropbox.com/scl/fi/itoc8eyftogefsba53mw1/CG-S11-n-1.pdf?rlkey=h8293n06ngapryfcxxm7g5fd8&dl=1",
    "CG S2A n14.PDF": "https://www.dropbox.com/scl/fi/ufi6o8u2qzmhmmokowrkf/CG-S2A-n14.PDF?rlkey=69ddq73enpkcpdxu0xi6xqjck&dl=1",
    "CG S2A n°1 Ch3.pdf": "https://www.dropbox.com/scl/fi/oq4rtmk7x56zoydtevx8f/CG-S2A-n-1-Ch3.pdf?rlkey=rjceoaqoirgtl65k74vfmauek&dl=1",
    "CG S2A n°1 Chap1.pdf": "https://www.dropbox.com/scl/fi/7myghrnm3ocda6juedawf/CG-S2A-n-1-Chap1.pdf?rlkey=chz6scg0g7jlligcxcicf0q1u&dl=1",
    "CG S2A n°15.pdf": "https://www.dropbox.com/scl/fi/dzltmjred6ai1gnil7lls/CG-S2A-n-15.pdf?rlkey=gyhu1x58zx3nvqrzq872eo4br&dl=1",
    "CG S2A n17.pdf": "https://www.dropbox.com/scl/fi/0x4op64ythky90pyaabro/CG-S2A-n17.pdf?rlkey=3f09gc5ordlnrd58viwh5lezp&dl=1",
    "CG S2A N°18.pdf": "https://www.dropbox.com/scl/fi/r93px9qxtv6dhv34hzozh/CG-S2A-N-18.pdf?rlkey=q6kv69awbtfvx4ahc40tpa719&dl=1",
    "CG S2A n°5 Chap 1.pdf": "https://www.dropbox.com/scl/fi/gctg5a0sbvp7ly34hpcgj/CG-S2A-n-5-Chap-1.pdf?rlkey=e6hnmdujs2oug60n83co15o9g&dl=1",
    "CG S2A n°5 chap 2.pdf": "https://www.dropbox.com/scl/fi/or3wk1by3ljhrh2cir4rn/CG-S2A-n-5-chap-2.pdf?rlkey=o5m70ozwp7yoadwhk9nanltgz&dl=1",
    "CG S2A n°5 chap 3.pdf": "https://www.dropbox.com/scl/fi/2l6rybamafy6zybx94794/CG-S2A-n-5-chap-3.pdf?rlkey=g19kiltnx71wxq8pz9eh5a8xo&dl=1",
    "CG S2A n°6.pdf": "https://www.dropbox.com/scl/fi/wxe4vscywbdejrdd9vu0o/CG-S2A-n-6.pdf?rlkey=im1v9c5ymwr1d50hi899yaprr&dl=1",
    "CG S2A n°8.pdf": "https://www.dropbox.com/scl/fi/zi4ghvnjl2rrqrcx5f1m0/CG-S2A-n-8.pdf?rlkey=tdwvdpmx4y9nro2tk7vlg0ml4&dl=1",
    "CG S2A N°9.pdf": "https://www.dropbox.com/scl/fi/zos9wauqlx430p9aetdmw/CG-S2A-N-9.pdf?rlkey=ilyou0kj9hut315vtndimpt9w&dl=1",
    "CG S2B n°1 - V03.pdf": "https://www.dropbox.com/scl/fi/1jbpzfohd411xxrr62n2f/CG-S2B-n-1-V03.pdf?rlkey=nbxvtnqf1q86x4xlpzlw6jr8x&dl=1",
    "CG S2B N°2.pdf": "https://www.dropbox.com/scl/fi/7ydgx1lfqydzbbsff6vmi/CG-S2B-N-2.pdf?rlkey=jma2gkz9zqy2063ga1g1w9b4v&dl=1",
    "CG S2B n°3.pdf": "https://www.dropbox.com/scl/fi/hnou8ap2er8atolpnami8/CG-S2B-n-3.pdf?rlkey=onrfmymdzsch74gixwyw0lrzu&dl=1",
    "CG S2B n°4.pdf": "https://www.dropbox.com/scl/fi/5x6ccsoudkgtxc75y8yvm/CG-S2B-n-4.pdf?rlkey=k62lw7pvvbuhbs3jkoimbpzh2&dl=1",
    "CG S2C n4 - Incident sur LGV VF zc signé.pdf": "https://www.dropbox.com/scl/fi/74v2jh25kp7hgkmtrbhyb/CG-S2C-n4-Incident-sur-LGV-VF-zc-sign.pdf?rlkey=budowp82713myskfcijg0k9iv&dl=1",
    "CG S2C n5 - Reconnaissance sur LGV VF zc signé.pdf": "https://www.dropbox.com/scl/fi/kat1uavr03vvfnjt7iers/CG-S2C-n5-Reconnaissance-sur-LGV-VF-zc-sign.pdf?rlkey=e6nly8hcperpz4qnooxnitf7i&dl=1",
    "CG S2C n8 - Manuel incident VF signé.pdf": "https://www.dropbox.com/scl/fi/2ogvhs66p1q20taq6f5t3/CG-S2C-n8-Manuel-incident-VF-sign.pdf?rlkey=a6250vu3i1m68nh12lz3mu76a&dl=1",
    "CG S2C n°1.pdf": "https://www.dropbox.com/scl/fi/he7yc336zd5a6t9ejy7l1/CG-S2C-n-1.pdf?rlkey=54i3almjz4l2cxcqmogt78cjr&dl=1",
    "CG S2C n°2.pdf": "https://www.dropbox.com/scl/fi/4blgji0whqtdv2j9jwr18/CG-S2C-n-2.pdf?rlkey=be6hqgv8kjnxa9mxzkhu8wgnh&dl=1",
    "CG S2C n7 exploitation du systeme de detection des boites chaudes (DBC) sol et embarque, et du systeme de detection de freins bloques (DFB) V05.pdf": "https://www.dropbox.com/scl/fi/hxftftoo44kbj9r4mg2a0/CG-S2C-n7-exploitation-du-systeme-de-detection-des-boites-chaudes-DBC-sol-et-embarque-et-du-systeme-de-detection-de-freins-bloques-DFB-V05.pdf?rlkey=9ixzcfv0c47jpsqkpwujxkg23&dl=1",
    "CG S2C n°3.pdf": "https://www.dropbox.com/scl/fi/l4oj8gzhxwex928y9mz7s/CG-S2C-n-3.pdf?rlkey=pctni0fb089tqstz696i3ditl&dl=1",
    "CG S2D n°2 - Points facilement repérables zc VF.pdf": "https://www.dropbox.com/scl/fi/x6r5fidwkdi5o0aacqh5u/CG-S2D-n-2-Points-facilement-rep-rables-zc-VF.pdf?rlkey=kn5x1u3t0vjfvsfpftxj4t70u&dl=1",
    "CG S2D n°3 derangement systèmes embarqués zc VF signé.pdf": "https://www.dropbox.com/scl/fi/1j7285ayllkc4z9sw05og/CG-S2D-n-3-derangement-syst-mes-embarqu-s-zc-VF-sign.pdf?rlkey=cglhcs6j2g33gvylhfr2ewrvr&dl=1",
    "CG S6A n10 -Tome I - VF.pdf": "https://www.dropbox.com/scl/fi/y4lt3u2kg5ekx2cnrp0p7/CG-S6A-n10-Tome-I-VF.pdf?rlkey=8lg9il3xaytd6m78vqjc1d8yc&dl=1",
    "CG S6A n10 -Tome II - vf zc signé.pdf": "https://www.dropbox.com/scl/fi/y9c03iears3c3fvyvf1d3/CG-S6A-n10-Tome-II-vf-zc-sign.pdf?rlkey=4zdyd618v5dhugkb98nmlck25&dl=1",
    "CG S6A n4 2018 zc vf.pdf": "https://www.dropbox.com/scl/fi/c5ibxtsfoavh6uwjn6ore/CG-S6A-n4-2018-zc-vf.pdf?rlkey=oce7ctgypcvcguj4wce4oc00g&dl=1",
    "CG S6A n°11.pdf": "https://www.dropbox.com/scl/fi/vqkedcbzy6qeded656qx4/CG-S6A-n-11.pdf?rlkey=vr14vnufvenb1aex6u8cy68pj&dl=1",
    "CG S6A n°13.pdf": "https://www.dropbox.com/scl/fi/i9pkfzuteszwioum82i82/CG-S6A-n-13.pdf?rlkey=g7oibxc522dsiprkpwo6ojrlc&dl=1",
    "CG S6A n°8.pdf": "https://www.dropbox.com/scl/fi/pho0o4htkpry56qg71wb7/CG-S6A-n-8.pdf?rlkey=jco98mjplq610f4s421n4hx3s&dl=1",
    "CG S6B N°4.pdf": "https://www.dropbox.com/scl/fi/cgxlbpw9kgjz6i3nbf781/CG-S6B-N-4.pdf?rlkey=xjrh877yw31j705b2pxvs99lm&dl=1",
    "CG S7A N°9.pdf": "https://www.dropbox.com/scl/fi/yt977d1izvpylukb3qbku/CG-S7A-N-9.pdf?rlkey=r6tkcfhzzew15hso10ufcuu95&dl=1",
    "CG S9A N°1.pdf": "https://www.dropbox.com/scl/fi/h0v46g0hsga725m62ho2g/CG-S9A-N-1.pdf?rlkey=31wjoewmlfjypx8axo8uu512s&dl=1",
    "CG S9A N°2.pdf": "https://www.dropbox.com/scl/fi/l78t7ob95cyg98ui3g1go/CG-S9A-N-2.pdf?rlkey=inchm8v20ebpckq57v8xxt68o&dl=1",
    "CG S9B N°1.pdf": "https://www.dropbox.com/scl/fi/96555trg42gp3nb7z5ijv/CG-S9B-N-1.pdf?rlkey=tilne9l0kwwmztnudtpgo1jd6&dl=1",
    "CG S9B N°4.pdf": "https://www.dropbox.com/scl/fi/lvckxbpukaspia9y6g4ep/CG-S9B-N-4.pdf?rlkey=5za02snzq3f6keslift0hemlz&dl=1",
    "CG S9B N°5.pdf": "https://www.dropbox.com/scl/fi/llwj3vxlqw097z3dpazc0/CG-S9B-N-5.pdf?rlkey=j77l6nc7diak04iabcpqpqomp&dl=1",
    "CG S9B N°6 2018 zc VF.pdf": "https://www.dropbox.com/scl/fi/j32j9x1ucbk9i5ulbnefr/CG-S9B-N-6-2018-zc-VF.pdf?rlkey=s75y17qcl08lmjsun3821v3t9&dl=1",
    "CGP S0 n 1-19 mise en application docs LGV et LC.pdf": "https://www.dropbox.com/scl/fi/piuikh961vx42ddslpmxe/CGP-S0-n-1-19-mise-en-application-docs-LGV-et-LC.pdf?rlkey=mnd4esk951g31cd9yqc6tlkmh&dl=1",
    "CGP S0n7 - v01 - VF signée.pdf": "https://www.dropbox.com/scl/fi/awll7kn9c5x1s35bb2yvz/CGP-S0n7-v01-VF-sign-e.pdf?rlkey=5mfalx6tvxq2lkkx6afvxh2kp&dl=1",
    "CGP S10B n°3.pdf": "https://www.dropbox.com/scl/fi/mom2et4t3b08nu2sgmo45/CGP-S10B-n-3.pdf?rlkey=2donjjpqck7n318dhyrdum6kj&dl=1",
    "CGP S1A n4 2018.pdf": "https://www.dropbox.com/scl/fi/9wwi2fg33ha9qo6qjhvdk/CGP-S1A-n4-2018.pdf?rlkey=4bglc9c8c55obqrhvavlgbvnb&dl=1",
    "CGP S1A n°1 système de vigilance.pdf": "https://www.dropbox.com/scl/fi/86qg6toiv6663e3yjvfqy/CGP-S1A-n-1-syst-me-de-vigilance.pdf?rlkey=4pnvkcmia843pm5bwckb8higx&dl=1",
    "CGP S1F n2 VF 2018 v2 VF.pdf": "https://www.dropbox.com/scl/fi/m0pdqvqf59vol4e2k1y85/CGP-S1F-n2-VF-2018-v2-VF.pdf?rlkey=a0ef1utudsimnx76716n4omoa&dl=1",
    "CGP S2C n11 alarme DBC dispos complémentaires VS.pdf": "https://www.dropbox.com/scl/fi/nq1fvnhsydkcwav7hpzaj/CGP-S2C-n11-alarme-DBC-dispos-compl-mentaires-VS.pdf?rlkey=gpfd3xnwcnaadhiidu5fgziom&dl=1",
    "CGP S2C n°6.pdf": "https://www.dropbox.com/scl/fi/o6wbgam9mklw9jfmq9wgt/CGP-S2C-n-6.pdf?rlkey=bu24fficf6lk9sfc76d5nv1jt&dl=1",
    "CGP S2D n°1.pdf": "https://www.dropbox.com/scl/fi/jqfnln1i5s8p17yk9ll58/CGP-S2D-n-1.pdf?rlkey=yy5awmusgqp39ch7zmicmjpaa&dl=1",
    "CGP S7A N°2.pdf": "https://www.dropbox.com/scl/fi/w8cv4mj5jzdz7ns9uoby9/CGP-S7A-N-2.pdf?rlkey=6idcjx14qjfnitj0kfmihk7ql&dl=1",
    "CGP S2C n°10 Essai nv seuils DBC BOUGUEDRA VS.pdf": "https://www.dropbox.com/scl/fi/bj5iu9btxow67owkla3ey/CGP-S2C-n-10-Essai-nv-seuils-DBC-BOUGUEDRA-VS.pdf?rlkey=yqzlemgna8efhy4rv2uxb7mzy&dl=1",
    "CGP S2C N°9 Seuils alarme DBC ASILAH.pdf": "https://www.dropbox.com/scl/fi/i1xouljwkmd7esmdq14or/CGP-S2C-N-9-Seuils-alarme-DBC-ASILAH.pdf?rlkey=d3rkl3h3m6c7a7uy0zpbcnbrh&dl=1",
    "CGP S4A n1 - V02.pdf": "https://www.dropbox.com/scl/fi/ir69zmuga0mc1kxqrb1vt/CGP-S4A-n1-V02.pdf?rlkey=s897o7cier5vhzbbuf2z9m246&dl=1",
    "CGP S2D n4 Tamponnement de chiens VS.pdf": "https://www.dropbox.com/scl/fi/b0vv4tdfxrtp9kix1i8fy/CGP-S2D-n4-Tamponnement-de-chiens-VS.pdf?rlkey=jtxxft16ype7q2sh81z5zfns7&dl=1",
    "CGP S7A N 6 circulation a 100km-h des machines seules.pdf": "https://www.dropbox.com/scl/fi/5ia1htxz82179h99wfuhk/CGP-S7A-N-6-circulation-a-100km-h-des-machines-seules.pdf?rlkey=fre7ofrbmxa222djdh7s714el&dl=1",
    "CGP S7A n10 dépassement 65 kmh en UM essais E1450.pdf.pdf": "https://www.dropbox.com/scl/fi/b33dfi9ikshgu2d47vzey/CGP-S7A-n10-d-passement-65-kmh-en-UM-essais-E1450.pdf.pdf?rlkey=h89sfwjuh39403noljetr5bra&dl=1",
    "CGP S7A n°7 - VF.pdf": "https://www.dropbox.com/scl/fi/3txjbouzob2tt1gi4rutt/CGP-S7A-n-7-VF.pdf?rlkey=w0g9z6zcc4wt31ri6ul1w7msc&dl=1",
    "NG S 1A n1 - VISA 2021-VF signé.pdf": "https://www.dropbox.com/scl/fi/2cpe7m9ijcl6tbczm6390/NG-S-1A-n1-VISA-2021-VF-sign.pdf?rlkey=iidrjeyeasgtxnlnghyveihd9&dl=1",
    "NG S0 n°1.Directive d'app Reg S0.pdf": "https://www.dropbox.com/scl/fi/ur51y9l22pyiurceq6iz4/NG-S0-n-1.Directive-d-app-Reg-S0.pdf?rlkey=t9g3qa5vur67lxbofgu2gn81j&dl=1",
    "NG S0A n1 - V03 du 25 10 2024 VS.pdf": "https://www.dropbox.com/scl/fi/rl2xqrf9yz8rylrolyegx/NG-S0A-n1-V03-du-25-10-2024-VS.pdf?rlkey=vlxybvu224qphhh03n95x1y9u&dl=1",
    "NG S11 n°1.pdf": "https://www.dropbox.com/scl/fi/mvpqyeee14kf1ew1fhms9/NG-S11-n-1.pdf?rlkey=tmrxt8xvyzjh13zj4te6rvgjd&dl=1",
    "NG S1D n°1.pdf": "https://www.dropbox.com/scl/fi/6i3hb1ku18crbottz22y5/NG-S1D-n-1.pdf?rlkey=qrqc13p3x9ardbdwzq2i6oy3a&dl=1",
    "NG S2C N2 VF - Règles implantation DBC signé.pdf": "https://www.dropbox.com/scl/fi/urofe7hbntvxkjakvp3zp/NG-S2C-N2-VF-R-gles-implantation-DBC-sign.pdf?rlkey=goxmxtuw0vv11nvrl3ls2zosb&dl=1",
    "NG S3B.pdf": "https://www.dropbox.com/scl/fi/35tn9glp6ck9admd8gjyj/NG-S3B.pdf?rlkey=ptp3bpsv8d7fpeqqik28jabiv&dl=1",
    "NG S6B n20 zc vf signé.pdf": "https://www.dropbox.com/scl/fi/1bz7tf5yc5yt1j0uc7gf6/NG-S6B-n20-zc-vf-sign.pdf?rlkey=b2rwd3mluo45xn5dlzkqpi85x&dl=1",
    "NG S7C n°1.pdf": "https://www.dropbox.com/scl/fi/52ig5995dwr1f9yemkqik/NG-S7C-n-1.pdf?rlkey=hppcown3uk8u50948dwz6wbwi&dl=1",
    "NG S8A n°1.pdf": "https://www.dropbox.com/scl/fi/p5gkbukg11snz8ac25rdz/NG-S8A-n-1.pdf?rlkey=arqekj9pf0itf17wc99sjf217&dl=1",
    "NG S6A n10 V00 vf zc signé.pdf": "https://www.dropbox.com/scl/fi/36p13uwpr6kg7bcitw444/NG-S6A-n10-V00-vf-zc-sign.pdf?rlkey=9zpr9zpr5fp58eiydbv8ddoy3&dl=1",
    "NG S8A N°2 designation des chefs de manoeuvre circuit de validation des consignes locales S8A.pdf": "https://www.dropbox.com/scl/fi/svm6l1vk7dse5jlslqfpo/NG-S8A-N-2-designation-des-chefs-de-manoeuvre-circuit-de-validation-des-consignes-locales-S8A.pdf?rlkey=7hjk7z9k6z8b12405zu6aaslu&dl=1",
    "NG S8B n°1.pdf": "https://www.dropbox.com/scl/fi/pltqzqinxz91zu6a6uvqp/NG-S8B-n-1.pdf?rlkey=52kf8cs6zu52wtaw1hkhrwd96&dl=1",
    "NG TR26e n°1.pdf": "https://www.dropbox.com/scl/fi/1z9yitf8z50ur4qm6o0w6/NG-TR26e-n-1.pdf?rlkey=mjf9immplkjmyzgao0ib4t5cc&dl=1",
    "CG S10B n°2 (a signé).pdf": "https://www.dropbox.com/scl/fi/r0oo1xbd1ifzxhcjbu07r/CG-S10B-n-2-a-sign.pdf?rlkey=gly3ayj78jmtslbwiyw1tqhra&dl=1",
    "CG S10B n4 - 2019 VF.pdf": "https://www.dropbox.com/scl/fi/9fz8cc0vb01a68gvxfc25/CG-S10B-n4-2019-VF.pdf?rlkey=rdtoc8tep9zy0slmr5karryqc&dl=1"
}

@st.cache_resource
def load_and_index_from_dropbox():
    """تحميل المستندات من Dropbox وقراءتها بالكامل"""
    search_index = []
    
    # شريط تقدم لمعالجة الملفات الكبيرة
    progress_bar = st.progress(0)
    total_files = len(DROPBOX_PDFS)
    
    for i, (doc_name, url) in enumerate(DROPBOX_PDFS.items()):
        try:
            # قراءة المادة عبر التنزيل المباشر
            response = requests.get(url, timeout=30)
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
            
            # تحديث شريط التقدم
            progress_bar.progress((i + 1) / total_files)
            
        except Exception as e:
            st.warning(f"⚠️ تعذر قراءة {doc_name}: {e}")
            
    return search_index

# شريط البحث
query = st.text_input("🔍 أدخل كلمة البحث أو رقم المادة (مثال: secours par l'arrière / article 203 / freinage):")

if query:
    with st.spinner("جاري البحث في الملفات..."):
        index_data = load_and_index_from_dropbox()
        
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
                
                # إعداد الرابط للقراءة المباشرة
                raw_url = res["original_url"]
                encoded_pdf_url = urllib.parse.quote(raw_url, safe='')
                pdf_js_viewer_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={encoded_pdf_url}#page={page_num}"

                with st.expander(f"📖 {doc_name} — الصفحة {page_num}"):
                    st.write(f"**المقتطع النصي:** {snippet}")
                    
                    st.markdown(f"👉 [**🔗 اضغط هنا لفتح {doc_name} على الصفحة {page_num} في نافذة كاملة**]({pdf_js_viewer_url})", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.caption(f"📺 المعاينة المباشرة للصفحة {page_num}:")
                    
                    pdf_iframe = f'<iframe src="{pdf_js_viewer_url}" width="100%" height="600" frameborder="0"></iframe>'
                    st.markdown(pdf_iframe, unsafe_allow_html=True)
else:
    st.info("👆 اكتب أي كلمة أو رقم مادة في شريط البحث أعلاه لبدء استخراج النتائج.")
