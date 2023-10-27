function getStream(youtubeVideourl, index, mediaType) {
	const encodedYoutubeVideoUrl = encodeURIComponent(youtubeVideourl)
	const form = document.createElement('form')
	form.method = 'POST'
	form.action = `/get/stream?url=${encodedYoutubeVideoUrl}&index=${index}&mediaType=${mediaType}`
	document.body.append(form)
	form.submit()
}