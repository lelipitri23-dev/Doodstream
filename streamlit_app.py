from flask import Flask, render_template, request, redirect, url_for, flash
import asyncio
import aiohttp
from doodstream import DoodStreamAPI # Mengambil kelas yang sudah kamu buat

app = Flask(__name__)
app.secret_key = "secret_doodoo"

# Fungsi pembantu untuk menjalankan coroutine asinkron di dalam Flask (sync)
def run_async(coro):
    return asyncio.run(coro)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash("Silakan masukkan URL DoodStream!")
            return redirect(url_for('index'))
        
        # Proses mendapatkan link
        try:
            async def get_info():
                async with aiohttp.ClientSession() as session:
                    api = DoodStreamAPI(session)
                    return await api.get_download_url(url)
            
            result = run_async(get_info())
            
            if result:
                download_url, title = result
                return render_template('index.html', title=title, download_url=download_url)
            else:
                flash("Gagal mendapatkan link. Pastikan URL benar.")
        except Exception as e:
            flash(f"Terjadi kesalahan: {str(e)}")
            
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    
