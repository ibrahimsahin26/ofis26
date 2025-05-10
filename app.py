
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ürün Paneli", layout="wide")
st.title("📦 Ürün - Stok - Fiyat - Tanım Paneli")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "STOK ID", "STOK Kodu", "Barkod", "Ürün Adı", "Kategori", "Marka", "Alış Fiyatı",
        "Kar Marjı (%)", "Satış Fiyatı", "Piyasa Fiyatı", "Tedarikçi",
        "Ofis26 Satış", "HEPCAZİP Satış", "Güncel Stok", "Raf", "Kasa", "Palet"
    ])
if "kategoriler" not in st.session_state:
    st.session_state.kategoriler = []
if "markalar" not in st.session_state:
    st.session_state.markalar = []
if "tedarikciler" not in st.session_state:
    st.session_state.tedarikciler = []

secim = st.selectbox("🔽 Menü", ["📋 Ürün Listesi", "➕ Yeni Ürün", "📊 Stok Sayımı", "⚙️ Tanımlamalar"])

if secim == "📋 Ürün Listesi":
    st.subheader("📋 Ürün Tablosu ve Filtreler")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        filtre_kategori = st.multiselect("Kategori", options=sorted(set(st.session_state.df["Kategori"].dropna())))
    with col2:
        filtre_marka = st.multiselect("Marka", options=sorted(set(st.session_state.df["Marka"].dropna())))
    with col3:
        filtre_tedarikci = st.multiselect("Tedarikçi", options=sorted(set(st.session_state.df["Tedarikçi"].dropna())))
    with col4:
        arama = st.text_input("Arama (Ad, Barkod, Kod)")

    df_filtered = st.session_state.df.copy()
    if filtre_kategori:
        df_filtered = df_filtered[df_filtered["Kategori"].isin(filtre_kategori)]
    if filtre_marka:
        df_filtered = df_filtered[df_filtered["Marka"].isin(filtre_marka)]
    if filtre_tedarikci:
        df_filtered = df_filtered[df_filtered["Tedarikçi"].isin(filtre_tedarikci)]
    if arama:
        df_filtered = df_filtered[df_filtered.apply(lambda row: arama.lower() in str(row).lower(), axis=1)]

    st.dataframe(df_filtered, use_container_width=True)

elif secim == "➕ Yeni Ürün":
    st.subheader("➕ Ürün Ekle")
    with st.form("urun_form"):
        stok_id = st.text_input("STOK ID")
        stok_kodu = st.text_input("STOK Kodu")
        barkod = st.text_input("Barkod")
        ad = st.text_input("Ürün Adı")
        kategori = st.selectbox("Kategori", options=st.session_state.kategoriler)
        marka = st.selectbox("Marka", options=st.session_state.markalar)
        tedarikci = st.selectbox("Tedarikçi", options=st.session_state.tedarikciler)
        alis = st.number_input("Alış Fiyatı", min_value=0.0, step=0.1)
        kar = st.number_input("Kar Marjı (%)", min_value=0.0, max_value=100.0, step=1.0)
        satis = round(alis * (1 + kar / 100), 2) if alis > 0 else 0.0
        st.markdown(f"💰 <b>Satış Fiyatı:</b> <code>{satis}</code>", unsafe_allow_html=True)
        piyasa = st.number_input("Piyasa Fiyatı", min_value=0.0, step=0.1)
        ofis26 = st.number_input("Ofis26 Satış", min_value=0, step=1)
        hepcazip = st.number_input("HEPCAZİP Satış", min_value=0, step=1)
        raf = st.number_input("Raf", min_value=0, step=1)
        kasa = st.number_input("Kasa", min_value=0, step=1)
        palet = st.number_input("Palet", min_value=0, step=1)
        gonder = st.form_submit_button("Ekle")

        if gonder:
            stok = raf + kasa + palet
            yeni = {
                "STOK ID": stok_id, "STOK Kodu": stok_kodu, "Barkod": barkod, "Ürün Adı": ad, "Kategori": kategori,
                "Marka": marka, "Alış Fiyatı": alis, "Kar Marjı (%)": kar, "Satış Fiyatı": satis,
                "Piyasa Fiyatı": piyasa, "Tedarikçi": tedarikci,
                "Ofis26 Satış": ofis26, "HEPCAZİP Satış": hepcazip,
                "Güncel Stok": stok, "Raf": raf, "Kasa": kasa, "Palet": palet
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([yeni])], ignore_index=True)
            st.success("Ürün eklendi.")

elif secim == "📊 Stok Sayımı":
    st.subheader("📊 Stok Güncelle")
    if st.session_state.df.empty:
        st.warning("Önce ürün eklemelisiniz.")
    else:
        for i, row in st.session_state.df.iterrows():
            st.markdown(f"### {row['Ürün Adı']}")
            raf = st.number_input(f"Raf ({row['Barkod']})", value=int(row['Raf']) if pd.notna(row['Raf']) else 0, key=f"raf_{i}")
            kasa = st.number_input(f"Kasa ({row['Barkod']})", value=int(row['Kasa']) if pd.notna(row['Kasa']) else 0, key=f"kasa_{i}")
            palet = st.number_input(f"Palet ({row['Barkod']})", value=int(row['Palet']) if pd.notna(row['Palet']) else 0, key=f"palet_{i}")
            st.session_state.df.at[i, "Raf"] = raf
            st.session_state.df.at[i, "Kasa"] = kasa
            st.session_state.df.at[i, "Palet"] = palet
            st.session_state.df.at[i, "Güncel Stok"] = raf + kasa + palet
        st.success("Stok bilgileri güncellendi.")

elif secim == "⚙️ Tanımlamalar":
    st.subheader("⚙️ Marka, Kategori, Tedarikçi Tanımları")

    def tanimla(label, key):
        yeni = st.text_input(f"Yeni {label}", key=f"input_{key}")
        if st.button(f"Ekle {label}", key=f"btn_{key}"):
            if yeni and yeni not in st.session_state[key]:
                st.session_state[key].append(yeni)
                st.success(f"{yeni} eklendi.")
        st.write(f"Tanımlı {label}:", st.session_state[key])

    tanimla("Kategori", "kategoriler")
    tanimla("Marka", "markalar")
    tanimla("Tedarikçi", "tedarikciler")
