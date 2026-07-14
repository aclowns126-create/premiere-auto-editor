def merge_cuts(cuts, duration):
    ranges = []
    for c in cuts:
        start = max(0.0, min(float(c["start"]), duration))
        end = max(0.0, min(float(c["end"]), duration))
        if end > start:
            ranges.append((start, end))
    ranges.sort()

    merged = []
    for start, end in ranges:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def compute_keep_segments(merged_cuts, duration, min_segment=0.05):
    segments = []
    cursor = 0.0
    for start, end in merged_cuts:
        if start - cursor > min_segment:
            segments.append((cursor, start))
        cursor = max(cursor, end)
    if duration - cursor > min_segment:
        segments.append((cursor, duration))
    return segments


def map_range_through_keep_segments(orig_start, orig_end, keep_segments):
    """Map a [orig_start, orig_end) source-time range onto the new (post-cut) timeline.

    Returns a list of (new_start, new_end) pieces, one per keep-segment overlap.
    """
    pieces = []
    timeline_cursor = 0.0
    for seg_start, seg_end in keep_segments:
        seg_len = seg_end - seg_start
        overlap_start = max(orig_start, seg_start)
        overlap_end = min(orig_end, seg_end)
        if overlap_end > overlap_start:
            new_start = timeline_cursor + (overlap_start - seg_start)
            new_end = timeline_cursor + (overlap_end - seg_start)
            pieces.append((new_start, new_end))
        timeline_cursor += seg_len
    return pieces


def remap_subtitles(subtitles, keep_segments):
    remapped = []
    for cue in subtitles:
        pieces = map_range_through_keep_segments(cue["start"], cue["end"], keep_segments)
        if not pieces:
            continue
        best = max(pieces, key=lambda p: p[1] - p[0])
        if best[1] - best[0] < 0.15:
            continue
        remapped.append({"start": best[0], "end": best[1], "text": cue["text"]})
    return remapped
