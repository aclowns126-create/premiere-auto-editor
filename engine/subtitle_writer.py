def format_srt_time(total_seconds):
    ms = round((total_seconds % 1) * 1000)
    total_ms = int(total_seconds)
    h = total_ms // 3600
    m = (total_ms % 3600) // 60
    s = total_ms % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(cues, out_path):
    lines = []
    for i, cue in enumerate(cues, start=1):
        lines.append(str(i))
        lines.append(f"{format_srt_time(cue['start'])} --> {format_srt_time(cue['end'])}")
        lines.append(cue["text"])
        lines.append("")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
