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
        self.logger.info(f"Memproses URL: {url}")
        # Mengubah format URL menjadi embed agar bisa diproses
        embed_url = url.replace('/d/', '/e/')

        try:
            self.session.headers.update({"Referer": embed_url})

            async with self.session.get(embed_url) as response:
                response.raise_for_status()
                html_content = await response.text()
            
            # Mencari path pass_md5 dalam konten HTML
            pass_md5_match = re.search(r'/pass_md5/([^"\']+)', html_content)
            if not pass_md5_match:
                return None
            
            pass_md5_path = pass_md5_match.group(1)
            domain = urlparse(embed_url).netloc
            pass_md5_url = f"https://{domain}/pass_md5/{pass_md5_path}"

            async with self.session.get(pass_md5_url) as md5_response:
                md5_response.raise_for_status()
                media_url_base = await md5_response.text()

            token = pass_md5_path.split('/')[-1]
            random_chars = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=10))

            # Membangun URL unduhan akhir
            final_url = f"{media_url_base}{random_chars}?token={token}&expiry={int(time.time())}"

            soup = BeautifulSoup(html_content, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.text.strip() if title_tag else token
            title = re.sub(r'[\\/*?:"<>|]', "", title)

            return final_url, title
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return None
