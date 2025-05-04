from flask import Flask, request, Response, abort
import yt_dlp
import tempfile
import os

app = Flask(__name__)

# Cookies string from your data (format: key=value; key2=value2; ...)
cookies_str = (
    "cookie_accept_v2=%7B%22e%22%3A1%2C%22f%22%3A1%2C%22t%22%3A1%2C%22a%22%3A1%7D; "
    "x_content_preference_index=straight; "
    "_cfg=da3b868acca04789d5060fd10ce2772c; "
    "parental-control=no; "
    "_ga=GA1.1.109405817.1745385339; "
    "x_viewes=%5B13383643%2C22427851%5D; "
    "settings=eyJpc1dlYnBTdXBwb3J0ZWQiOnRydWUsImlzV2VibVN1cHBvcnRlZCI6dHJ1ZSwiZXh0RGV0ZWN0ZWRWMiI6ZmFsc2UsIm1vbWVudHNJc0hpZGRlbiI6bnVsbCwiZXhwaXJlcyI6eyJleHREZXRlY3RlZFYyIjoxNzQ1MzgzNTgxfSwidHNTcG90Q291bnRlcnMiOlt7InNwb3QiOiJtYXN0ZXJfZm9vdGVyIiwidGltZSI6MTc0NTM4MzU4MCwiY291bnQiOjV9LHsic3BvdCI6Im1hc3Rlcl9wbGF5ZXJfcGF1c2UiLCJ0aW1lIjoxNzQ1MzgzNTgwLCJjb3VudCI6NX1dfQ%3D%3D; "
    "h_v4_straight=%7B%22v%22%3A%5B%5D%2C%22l%22%3A%5B%5D%2C%22f%22%3A%5B%5D%2C%22pv%22%3A%5B13383643%2C22427851%5D%7D; "
    "_ga_M59JX8S6QE=GS1.1.1745385339.1.1.1745385655.0.0.2115039570"
)

@app.route('/download')
def download_video():
    url = request.args.get('url')
    if not url:
        abort(400, description="Missing 'url' query parameter")

    ydl_opts = {
        'format': 'best',
        'cookiefile': None,
        'http_headers': {
            'Cookie': cookies_str,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        },
        'outtmpl': '%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts['outtmpl'] = f"{tmpdir}/%(id)s.%(ext)s"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            def generate():
                with open(filename, 'rb') as f:
                    while True:
                        chunk = f.read(1024*1024)
                        if not chunk:
                            break
                        yield chunk

            return Response(generate(),
                            content_type='application/octet-stream',
                            headers={"Content-Disposition": f"attachment; filename={os.path.basename(filename)}"})

    except Exception as e:
        abort(400, description=f"Failed to download video: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
