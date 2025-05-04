from flask import Flask, request, Response, abort
import yt_dlp
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h2>XHamster Full HD Video Downloader API</h2>
    <p>Use endpoint <code>/download?url=VIDEO_URL</code> to download.</p>
    <p>Made with ❤️ by <b>@cyber_ansh</b></p>
    '''

@app.route('/download')
def download_video():
    url = request.args.get('url')
    if not url:
        abort(400, description="Missing 'url' query parameter")

    # yt-dlp options
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'outtmpl': '%(id)s.%(ext)s',
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

    except Exception as e:
        abort(400, description=f"Failed to download video: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
