import logging
import re
import random
import time
from typing import Optional, Tuple
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

class DoodStreamAPI:
    """Kelas untuk berinteraksi dengan DoodStream API."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    async def get_download_url(self, url: str) -> Optional[Tuple[str, str]]:
        """Mendapatkan direct download URL dan judul video."""
        self.logger.info(f"Memproses URL: {url}")

        # Menangani berbagai format URL (dood.la, doodstream.com, d-s.io, dll)
        # Serta memastikan menggunakan format embed /e/ untuk ekstraksi
        embed_url = url.replace('/d/', '/e/').replace('/f/', '/e/')

        try:
            # Update Headers agar meniru browser asli
            self.session.headers.update({
                "Referer": embed_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            async with self.session.get(embed_url) as response:
                response.raise_for_status()
                html_content = await response.text()
            
            # 1. Cari path pass_md5
            pass_md5_match = re.search(r'/pass_md5/([^"\']+)', html_content)
            if not pass_md5_match:
                self.logger.error("Tidak dapat menemukan 'pass_md5'.")
                return None
            
            pass_md5_path = pass_md5_match.group(1)
            domain = urlparse(embed_url).netloc
            pass_md5_url = f"https://{domain}/pass_md5/{pass_md5_path}"

            # 2. Ambil base URL untuk media
            async with self.session.get(pass_md5_url) as md5_response:
                md5_response.raise_for_status()
                media_url_base = await md5_response.text()

            # 3. Generate karakter acak dan token
            token = pass_md5_path.split('/')[-1]
            random_chars = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=10))

            # URL Akhir untuk download
            final_url = f"{media_url_base}{random_chars}?token={token}&expiry={int(time.time())}"

            # 4. Ambil judul video
            soup = BeautifulSoup(html_content, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.text.strip() if title_tag else "Video_Doodstream"
            
            # Bersihkan karakter terlarang untuk nama file
            title = re.sub(r'[\\/*?:"<>|]', "", title)

            return final_url, title
            
        except Exception as e:
            self.logger.error(f"Error saat memproses DoodStream: {e}")
            return None
