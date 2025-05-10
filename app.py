
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Yönetim Paneli", layout="wide")

# --- Üst Logo ve Başlık ---
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.image("ofis_26_logo.png", width=140)
with col2:
    st.markdown("## 📦 Yönetim Paneli")

# --- Menü Seçimi ---
secim = st.selectbox("Menü", ["📋 Ürün Listesi", "➕ Ürün Ekle", "📊 Stok Sayımı", "⚙️ Tanımlamalar"], label_visibility="collapsed")

@st.cache_data
def yukle():
    return pd.read_csv("urunler.csv")

if "df" not in st.session_state:
    st.session_state.df = yukle()

df = st.session_state.df.copy()

# --- Ürün Listesi ---
if secim == "📋 Ürün Listesi":
    st.subheader("📋 Ürün Tablosu ve Filtreler")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kategori = st.selectbox("Kategori", [""] + sorted(df["Kategori"].dropna().unique().tolist()))
    with col2:
        marka = st.selectbox("Marka", [""] + sorted(df["Marka"].dropna().unique().tolist()))
    with col3:
        tedarikci = st.selectbox("Tedarikçi", [""] + sorted(df["Tedarikçi"].dropna().unique().tolist()))
    with col4:
        arama = st.text_input("Arama (Ad, Barkod, Kod)")

    filtreli_df = df.copy()
    if kategori: filtreli_df = filtreli_df[filtreli_df["Kategori"] == kategori]
    if marka: filtreli_df = filtreli_df[filtreli_df["Marka"] == marka]
    if tedarikci: filtreli_df = filtreli_df[filtreli_df["Tedarikçi"] == tedarikci]
    if arama:
        filtreli_df = filtreli_df[filtreli_df.apply(lambda r: arama.lower() in str(r).lower(), axis=1)]

    filtreli_df.reset_index(drop=True, inplace=True)
    filtreli_df.index += 1
    filtreli_df.insert(0, "No", filtreli_df.index)

    st.data_editor(filtreli_df.head(250), use_container_width=True, hide_index=True)

# --- Ürün Ekle ---
elif secim == "➕ Ürün Ekle":
    st.subheader("➕ Yeni Ürün Ekle")

    with st.form("urun_form"):
        col1, col2 = st.columns(2)
        with col1:
            stok_kodu = st.text_input("STOK Kodu")
            barkod = st.text_input("Barkod")
            urun_adi = st.text_input("Ürün Adı")
            kategori = st.text_input("Kategori")
            marka = st.text_input("Marka")
            tedarikci = st.text_input("Tedarikçi")
        with col2:
            alis = st.number_input("Alış Fiyatı", 0.0, step=0.01)
            kar = st.number_input("Kar Marjı (%)", 0.0, 100.0, step=1.0)
            satis = round(alis * (1 + kar / 100), 2)
            st.markdown(f"📌 **Satış Fiyatı**: `{satis}`")
            piyasa = st.number_input("Piyasa Fiyatı", 0.0, step=0.01)
            raf = st.number_input("RAF ADET", 0, step=1)
            kasa = st.number_input("KASA ADET", 0, step=1)
            palet = st.number_input("PALET ADET", 0, step=1)
        
        submitted = st.form_submit_button("Ekle")
        if submitted:
            yeni = {
                "STOK Kodu": stok_kodu,
                "Barkod": barkod,
                "Ürün Adı": urun_adi,
                "Kategori": kategori,
                "Marka": marka,
                "Tedarikçi": tedarikci,
                "Alış Fiyatı": alis,
                "Kar Marjı (%)": kar,
                "Satış Fiyatı": satis,
                "Piyasa Fiyatı": piyasa,
                "RAF ADET": raf,
                "KASA ADET": kasa,
                "PALET ADET": palet,
                "Güncel Stok": raf + kasa + palet
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([yeni])], ignore_index=True)
            st.success("Ürün eklendi.")

# --- Stok Sayımı ---
elif secim == "📊 Stok Sayımı":
    st.subheader("📊 Stok Sayımı")

    aranan = st.text_input("Barkod, Stok Kodu veya Ad")
    bulunan = df[df.apply(lambda r: aranan.lower() in str(r).lower(), axis=1)] if aranan else pd.DataFrame()

    for _, row in bulunan.iterrows():
        st.markdown(f"### {row['Ürün Adı']} ({row['Barkod']}) - Mevcut: {row.get('Güncel Stok', 0)}")
        col1, col2, col3 = st.columns(3)
        with col1:
            raf = st.number_input(f"Raf ({row['Barkod']})", 0, step=1, value=int(row.get("RAF ADET", 0)))
        with col2:
            kasa = st.number_input(f"Kasa ({row['Barkod']})", 0, step=1, value=int(row.get("KASA ADET", 0)))
        with col3:
            palet = st.number_input(f"Palet ({row['Barkod']})", 0, step=1, value=int(row.get("PALET ADET", 0)))
        
        toplam = raf + kasa + palet
        fark = toplam - int(row.get("Güncel Stok", 0))
        st.write(f"**Fark:** {fark}")

# --- Tanımlamalar ---
elif secim == "⚙️ Tanımlamalar":
    st.subheader("⚙️ Tanımlamalar")

    def tanim_ekle(label):
        yeni = st.text_input(f"Yeni {label}", key=label)
        if st.button(f"{label} Ekle", key=label + "_btn"):
            st.success(f"{yeni} eklendi.")

    with st.expander("Kategori / Marka / Tedarikçi"):
        tanim_ekle("Kategori")
        tanim_ekle("Marka")
        tanim_ekle("Tedarikçi")

    with st.expander("Stok Yeri"):
        tanim_ekle("RAF")
        tanim_ekle("KASA")
        tanim_ekle("PALET")
