from flask import Flask, request, Response, abort
import yt_dlp
import tempfile
import os

app = Flask(__name__)

# Optional: Add cookies here if needed for age-restricted content
cookies_str = (
    "cookie_accept_v2=%7B%22e%22%3A1%2C%22f%22%3A1%2C%22t%22%3A1%2C%22a%22%3A1%7D;"
)

@app.route('/')
def home():
    return '''
    <h2>XHamster Full HD Video Downloader API</h2>
    <p>Usage: <code>/download?url=https://xhamster.com/videos/your-link</code></p>
    <p><b>Credit:</b> Made by @cyber_ansh</p>
    '''

@app.route('/download')
def download_video():
    url = request.args.get('url')
    if not url:
        abort(400, description="❌ Missing 'url' query parameter!")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'outtmpl': '%(id)s.%(ext)s',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0',
            'Cookie': cookies_str
        }
    }

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts['outtmpl'] = os.path.join(tmpdir, '%(id)s.%(ext)s')
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            def generate():
                with open(filename, 'rb') as f:
                    while True:
                        chunk = f.read(1024 * 1024)
                        if not chunk:
                            break
                        yield chunk

            return Response(generate(),
                            content_type='application/octet-stream',
                            headers={
                                "Content-Disposition": f"attachment; filename={os.path.basename(filename)}"
                            })

    except yt_dlp.utils.DownloadError as e:
        abort(400, description=f"❌ Download error: {str(e)}")
    except Exception as e:
        abort(500, description=f"❌ Internal error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
