import logging
import re
import random
import time
from typing import Optional, Tuple
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

class DoodStreamAPI:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    async def get_download_url(self, url: str) -> Optional[Tuple[str, str]]:
        # Otomatis mengubah /d/ menjadi /e/ karena data hanya ada di halaman embed
        embed_url = url.replace('/d/', '/e/').replace('/f/', '/e/')

        try:
            # Mengikuti redirect jika domain berubah (misal ke myvidplay.com)
            async with self.session.get(embed_url, allow_redirects=True) as response:
                response.raise_for_status()
                # Mengambil domain terbaru setelah redirect
                final_url_obj = response.url
                domain = final_url_obj.netloc
                html_content = await response.text()
            
            # Header Referer harus sesuai dengan URL embed terakhir
            self.session.headers.update({"Referer": str(final_url_obj)})

            # Mencari token pass_md5
            pass_md5_match = re.search(r'/pass_md5/([^"\']+)', html_content)
            if not pass_md5_match:
                return None
            
            pass_md5_path = pass_md5_match.group(1)
            # Request ke domain terbaru yang didapat dari redirect
            pass_md5_url = f"https://{domain}/pass_md5/{pass_md5_path}"

            async with self.session.get(pass_md5_url) as md5_response:
                md5_response.raise_for_status()
                media_url_base = await md5_response.text()

            token = pass_md5_path.split('/')[-1]
            random_chars = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=10))
            
            # Membangun link download final
            final_download_link = f"{media_url_base}{random_chars}?token={token}&expiry={int(time.time())}"

            soup = BeautifulSoup(html_content, "html.parser")
            title = soup.find("title").text.strip() if soup.find("title") else "Video"
            title = re.sub(r'[\\/*?:"<>|]', "", title)

            return final_download_link, title
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return None
