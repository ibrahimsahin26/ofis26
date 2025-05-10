
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Yönetim Paneli", layout="wide")

# --- Üst Logo ve Başlık ---
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.image("ofis_26_logo.png", width=100)
with col2:
    st.markdown("## 📦 Yönetim Paneli")

# --- Menü ---
secim = st.selectbox("Menü", ["📋 Ürün Listesi", "📊 Stok Sayımı", "⚙️ Tanımlamalar"], label_visibility="collapsed")

# --- Veri Yükle ---
@st.cache_data
def yukle():
    return pd.read_csv("urunler.csv")

if "df" not in st.session_state:
    st.session_state.df = yukle()

# --- Ürün Listesi ---
if secim == "📋 Ürün Listesi":
    st.subheader("📋 Ürün Tablosu ve Filtreler")

    col1, col2, col3, col4 = st.columns(4)
    kategoriler = st.session_state.df["Kategori"].dropna().unique()
    markalar = st.session_state.df["Marka"].dropna().unique()
    tedarikciler = st.session_state.df["Tedarikçi"].dropna().unique()

    with col1:
        f_kat = st.multiselect("Kategori", kategoriler)
    with col2:
        f_marka = st.multiselect("Marka", markalar)
    with col3:
        f_tedarik = st.multiselect("Tedarikçi", tedarikciler)
    with col4:
        arama = st.text_input("Arama (Ad, Barkod, Kod)")

    df = st.session_state.df.copy()
    if f_kat:
        df = df[df["Kategori"].isin(f_kat)]
    if f_marka:
        df = df[df["Marka"].isin(f_marka)]
    if f_tedarik:
        df = df[df["Tedarikçi"].isin(f_tedarik)]
    if arama:
        df = df[df.apply(lambda r: arama.lower() in str(r).lower(), axis=1)]

    df.reset_index(drop=True, inplace=True)
    df.insert(0, "No", df.index + 1)
    st.dataframe(df.head(200), use_container_width=True)

# --- Stok Sayımı ---
elif secim == "📊 Stok Sayımı":
    st.subheader("📊 Ürün Bazlı Stok Sayımı")

    aranan = st.text_input("Ürün Ara (Ad, Kod, Barkod)")
    df = st.session_state.df.copy()
    eslesen = df[df.apply(lambda r: aranan.lower() in str(r).lower(), axis=1)] if aranan else pd.DataFrame()

    if not eslesen.empty:
        urun = eslesen.iloc[0]
        st.markdown(f"### {urun['Ürün Adı']} - Mevcut: {urun.get('Güncel Stok', 0)}")

        raf = st.number_input("Raf", 0, step=1, value=int(urun.get("RAF ADET", 0)))
        kasa = st.number_input("Kasa", 0, step=1, value=int(urun.get("KASA ADET", 0)))
        palet = st.number_input("Palet", 0, step=1, value=int(urun.get("PALET ADET", 0)))

        toplam = raf + kasa + palet
        mevcut = int(urun.get("Güncel Stok", 0))
        fark = toplam - mevcut
        st.markdown(f"**Fark:** {fark}")
    else:
        st.info("Eşleşen ürün bulunamadı.")

# --- Tanımlamalar ---
elif secim == "⚙️ Tanımlamalar":
    st.subheader("⚙️ Tanımlamalar")

    def tanimla(label, anahtar):
        yeni = st.text_input(f"Yeni {label}", key=anahtar)
        if st.button(f"{label} Ekle", key=anahtar + "_btn"):
            st.success(f"{yeni} kaydedildi.")

    with st.expander("Kategori / Marka / Tedarikçi"):
        tanimla("Kategori", "kat")
        tanimla("Marka", "marka")
        tanimla("Tedarikçi", "ted")

    with st.expander("Stok Yeri"):
        tanimla("Raf", "raf")
        tanimla("Kasa", "kasa")
        tanimla("Palet", "palet")
