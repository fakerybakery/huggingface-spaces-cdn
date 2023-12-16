# copyright (c) 2023 mrfakename. all rights reserved.
# https://github.com/fakerybakery/huggingface-spaces-cdn
# 
# 
# this software may be used for personal/non-commercial use only. this software is not open sourced.
# redistribution of this code is allowed, but modification is not. removing this copyright notice and
# license is not allowed.
# 
# the software is provided "as is", without warranty of any kind, express or implied, including but not
# limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors or copyright holders be liable for any claim, damages or other liability,
# whether in an action of contract, tort or otherwise, arising from, out of or in connection with the
# software or the use or other dealings in the software.

from flask import Flask, request, send_file, make_response
import os
import requests
import hashlib
import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from fake_useragent import UserAgent
import tldextract
app = Flask(__name__)

CACHE_FOLDER = 'cache'
MAX_CACHE_SIZE = 25 * 1024 * 1024 * 1024  # 25 GB
MAX_FILE_SIZE = 0.99 * 1024 * 1024 * 1024  # 1 GB
CACHE_EXPIRATION_TIME = timedelta(hours=2)
ua = UserAgent(browsers=['edge', 'chrome', 'safari', 'opera', 'firefox'])


def clean_cache():
    """
    Clean the cache if it exceeds the maximum size.
    """
    total_size = 0
    files = []

    for _, _, filenames in os.walk(CACHE_FOLDER):
        for filename in filenames:
            file_path = os.path.join(CACHE_FOLDER, filename)
            total_size += os.path.getsize(file_path)
            files.append((file_path, os.path.getmtime(file_path)))

    files.sort(key=lambda x: x[1])

    while total_size > MAX_CACHE_SIZE:
        if not files:
            break

        file_to_remove = files.pop(0)
        os.remove(file_to_remove[0])
        total_size -= os.path.getsize(file_to_remove[0])


def download_and_cache_file(url):
    """
    Download the file from the given URL, cache it, and store metadata.
    """
    response = requests.get(url, headers={'User-Agent': ua.random})
    if response.status_code == 200:
        # Use MD5 hash of the URL as the filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        filename = secure_filename(url_hash)
        file_path = os.path.join(CACHE_FOLDER, filename)

        # Save content-type and other headers in metadata file
        metadata = {
            'content-type': response.headers.get('content-type'),
            'headers': dict(response.headers),
        }
        metadata_path = file_path + '.json'
        with open(metadata_path, 'w') as metadata_file:
            json.dump(metadata, metadata_file)

        # Save the file content
        with open(file_path, 'wb') as file:
            file.write(response.content)

        clean_cache()  # Clean the cache after downloading the file
        return file_path, metadata_path
    else:
        print(f"Error, status code {response.status_code}")
        return None


def get_cached_file(url):
    """
    Check if the file is cached and return its path if it is.
    """
    url_hash = hashlib.md5(url.encode()).hexdigest()
    filename = secure_filename(url_hash)
    file_path = os.path.join(CACHE_FOLDER, filename)

    metadata_path = file_path + '.json'
    if os.path.exists(file_path) and os.path.exists(metadata_path):
        modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if datetime.now() - modification_time > CACHE_EXPIRATION_TIME:
            # If the file is older than 2 hours, redownload it
            os.remove(file_path)
            os.remove(metadata_path)
            return download_and_cache_file(url)
        else:
            return file_path, metadata_path
    else:
        return download_and_cache_file(url)
@app.route('/', methods=['GET', 'POST', 'DELETE'])
def proxy():
    if request.method == 'GET':
        url = request.args.get('url')
        if not url:
            return 'Missing "url" parameter in the query string.', 400
    elif request.method == 'DELETE':
        url = request.form.get('url')
        if not url:
            return 'Missing "url" parameter in the query string.', 400
        file_path, metadata_path = get_cached_file(url)
        os.remove(file_path)
        os.remove(metadata_path)
        return 'Cache cleared for URL.', 200
    elif request.method == 'POST':
        # Assuming the URL is sent as a JSON parameter in the request body
        url = request.form.get('url')
        if not url:
            return 'Missing "url" parameter in the request body.', 400
    else:
        return 'Unsupported method', 405
    cached_file, metadata_path = get_cached_file(url)
    if cached_file:
        # Load metadata
        with open(metadata_path, 'r') as metadata_file:
            metadata = json.load(metadata_file)

        return send_file(cached_file, as_attachment=True,
                        mimetype=metadata['content-type'],
                        download_name=f"{secure_filename(url)}.{'.'.join(metadata['content-type'].split('/')[1:])}")
    return 'Failed to retrieve or cache the file.', 500


if __name__ == '__main__':
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)

    app.run(host='0.0.0.0', port=7860)
