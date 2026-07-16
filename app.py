import os
import uuid
import textwrap
import subprocess
import requests
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

OUTPUT_DIR = "outputs"
TMP_DIR = "/tmp"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def wrap_text(text, width=28):
    """Wrap long fact text into multiple lines so it fits nicely on a 1080x1920 video."""
    lines = textwrap.wrap(text, width=width)
    return "\n".join(lines)


def escape_for_drawtext(text):
    """Escape characters that break ffmpeg's drawtext filter syntax."""
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\u2019")  # swap apostrophes to avoid quote-escaping issues
        .replace("%", "\\%")
    )


@app.route("/generate-video", methods=["POST"])
def generate_video():
    data = request.get_json(silent=True) or {}
    image_url = data.get("image_url")
    text = data.get("text", "")
    font_color = data.get("font_color", "white")
    duration = int(data.get("duration", 8))

    if not image_url:
        return jsonify({"error": "image_url is required"}), 400
    if not text:
        return jsonify({"error": "text is required"}), 400

    job_id = str(uuid.uuid4())
    image_path = f"{TMP_DIR}/{job_id}.jpg"
    output_filename = f"{job_id}.mp4"
    output_path = f"{OUTPUT_DIR}/{output_filename}"

    try:
        resp = requests.get(image_url, timeout=30)
        resp.raise_for_status()
        with open(image_path, "wb") as f:
            f.write(resp.content)
    except Exception as e:
        return jsonify({"error": f"failed to download image_url: {e}"}), 400

    wrapped = wrap_text(text)
    safe_text = escape_for_drawtext(wrapped)

    drawtext = (
        "drawtext="
        f"text='{safe_text}':"
        f"fontcolor={font_color}:"
        "fontsize=54:"
        "box=1:boxcolor=black@0.55:boxborderw=24:"
        "x=(w-text_w)/2:"
        "y=(h-text_h)/2:"
        "line_spacing=14"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{drawtext}",
        "-t", str(duration),
        "-r", "24",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(image_path):
        os.remove(image_path)

    if result.returncode != 0:
        return jsonify({"error": "ffmpeg failed", "details": result.stderr[-2000:]}), 500

    return jsonify({"download_url": f"/download/{output_filename}"})


@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "not found"}), 404
    return send_file(path, mimetype="video/mp4")


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "facts-trivia-ffmpeg-api"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
