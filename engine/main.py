import argparse
import json
import os
import sys

from dotenv import load_dotenv

from probe import probe_media
from silence import detect_silences
from transcribe import transcribe
from claude_plan import build_plan
from segments import merge_cuts, compute_keep_segments, remap_subtitles
from xml_writer import build_fcp7_xml
from subtitle_writer import write_srt


def log(message):
    print(message, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--instruction", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--whisper-model", default="medium")
    parser.add_argument("--language", default="ko")
    args = parser.parse_args()

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "server", ".env"))

    os.makedirs(args.out, exist_ok=True)

    log(f"영상 정보 분석 중: {args.video}")
    media_info = probe_media(args.video)
    log(f"영상 정보: {media_info['width']}x{media_info['height']} @ {media_info['fps']:.2f}fps, {media_info['duration']:.1f}초")

    log("무음 구간 탐지 중...")
    silences = detect_silences(args.video)
    log(f"무음 구간 {len(silences)}개 발견.")

    transcript = transcribe(args.video, model_size=args.whisper_model, language=args.language, log=log)

    plan = build_plan(transcript, silences, args.instruction, log=log)

    merged_cuts = merge_cuts(plan.get("cuts", []), media_info["duration"])
    keep_segments = compute_keep_segments(merged_cuts, media_info["duration"])
    log(f"최종 유지 구간 {len(keep_segments)}개 (원본 {media_info['duration']:.1f}초 -> 편집본 "
        f"{sum(e - s for s, e in keep_segments):.1f}초)")

    remapped_subtitles = remap_subtitles(plan.get("subtitles", []), keep_segments)

    xml_content = build_fcp7_xml(args.video, keep_segments, media_info)
    xml_path = os.path.join(args.out, "sequence.xml")
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    log(f"시퀀스 XML 저장: {xml_path}")

    srt_path = os.path.join(args.out, "subtitles.srt")
    write_srt(remapped_subtitles, srt_path)
    log(f"자막 SRT 저장: {srt_path}")

    result = {
        "xmlPath": os.path.abspath(xml_path),
        "srtPath": os.path.abspath(srt_path),
        "cutCount": len(merged_cuts),
        "keepSegmentCount": len(keep_segments),
        "subtitleCount": len(remapped_subtitles),
    }
    print("RESULT:" + json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # surface a clean error line for the Node server to relay
        print(f"ERROR:{exc}", flush=True)
        sys.exit(1)
