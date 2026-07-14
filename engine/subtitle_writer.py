def format_srt_time(total_seconds):
    total_ms = round(total_seconds * 1000)
    h, rem_ms = divmod(total_ms, 3_600_000)
    m, rem_ms = divmod(rem_ms, 60_000)
    s, ms = divmod(rem_ms, 1000)
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
