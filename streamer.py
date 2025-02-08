import os
from flask import Flask, send_file, render_template, abort
import mimetypes
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching

# Supported media formats
MEDIA_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.mp3', '.wav']

def get_media_files():
    return [f for f in os.listdir('.') if os.path.splitext(f)[1].lower() in MEDIA_EXTENSIONS]

@app.route('/')
def index():
    return render_template('index.html', media_files=get_media_files())

@app.route('/media/<path:filename>')
def stream_media(filename):
    if not os.path.exists(filename):
        abort(404)
    
    # Use Flask's built-in range request handling
    response = send_file(
        filename,
        mimetype=mimetypes.guess_type(filename)[0],
        conditional=True,
        etag=False
    )
    
    # Set required headers for streaming
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    
    # Create HTML template with better media handling
    with open('templates/index.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Media Streamer</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .media-list { list-style: none; padding: 0; }
        .media-item { margin: 10px 0; }
        .media-link { 
            text-decoration: none; 
            color: #0366d6;
            font-size: 1.2em;
        }
        #mediaPlayer {
            width: 80%;
            max-width: 1000px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Available Media</h1>
    <ul class="media-list">
        {% for media in media_files %}
        <li class="media-item">
            <a href="#" class="media-link" onclick="playMedia('{{ media }}')">{{ media }}</a>
        </li>
        {% endfor %}
    </ul>
    <video id="mediaPlayer" controls></video>

    <script>
        function playMedia(filename) {
            const player = document.getElementById('mediaPlayer');
            const source = document.createElement('source');
            
            // Clear previous sources
            player.innerHTML = '';
            
            source.src = `/media/${encodeURIComponent(filename)}`;
            source.type = getMimeType(filename);
            
            player.appendChild(source);
            player.load();
            
            player.play().catch(error => {
                console.error('Playback failed:', error);
                alert('Error playing media. Ensure file format is supported by your browser.');
            });
        }

        function getMimeType(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            const types = {
                'mp4': 'video/mp4',
                'mov': 'video/quicktime',
                'avi': 'video/x-msvideo',
                'mkv': 'video/x-matroska',
                'webm': 'video/webm',
                'mp3': 'audio/mpeg',
                'wav': 'audio/wav'
            };
            return types[ext] || 'video/mp4';
        }
    </script>
</body>
</html>''')

    # Configure proxy settings
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1
    )
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, threaded=True)

    # ffmpeg -i file.mkv -movflags faststart fiii.mp4