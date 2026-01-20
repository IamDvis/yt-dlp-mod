import os
import typer
import typing as t
from pathlib import Path
from yt_dlp_mod.constants import videoQualities, audioQualities, videoExtensions
from yt_dlp_mod import YoutubeDLMod, Downloader
from yt_dlp_mod.models import ExtractedInfo
from enum import Enum

app = typer.Typer(help="Download Youtube videos in a number of formats.")

yt = YoutubeDLMod()

downloader = Downloader(yt)

downloader.default_audio_extension_for_sorting = "webm"
downloader.default_video_extension_for_sorting = "webm"


def get_extracted_info(url: str) -> ExtractedInfo:
    resp = yt.extract_info_and_form_model(url)
    return resp


class VideoQualities(str, Enum):
    P144 = "144p"
    P240 = "240p"
    P360 = "360p"
    P480 = "480p"
    P720 = "720p"
    P1080 = "1080p"
    P1440 = "2k"
    P2160 = "4k"
    P4320 = "8k"
    BEST = "best"


class MediaExtensions(str, Enum):
    WEBM = "webm"
    MP4 = "mp4"
    MP3 = "mp3"
    M4A = "m4a"


class AudioQualities(str, Enum):
    ULTRALOW = "ultralow"
    LOW = "low"
    MEDIUM = "medium"
    BESTAUDIO = "bestaudio"


class AudioBitrates(str, Enum):
    K64 = "64k"
    K96 = "96k"
    K128 = "128k"
    K192 = "192k"
    K256 = "256k"
    K320 = "320k"


@app.command("video")
def download_video(
    url: t.Annotated[str, typer.Argument(help="Link pointing to a Youtube video")],
    quality: t.Annotated[
        t.Optional[VideoQualities],
        typer.Option(help="Video quality to download", show_default=True),
    ] = VideoQualities.BEST,
    dir: t.Annotated[
        t.Optional[Path],
        typer.Option(
            help="Directory to save the video to",
            exists=True,
            writable=True,
            file_okay=False,
        ),
    ] = os.getcwd(),
    format: t.Annotated[
        t.Optional[MediaExtensions],
        typer.Option(help="Video format to process ie. mp4 or webm"),
    ] = MediaExtensions.WEBM,
    quiet: t.Annotated[
        t.Optional[bool],
        typer.Option(
            help="Do not stdout anything",
        ),
    ] = False,
    subtitle_lang: t.Annotated[
        t.Optional[str], typer.Option(help="Subtitle language to embed in the video")
    ] = None,
):
    """Download a youtube video"""
    extracted_info = get_extracted_info(url)
    downloader.default_video_extension_for_sorting = format
    source_audio_ext = "m4a" if format == MediaExtensions.MP4 else "webm"
    qualities_videoFormat = yt.get_video_qualities_with_extension(
        extracted_info, ext=format.value, audio_ext=source_audio_ext
    )
    target_format = qualities_videoFormat.get(
        {"2k": "1440p", "4k": "2160p", "8k": "4320p"}.get(quality.value, quality.value)
    )
    if not (quality == VideoQualities.BEST or target_format):
        # Fallback to the next best quality
        available_qualities = [q for q in videoQualities if q in qualities_videoFormat]
        if available_qualities:
             # Sort available qualities by height (descending) to find the best available
             sorted_available = sorted(available_qualities, key=lambda q: (quality_height_map.get(q, 0)), reverse=True)
             target_format = qualities_videoFormat[sorted_available[0]]
             if not quiet:
                 typer.echo(f"Requested quality {quality.value} not found. Falling back to {sorted_available[0]}.")
        else:
            raise typer.BadParameter(
                f"The video does not support that quality {quality}. No alternative video qualities found for format {format.value}."
            )

    ytdl_params = {
        "quiet": quiet,
        "overwrites": True,
        "outtmpl": dir.joinpath(downloader.default_ydl_output_format).as_posix(),
    }
    if subtitle_lang:
        ytdl_params.update(
            {
                "postprocessors": [
                    {"already_have_subtitle": False, "key": "FFmpegEmbedSubtitle"}
                ],
                "writeautomaticsub": True,
                "writesubtitles": True,
                "subtitleslangs": [subtitle_lang],
            }
        )
    
    # Ensure target_format is set (should be by now)
    if not target_format:
        raise typer.BadParameter("Failed to find a suitable video format for download.")

    medium_format = qualities_videoFormat.get("medium") or qualities_videoFormat.get("low")
    medium_format_id = medium_format.format_id if medium_format else "bestaudio[ext=m4a]/bestaudio"
    
    # Prefer m4a (AAC) audio for MP4 containers to avoid Opus compatibility issues
    if quality == VideoQualities.BEST:
        format_str = "bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
    else:
        format_str = f"{target_format.format_id}+bestaudio[ext=m4a]/{target_format.format_id}+{medium_format_id}/{target_format.format_id}/best"
    
    # Force AAC audio encoding when merging to ensure compatibility
    ytdl_params["postprocessor_args"] = {"merger": ["-c:a", "aac"]}
    download_resp = downloader.ydl_run(
        extracted_info,
        video_format=None,
        audio_format=None,
        default_format=format_str,
        output_ext="mp4",
        ytdl_params=ytdl_params,
    )


