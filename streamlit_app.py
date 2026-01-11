import streamlit as st
import asyncio
import aiohttp
import re
from doodstream import DoodStreamAPI

# Konfigurasi Halaman
st.set_page_config(page_title="Doodozer Downloader", page_icon="🚀")

st.title("🚀 Doodozer Downloader")
st.markdown("Masukkan URL DoodStream untuk mendapatkan link unduhan langsung.")

# Fungsi asinkron untuk mengambil data
async def fetch_dood_data(url):
    async with aiohttp.ClientSession() as session:
        api = DoodStreamAPI(session)
        return await api.get_download_url(url)

# Input URL
url_input = st.text_input("URL DoodStream:", placeholder="https://dood.la/e/xxxx")

if st.button("Dapatkan Link"):
    if url_input:
        if "dood" in url_input:
            with st.spinner("Sedang memproses..."):
                try:
                    # Menjalankan fungsi async di Streamlit
                    result = asyncio.run(fetch_dood_data(url_input))
                    
                    if result:
                        download_url, title = result
                        st.success("Berhasil mengekstrak link!")
                        st.write(f"**Judul:** {title}")
                        
                        # Tombol Download
                        st.link_button("DOWNLOAD VIDEO", download_url, type="primary")
                        st.info("Catatan: Jika video hanya terputar, klik kanan tombol dan pilih 'Save link as'.")
                    else:
                        st.error("Gagal mendapatkan link. Pastikan URL benar atau coba lagi nanti.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
        else:
            st.warning("Mohon masukkan URL DoodStream yang valid.")
    else:
        st.warning("Silakan masukkan URL terlebih dahulu.")
