import json
import subprocess


def probe_media(path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)

    video_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    audio_stream = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)

    if video_stream is None:
        raise RuntimeError(f"{path}: 비디오 스트림을 찾지 못했습니다.")

    num, den = (video_stream.get("r_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den) if float(den) != 0 else float(num)

    return {
        "width": int(video_stream.get("width", 1920)),
        "height": int(video_stream.get("height", 1080)),
        "fps": fps,
        "duration": float(data["format"]["duration"]),
        "audio_samplerate": int(audio_stream["sample_rate"]) if audio_stream else 48000,
        "audio_channels": int(audio_stream["channels"]) if audio_stream else 2,
    }
