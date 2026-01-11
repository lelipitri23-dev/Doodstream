import streamlit as st
from doodstream import DoodStreamAPI

# Konfigurasi UI
st.set_page_config(page_title="Doodozer Cloudflare Bypass", page_icon="🛡️")

st.title("🛡️ Doodozer Downloader")
st.markdown("Aplikasi ini menggunakan `cloudscraper` untuk mencoba melewati proteksi Cloudflare.")

# Inisialisasi API (disimpan dalam session agar tidak dibuat ulang terus-menerus)
if 'api' not in st.session_state:
    st.session_state.api = DoodStreamAPI()

url_input = st.text_input("Masukkan URL DoodStream:", placeholder="https://dood.li/d/xxxx")

if st.button("Generate Download Link", type="primary"):
    if url_input:
        with st.spinner("Sedang menembus Cloudflare... Mohon tunggu."):
            # Panggilan sinkron langsung
            result = st.session_state.api.get_download_url(url_input)
            
            if result:
                dl_url, title = result
                st.success(f"Berhasil! Video: **{title}**")
                st.link_button("KLIK UNTUK DOWNLOAD", dl_url)
                st.info("Tips: Jika video terputar otomatis, klik kanan tombol di atas dan pilih 'Save link as'.")
            else:
                st.error("Gagal mendapatkan link. Cloudflare mungkin masih memblokir IP server ini.")
                st.info("Cobalah jalankan script ini di komputer lokal jika server cloud gagal.")
    else:
        st.warning("Silakan masukkan URL.")
