import os, time
from threading import Thread

def map_streams(item):
	index, stream = item
	return {
		'index': index,
		'quality': stream.resolution if stream.type == 'video' else stream.abr,
		'filesize': stream.filesize
	}

def delete_file(filepath):
	# Delete the file in 1 hour
	time.sleep(60*60)
	os.remove(filepath)
	
# Main functions	
def format_streams(streams):
	formatted_streams = list(map(map_streams, enumerate(streams)))
	return formatted_streams
	
def schedule_delete_file(filepath):
	thread = Thread(target=lambda: delete_file(filepath))
	thread.start()