import re
import subprocess


def detect_silences(path, noise_db=-30, min_silence=0.4):
    """Run ffmpeg's silencedetect filter and return a list of (start, end) seconds."""
    proc = subprocess.run(
        [
            "ffmpeg",
            "-i", path,
            "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}",
            "-f", "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    log = proc.stderr

    starts = [float(m) for m in re.findall(r"silence_start:\s*([0-9.]+)", log)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([0-9.]+)", log)]

    silences = []
    for i, start in enumerate(starts):
        if i < len(ends):
            silences.append((start, ends[i]))
    return silences
