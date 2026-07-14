import os
from xml.sax.saxutils import escape


def rate_info(fps):
    ntsc_rates = {23.976: 24, 29.97: 30, 59.94: 60}
    for ntsc_fps, timebase in ntsc_rates.items():
        if abs(fps - ntsc_fps) < 0.01:
            return timebase, True
    return round(fps), False


def to_frames(seconds, fps):
    return int(round(seconds * fps))


def path_to_file_url(path):
    abs_path = os.path.abspath(path).replace("\\", "/")
    if not abs_path.startswith("/"):
        abs_path = "/" + abs_path
    return f"file://localhost{abs_path}"


def rate_tag(timebase, ntsc, indent="  "):
    return (
        f"{indent}<rate>\n"
        f"{indent}  <timebase>{timebase}</timebase>\n"
        f"{indent}  <ntsc>{'TRUE' if ntsc else 'FALSE'}</ntsc>\n"
        f"{indent}</rate>\n"
    )


def build_fcp7_xml(source_path, keep_segments, media_info, sequence_name="Auto Edit Sequence"):
    fps = media_info["fps"]
    timebase, ntsc = rate_info(fps)
    width = media_info["width"]
    height = media_info["height"]
    samplerate = media_info["audio_samplerate"]
    channels = media_info["audio_channels"]
    source_duration_frames = to_frames(media_info["duration"], fps)
    source_name = escape(os.path.basename(source_path))
    file_url = escape(path_to_file_url(source_path))

    total_frames = 0
    video_clipitems = []
    audio_clipitems = []

    timeline_cursor = 0
    for i, (seg_start, seg_end) in enumerate(keep_segments):
        in_frame = to_frames(seg_start, fps)
        out_frame = to_frames(seg_end, fps)
        clip_len = out_frame - in_frame
        if clip_len <= 0:
            continue
        start_frame = timeline_cursor
        end_frame = timeline_cursor + clip_len
        timeline_cursor = end_frame
        total_frames = end_frame

        clip_id = f"clipitem-v{i + 1}"
        audio_id = f"clipitem-a{i + 1}"

        file_block = (
            f'        <file id="file-1">\n'
            f"          <name>{source_name}</name>\n"
            f"          <pathurl>{file_url}</pathurl>\n"
            f"{rate_tag(timebase, ntsc, '          ')}"
            f"          <duration>{source_duration_frames}</duration>\n"
            f"          <media>\n"
            f"            <video>\n"
            f"              <samplecharacteristics>\n"
            f"                <width>{width}</width>\n"
            f"                <height>{height}</height>\n"
            f"              </samplecharacteristics>\n"
            f"            </video>\n"
            f"            <audio>\n"
            f"              <samplecharacteristics>\n"
            f"                <depth>16</depth>\n"
            f"                <samplerate>{samplerate}</samplerate>\n"
            f"              </samplecharacteristics>\n"
            f"              <channelcount>{channels}</channelcount>\n"
            f"            </audio>\n"
            f"          </media>\n"
            f"        </file>\n"
            if i == 0
            else '        <file id="file-1"/>\n'
        )

        video_clipitems.append(
            f'      <clipitem id="{clip_id}">\n'
            f"        <name>{source_name}</name>\n"
            f"        <duration>{source_duration_frames}</duration>\n"
            f"{rate_tag(timebase, ntsc, '        ')}"
            f"        <start>{start_frame}</start>\n"
            f"        <end>{end_frame}</end>\n"
            f"        <in>{in_frame}</in>\n"
            f"        <out>{out_frame}</out>\n"
            f"{file_block}"
            f"      </clipitem>\n"
        )

        audio_clipitems.append(
            f'      <clipitem id="{audio_id}">\n'
            f"        <name>{source_name}</name>\n"
            f"        <duration>{source_duration_frames}</duration>\n"
            f"{rate_tag(timebase, ntsc, '        ')}"
            f"        <start>{start_frame}</start>\n"
            f"        <end>{end_frame}</end>\n"
            f"        <in>{in_frame}</in>\n"
            f"        <out>{out_frame}</out>\n"
            f'        <file id="file-1"/>\n'
            f"      </clipitem>\n"
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5">
  <sequence>
    <name>{escape(sequence_name)}</name>
    <duration>{total_frames}</duration>
{rate_tag(timebase, ntsc, '    ')}    <media>
      <video>
        <format>
          <samplecharacteristics>
            <width>{width}</width>
            <height>{height}</height>
          </samplecharacteristics>
        </format>
        <track>
{''.join(video_clipitems)}        </track>
      </video>
      <audio>
        <track>
{''.join(audio_clipitems)}        </track>
      </audio>
    </media>
  </sequence>
</xmeml>
"""
    return xml
