
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Yönetim Paneli", layout="wide")

col_logo, col_title, col_menu = st.columns([1, 3, 2])
with col_logo:
    st.image("ofis_26_logo.png", width=80)
with col_title:
    st.markdown("<h2 style='margin-top: 20px;'>Yönetim Paneli</h2>", unsafe_allow_html=True)

secim = col_menu.selectbox("Menü", ["📋 Ürün Listesi", "➕ Yeni Ürün", "📊 Stok Sayımı", "⚙️ Tanımlamalar"], label_visibility="collapsed")

if "df" not in st.session_state:
    st.session_state.df = pd.read_csv("urunler.csv")

if "kategoriler" not in st.session_state:
    st.session_state.kategoriler = list(st.session_state.df["Kategori"].dropna().unique())
if "markalar" not in st.session_state:
    st.session_state.markalar = list(st.session_state.df["Marka"].dropna().unique())
if "tedarikciler" not in st.session_state:
    st.session_state.tedarikciler = list(st.session_state.df["Tedarikçi"].dropna().unique())

if secim == "📋 Ürün Listesi":
    st.subheader("📋 Ürün Tablosu")
    st.dataframe(st.session_state.df, use_container_width=True)

elif secim == "➕ Yeni Ürün":
    st.subheader("➕ Yeni Ürün Ekle")
    with st.form("ekle"):
        col1, col2 = st.columns(2)
        with col1:
            stok_id = st.text_input("STOK ID")
            stok_kodu = st.text_input("STOK Kodu")
            barkod = st.text_input("Barkod")
            ad = st.text_input("Ürün Adı")
            kategori = st.selectbox("Kategori", options=st.session_state.kategoriler)
            marka = st.selectbox("Marka", options=st.session_state.markalar)
            tedarikci = st.selectbox("Tedarikçi", options=st.session_state.tedarikciler)
        with col2:
            alis = st.number_input("Alış Fiyatı", min_value=0.0)
            kar = st.number_input("Kar Marjı (%)", min_value=0.0, max_value=100.0)
            satis = round(alis * (1 + kar / 100), 2)
            st.markdown(f"**Satış Fiyatı:** <code>{satis}</code>", unsafe_allow_html=True)
            piyasa = st.number_input("Piyasa Fiyatı", min_value=0.0)
            ofis = st.number_input("Ofis26 Satış", min_value=0)
            hepcazip = st.number_input("HEPCAZİP Satış", min_value=0)
            raf = st.number_input("Raf", min_value=0)
            kasa = st.number_input("Kasa", min_value=0)
            palet = st.number_input("Palet", min_value=0)

        gonder = st.form_submit_button("Ürünü Ekle")
        if gonder:
            stok = raf + kasa + palet
            yeni = {
                "STOK ID": stok_id, "STOK Kodu": stok_kodu, "Barkod": barkod, "Ürün Adı": ad, "Kategori": kategori,
                "Marka": marka, "Alış Fiyatı": alis, "Kar Marjı (%)": kar, "Satış Fiyatı": satis,
                "Piyasa Fiyatı": piyasa, "Tedarikçi": tedarikci,
                "Ofis26 Satış": ofis, "HEPCAZİP Satış": hepcazip,
                "Güncel Stok": stok, "Raf": raf, "Kasa": kasa, "Palet": palet
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([yeni])], ignore_index=True)
            st.success("Ürün eklendi.")

elif secim == "📊 Stok Sayımı":
    st.subheader("📊 Stok Sayımı")
    for i, row in st.session_state.df.iterrows():
        st.markdown(f"### {row['Ürün Adı']} - Mevcut: {row['Güncel Stok']}")
        raf = st.number_input(f"Raf ({row['Barkod']})", value=int(row['Raf']), key=f"raf_{i}")
        kasa = st.number_input(f"Kasa ({row['Barkod']})", value=int(row['Kasa']), key=f"kasa_{i}")
        palet = st.number_input(f"Palet ({row['Barkod']})", value=int(row['Palet']), key=f"palet_{i}")
        fark = (raf + kasa + palet) - row['Güncel Stok']
        st.session_state.df.at[i, "Raf"] = raf
        st.session_state.df.at[i, "Kasa"] = kasa
        st.session_state.df.at[i, "Palet"] = palet
        st.session_state.df.at[i, "Güncel Stok"] = raf + kasa + palet
        st.markdown(f"**Fark:** {fark}")

elif secim == "⚙️ Tanımlamalar":
    st.subheader("⚙️ Tanımlamalar")
    def tanimla(label, key):
        yeni = st.text_input(f"Yeni {label}", key=f"{key}_input")
        if st.button(f"Ekle {label}", key=f"{key}_btn"):
            if yeni and yeni not in st.session_state[key]:
                st.session_state[key].append(yeni)
                st.success(f"{yeni} eklendi.")
        st.write("Tanımlı:", st.session_state[key])

    with st.expander("Kategori / Marka / Tedarikçi"):
        tanimla("Kategori", "kategoriler")
        tanimla("Marka", "markalar")
        tanimla("Tedarikçi", "tedarikciler")
