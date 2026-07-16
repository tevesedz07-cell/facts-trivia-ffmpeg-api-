# Facts/Trivia FFmpeg API

Simple Flask API na mo-download og image (gikan sa Pexels) ug mo-overlay og custom text
(imong AI-generated fact) gamit ang FFmpeg, dayon mag-output og short vertical (1080x1920) MP4.

## Endpoints

### `POST /generate-video`
Request body (JSON):
```json
{
  "image_url": "https://images.pexels.com/photos/xxxx/photo.jpeg",
  "text": "Honey never spoils! Archaeologists found 3000-year-old edible honey.",
  "font_color": "white",
  "duration": 8
}
```

Response:
```json
{ "download_url": "/download/<job_id>.mp4" }
```

### `GET /download/<filename>`
Download stream sa na-generate nga video (MP4).

### `GET /`
Health check.

## Deploy sa Render (Docker)

1. Himua bag-ong GitHub repo (e.g. `facts-trivia-ffmpeg-api`), i-push kining tanan nga files
   (`app.py`, `requirements.txt`, `Dockerfile`).
2. Sa Render dashboard: **New +** → **Web Service**
3. I-connect ang bag-ong GitHub repo
4. Environment: **Docker** (auto-detect gikan sa Dockerfile)
5. Instance type: Free tier OK ra para sa testing
6. Deploy — kuhaon ang imong live URL (e.g. `https://facts-trivia-ffmpeg-api.onrender.com`)

## Note

- Free tier sa Render mo-spin down after 15 min inactivity — first request pagkahuman
  pwede molangay ug 30-60 seconds (cold start), pareho ra sa imong existing Bible Verse API.
- Kung gusto nimo dugangon ang duration, background music, o multiple font styles,
  pwede ni i-extend sa `app.py`.
