
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Yönetim Paneli", layout="wide")

col_logo, col_title, col_menu = st.columns([1, 3, 2])
with col_logo:
    st.image("ofis_26_logo.png", width=80)
with col_title:
    st.markdown("<h2 style='margin-top: 20px;'>Yönetim Paneli</h2>", unsafe_allow_html=True)

secim = col_menu.selectbox("Menü", ["📋 Ürün Listesi", "📊 Stok Sayımı", "⚙️ Tanımlamalar"], label_visibility="collapsed")

@st.cache_data
def veri_yukle():
    return pd.read_csv("urunler.csv")

if "df" not in st.session_state:
    st.session_state.df = veri_yukle()

# Tanımlı listeler
if "kategoriler" not in st.session_state:
    st.session_state.kategoriler = list(st.session_state.df["Kategori"].dropna().unique())
if "markalar" not in st.session_state:
    st.session_state.markalar = list(st.session_state.df["Marka"].dropna().unique())
if "tedarikciler" not in st.session_state:
    st.session_state.tedarikciler = list(st.session_state.df["Tedarikçi"].dropna().unique())

if secim == "📋 Ürün Listesi":
    st.subheader("📋 Ürün Tablosu ve Filtreler")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        f_kat = st.multiselect("Kategori", options=st.session_state.kategoriler)
    with col2:
        f_marka = st.multiselect("Marka", options=st.session_state.markalar)
    with col3:
        f_tedarik = st.multiselect("Tedarikçi", options=st.session_state.tedarikciler)
    with col4:
        arama = st.text_input("Ara (Ad, Barkod, Kod)")

    df = st.session_state.df.copy()
    if f_kat:
        df = df[df["Kategori"].isin(f_kat)]
    if f_marka:
        df = df[df["Marka"].isin(f_marka)]
    if f_tedarik:
        df = df[df["Tedarikçi"].isin(f_tedarik)]
    if arama:
        df = df[df.apply(lambda row: arama.lower() in str(row).lower(), axis=1)]

    st.dataframe(df, use_container_width=True)

elif secim == "📊 Stok Sayımı":
    st.subheader("📊 Ürün Bazlı Stok Sayımı")

    urun_ara = st.text_input("Barkod, Kod veya Ad ile Ürün Ara")
    eslesen = st.session_state.df[
        st.session_state.df.apply(lambda r: urun_ara.lower() in str(r).lower(), axis=1)
    ] if urun_ara else pd.DataFrame()

    if not eslesen.empty:
        secilen = eslesen.iloc[0]
        st.markdown(f"### {secilen['Ürün Adı']} (Stok: {secilen['Güncel Stok']})")
        raf = st.number_input("Raf Adeti", min_value=0, value=int(secilen["RAF ADET"]))
        kasa = st.number_input("Kasa Adeti", min_value=0, value=int(secilen["KASA ADET"]))
        palet = st.number_input("Palet Adeti", min_value=0, value=int(secilen["PALET ADET"]))
        yeni_toplam = raf + kasa + palet
        fark = yeni_toplam - int(secilen["Güncel Stok"])
        st.markdown(f"**Fark:** {fark}")
    else:
        st.info("Arama sonucu ürün bulunamadı.")

elif secim == "⚙️ Tanımlamalar":
    st.subheader("⚙️ Tanımlamalar")
    def tanimla(label, key):
        yeni = st.text_input(f"Yeni {label}", key=f"{key}_in")
        if st.button(f"Ekle {label}", key=f"{key}_btn"):
            if yeni and yeni not in st.session_state[key]:
                st.session_state[key].append(yeni)
                st.success(f"{yeni} eklendi.")
        st.write(f"{label} Listesi:", st.session_state[key])

    with st.expander("Kategori / Marka / Tedarikçi"):
        tanimla("Kategori", "kategoriler")
        tanimla("Marka", "markalar")
        tanimla("Tedarikçi", "tedarikciler")

    with st.expander("Stok Yeri"):
        st.markdown("🗂️ **RAF / KASA / PALET numaraları bu bölümden yönetilecek.**")
        tanimla("RAF", "raf_yeri" if "raf_yeri" in st.session_state else st.session_state.setdefault("raf_yeri", []))
        tanimla("KASA", "kasa_yeri" if "kasa_yeri" in st.session_state else st.session_state.setdefault("kasa_yeri", []))
        tanimla("PALET", "palet_yeri" if "palet_yeri" in st.session_state else st.session_state.setdefault("palet_yeri", []))
