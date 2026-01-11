import logging
import re
import random
import time
from typing import Optional, Tuple
import aiohttp
from bs4 import BeautifulSoup

class DoodStreamAPI:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    async def get_download_url(self, url: str) -> Optional[Tuple[str, str]]:
        # Normalisasi URL
        embed_url = url.replace('/d/', '/e/').replace('/f/', '/e/')

        # Header yang lebih lengkap untuk meniru browser sungguhan
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

        try:
            async with self.session.get(embed_url, headers=headers, allow_redirects=True) as response:
                response.raise_for_status()
                final_url_obj = response.url
                domain = final_url_obj.host
                html_content = await response.text()
            
            # Update Referer secara dinamis
            headers["Referer"] = str(final_url_obj)
            self.session.headers.update(headers)

            # Debug: Cek apakah konten HTML valid (opsional)
            if "pass_md5" not in html_content:
                self.logger.error(f"Konten HTML diterima tetapi 'pass_md5' tidak ditemukan. Panjang karakter: {len(html_content)}")
                # Mencoba regex yang lebih fleksibel
                pass_md5_match = re.search(r'/(pass_md5|pass_md5_extra)/([^"\']+)', html_content)
            else:
                pass_md5_match = re.search(r'/pass_md5/([^"\']+)', html_content)

            if not pass_md5_match:
                return None
            
            pass_md5_path = pass_md5_match.group(1)
            pass_md5_id = pass_md5_match.group(2) if pass_md5_match.lastindex >= 2 else ""
            
            # Membangun URL MD5
            pass_md5_url = f"https://{domain}/{pass_md5_path}/{pass_md5_id}"

            async with self.session.get(pass_md5_url, headers=headers) as md5_response:
                md5_response.raise_for_status()
                media_url_base = await md5_response.text()

            # Logic token dan random string
            token = pass_md5_id.split('/')[-1]
            random_chars = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=10))
            
            final_download_link = f"{media_url_base}{random_chars}?token={token}&expiry={int(time.time())}"

            soup = BeautifulSoup(html_content, "html.parser")
            title = soup.find("title").text.strip() if soup.find("title") else "Video"
            title = re.sub(r'[\\/*?:"<>|]', "", title)

            return final_download_link, title
        except Exception as e:
            self.logger.error(f"Terjadi kesalahan: {e}")
            return None
