import streamlit as st
import asyncio
import aiohttp
from doodstream import DoodStreamAPI

st.set_page_config(page_title="Doodozer Downloader", page_icon="🎥")

st.title("🎥 Doodozer Downloader")
st.write("Masukkan link DoodStream (format /d/ atau /e/) di bawah ini.")

async def process_url(url):
    async with aiohttp.ClientSession() as session:
        api = DoodStreamAPI(session)
        return await api.get_download_url(url)

url_input = st.text_input("URL Video:", placeholder="https://dood.li/d/xxxx atau https://myvidplay.com/e/xxxx")

if st.button("Generate Link", type="primary"):
    if url_input:
        with st.spinner("Sedang memproses pengalihan domain..."):
            result = asyncio.run(process_url(url_input))
            if result:
                dl_url, title = result
                st.success(f"Ditemukan: {title}")
                st.link_button("DOWNLOAD SEKARANG", dl_url)
            else:
                st.error("Gagal mengekstrak link. Domain mungkin memblokir akses atau link mati.")
    else:
        st.warning("Masukkan URL terlebih dahulu.")
