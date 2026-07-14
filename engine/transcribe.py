from faster_whisper import WhisperModel


def transcribe(path, model_size="medium", language="ko", log=print):
    log(f"Whisper 모델 로드 중 ({model_size})...")
    model = WhisperModel(model_size, device="auto", compute_type="auto")

    log("음성 인식(전사) 진행 중...")
    segments, _info = model.transcribe(
        path,
        language=language,
        word_timestamps=True,
        vad_filter=True,
    )

    words = []
    text_segments = []
    for seg in segments:
        text_segments.append({"start": seg.start, "end": seg.end, "text": seg.text.strip()})
        if seg.words:
            for w in seg.words:
                words.append({"start": w.start, "end": w.end, "word": w.word})

    log(f"전사 완료: 세그먼트 {len(text_segments)}개, 단어 {len(words)}개.")
    return {"segments": text_segments, "words": words}
