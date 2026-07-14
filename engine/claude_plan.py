import json
import os

import anthropic

PLAN_TOOL = {
    "name": "submit_edit_plan",
    "description": "Submit the final cut list and subtitle cue list for the video edit.",
    "input_schema": {
        "type": "object",
        "properties": {
            "cuts": {
                "type": "array",
                "description": "Ranges of the SOURCE video (in seconds) to remove.",
                "items": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                        "reason": {"type": "string"},
                    },
                    "required": ["start", "end"],
                },
            },
            "subtitles": {
                "type": "array",
                "description": "Cleaned-up subtitle cues timed against the ORIGINAL (uncut) source video.",
                "items": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                        "text": {"type": "string"},
                    },
                    "required": ["start", "end", "text"],
                },
            },
        },
        "required": ["cuts", "subtitles"],
    },
}

SYSTEM_PROMPT = """You are a professional video editor assistant working on a Korean-language \
talking-head video. You will be given:
- a word-level transcript of the source video with timestamps (seconds from the start),
- a list of acoustically detected silence ranges,
- a free-form editing instruction from the user (in Korean).

Decide the final edit:
1. `cuts`: ranges of the SOURCE video to remove entirely (long silences, filler words like \
"음", "어", "그", stutters/false starts, and anything the user's instruction asks to remove or \
that is clearly off-topic or redundant). Keep natural pauses that aid pacing; do not over-cut. \
Ranges must not overlap and must use SOURCE video timestamps in seconds.
2. `subtitles`: clean, readable subtitle cues covering the KEPT speech, timed against the \
ORIGINAL uncut source video timeline (the XML builder will remap them). Break long sentences \
into short cues (roughly 1-2 lines, under ~20 Korean characters per line). Fix obvious \
transcription errors using context, but do not change the speaker's meaning.

Respond only by calling the submit_edit_plan tool."""


def build_plan(transcript, silences, instruction, log=print):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY 환경변수가 설정되어 있지 않습니다.")

    client = anthropic.Anthropic(api_key=api_key)

    user_content = {
        "instruction": instruction,
        "silences": [{"start": s, "end": e} for s, e in silences],
        "transcript_segments": transcript["segments"],
    }

    log("Claude에게 편집 계획을 요청합니다...")
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[PLAN_TOOL],
        tool_choice={"type": "tool", "name": "submit_edit_plan"},
        messages=[
            {
                "role": "user",
                "content": json.dumps(user_content, ensure_ascii=False),
            }
        ],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "submit_edit_plan":
            plan = block.input
            log(f"편집 계획 수신: 컷 {len(plan.get('cuts', []))}개, 자막 {len(plan.get('subtitles', []))}개.")
            return plan

    raise RuntimeError("Claude 응답에서 편집 계획을 찾지 못했습니다.")