@app.command("audio")
def download_audio(
    url: t.Annotated[str, typer.Argument(help="Link pointing to a Youtube video")],
    quality: t.Annotated[
        t.Optional[AudioQualities],
        typer.Option(help="Video quality to download", show_default=True),
    ] = AudioQualities.BESTAUDIO,
    dir: t.Annotated[
        t.Optional[Path],
        typer.Option(
            help="Directory to save the video to",
            exists=True,
            writable=True,
            file_okay=False,
        ),
    ] = os.getcwd(),
    format: t.Annotated[
        t.Optional[MediaExtensions],
        typer.Option(help="Video format to process ie. mp4 or webm"),
    ] = MediaExtensions.WEBM,
    bitrate: t.Annotated[
        t.Optional[AudioBitrates],
        typer.Option(help="Audio bitrate while converting to mp3"),
    ] = None,
    quiet: t.Annotated[
        t.Optional[bool],
        typer.Option(help="Do not stdout anything"),
    ] = False,
):
    """Download audio version of a YouTube video"""
    extracted_info = get_extracted_info(url)
    
    # Check if video has audio
    has_audio = any(f.acodec and f.acodec != "none" for f in extracted_info.formats)
    if not has_audio:
        raise typer.BadParameter("This video does not contain any audio streams (it is silent).")

    # Use webm as source extension for metadata if mp3/m4a is requested for final output
    source_ext = "webm" if format.value not in videoExtensions else format.value
    qualities_videoFormat = yt.get_video_qualities_with_extension(
        extracted_info, ext=source_ext
    )
    target_format = qualities_videoFormat.get(quality.value)
    if quality != AudioQualities.BESTAUDIO:
        assert target_format, (
            f"The video does not support that quality {quality.value}. "
            f"Choose from "
            f"{', '.join([q for q in qualities_videoFormat.keys() if q in audioQualities])}"
        )
    
    format_id = "bestaudio" if quality == AudioQualities.BESTAUDIO else str(target_format.format_id)
    ytdl_params = {
        "quiet": quiet,
        "outtmpl": dir.joinpath(downloader.default_ydl_output_format).as_posix(),
    }
    
    # If format is mp3, ensure conversion happens even if bitrate is not specified
    if format == MediaExtensions.MP3 and not bitrate:
        bitrate = AudioBitrates.K128

    download_resp = downloader.ydl_run_audio(
        extracted_info,
        bitrate=bitrate,
        audio_format=None,
        default_format=format_id,
        ytdl_params=ytdl_params,
    )


if __name__ == "__main__":
    app()
