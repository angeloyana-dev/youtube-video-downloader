import os, shutil, uuid
from dotenv import load_dotenv
from flask import Flask, request, render_template, url_for, flash, redirect, session, send_file, abort
from pytube import YouTube
from pytube.exceptions import PytubeError
from utils import format_streams, schedule_delete_file
from urllib.parse import quote, unquote
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY').encode()

# Page routes
@app.route('/')
def index():
	return render_template('index.html')

# Video info and available streams page
@app.route('/streams')
def streams():
	video_info = session.pop('video_info', None)
	if video_info:
		audio_streams, thumbnail, title, url, video_streams = video_info.values()
		return render_template('video_info.html',
			url=url,
			title=title,
			thumbnail=thumbnail,
			audio_streams=audio_streams,
			video_streams=video_streams
		)
	else:
		return redirect('/')
	
# Download page
@app.route('/stream')
def stream():
	download_info = session.pop('download_info', None)
	if download_info:
		download_url, thumbnail, title = download_info.values()
		return render_template('download.html',
			download_url=download_url,
			thumbnail=thumbnail,
			title=title
		)
		return download_info
	else:
		return redirect('/')
		
# Download stream to client
@app.route('/download/<string:filename>')
def download_stream(filename):
	filepath = f'assets/{filename}'
	if os.path.exists(filepath):
		original_filename = unquote(request.args.get('original_filename'))
		return send_file(filepath, as_attachment=True, download_name=original_filename)
	else:
		abort(404)
	
# Post routes
# Get video info and streams
@app.post('/get/streams')
def get_streams():
	try:
		url = request.form['url']
		yt = YouTube(url)
		title = yt.title
		thumbnail = yt.thumbnail_url
		audio_streams = format_streams(yt.streams.filter(only_audio=True))
		video_streams = format_streams(yt.streams.filter(progressive=True, file_extension='mp4'))
		session['video_info'] = {
			'url': url,
			'title': title,
			'thumbnail': thumbnail,
			'audio_streams': audio_streams,
			'video_streams': video_streams
		}
		return redirect('/streams')
	except PytubeError as e:
		print(f'Error: {str(e)}')
		flash('Invalid url!', 'error')
		return redirect('/')
	except Exception as e:
		print(f'Error: {str(e)}')
		flash('Internal server error', 'error')
		return redirect('/')
	
# Save stream to server
@app.post('/get/stream')
def get_stream():
	try:
		url = request.args.get('url', None)
		index = int(request.args.get('index', None))
		media_type = request.args.get('mediaType', None)
		yt = YouTube(url)
		title = yt.title
		thumbnail = yt.thumbnail_url
		if media_type == 'video': stream = yt.streams.filter(progressive=True, file_extension='mp4')[index]
		else: stream = yt.streams.filter(only_audio=True)[index]
		file_extension = 'mp4' if media_type == 'video' else 'mp3'
		filename = f"{uuid.uuid4()}.{file_extension}"
		stream.download(output_path='assets', filename=filename)
		schedule_delete_file(f'assets/{filename}')
		session['download_info'] = {
			'title': title,
			'thumbnail': thumbnail,
			'download_url': f"/download/{filename}?original_filename={quote(yt.title + '.' + file_extension)}"
		}
		return redirect('/stream')
	except Exception as e:
		print(f'Error: {str(e)}')
		flash('Internal server error', 'error')
		return redirect('/')
	
if __name__ == '__main__':
	if os.path.exists('assets'):
		shutil.rmtree('assets')
	os.mkdir('assets')
	app.run(host='0.0.0.0')