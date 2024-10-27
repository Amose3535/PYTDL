"""PYTDL - Yet another YouTube video downloader made with Python."""

from __future__ import annotations

import importlib.resources as pkg_resources
import logging
import logging.config
import threading
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.error import HTTPError

import customtkinter  # type: ignore[import-untyped]
from moviepy.editor import AudioFileClip, VideoFileClip  # type: ignore[import-untyped]
from pytubefix import YouTube  # type: ignore[import-untyped]

from pytdl import assets

if TYPE_CHECKING:
    from typing import Any

with pkg_resources.as_file(pkg_resources.files(assets)) as assets_dir:
    ASSETS_DIR = assets_dir

TITLE_FONT = customtkinter.CTkFont(family="Arial", size=20, weight="bold")
SUBTITLE_FONT = customtkinter.CTkFont(family="Arial", size=16, weight="normal")
DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads"

class AnsiEscape(str, Enum):
    """Shortcuts for ANSI escape sequences."""

    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    BOLD_RED = '\033[31;1m'


class ColouredFormatter(logging.Formatter):
    """Coloured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        log_level_colours = {
            logging.CRITICAL: AnsiEscape.BOLD_RED,
            logging.ERROR: AnsiEscape.RED,
            logging.WARNING: AnsiEscape.YELLOW,
            logging.INFO: AnsiEscape.GREEN,
            logging.DEBUG: AnsiEscape.CYAN,
        }

        record.msg = f"{log_level_colours.get(record.levelno, AnsiEscape.RESET)}{record.msg}{AnsiEscape.RESET}"
        record.levelname = f"{log_level_colours.get(record.levelno, AnsiEscape.RESET)}{record.levelname:^8}{AnsiEscape.RESET}"

        return super().format(record)


log_config = {
    "version": 1,
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "handlers": {
        "console": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG",
        },
    },
    "formatters": {
        "std_out": {
            "()": "pytdl.main.ColouredFormatter",
            "format": "%(asctime)s [%(levelname)s] %(module)s:L%(lineno)d | %(funcname)s: %(message)s",
            "datefmt": "%d-%m-%Y %I:%M:%S",
        },
    },
}

logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class YTDLApp(customtkinter.CTk):
    """YTDL App."""

    def __init__(self, fg_color: str | tuple[str, str] | None = None, **kwargs) -> None:  # noqa: ANN003
        """Create new app instance."""
        super().__init__(fg_color, **kwargs)
        #print(self.cget("bg")) <<< Used to know that the bgcolor is gray14

        self.geometry("850x520")
        self.minsize(720,520)
        self.maxsize(850,750)
        self.title("PYTDL")  # type: ignore[has-type]
        self.iconbitmap(ASSETS_DIR / "icon.ico")  # Currently bugged

        logger.info("The default download directory is: %s", DEFAULT_DOWNLOAD_DIR)
        self.download_dir = DEFAULT_DOWNLOAD_DIR

        self.title = customtkinter.CTkLabel(self, text="Python YouTube DownLoader", font=TITLE_FONT)
        self.title.pack(padx=10, pady=10)

        self.subtitle = customtkinter.CTkLabel(self, text="Insert a Youtube link:", font=SUBTITLE_FONT)
        self.subtitle.pack(pady=20)

        self.url_var = customtkinter.StringVar()
        self.link_field = customtkinter.CTkEntry(self, width=400, height=40, textvariable=self.url_var, font=SUBTITLE_FONT, placeholder_text="Enter a YouTube link here", placeholder_text_color="white")
        self.url_var.trace_add("write", lambda *_: threading.Thread(target=self.on_url_change).start())
        self.link_field.pack(pady=10)

        #Add dropdown to choose the quality of the video
        self.video_quality_var = customtkinter.StringVar()
        self.video_quality_dropdown = customtkinter.CTkOptionMenu(self, variable=self.video_quality_var, values=["Select video quality"], font=SUBTITLE_FONT)
        self.video_quality_dropdown.set("Select video quality")
        self.video_quality_dropdown.pack(pady=2)
        #Add dropdown to choose the quality of the audio
        self.audio_quality_var = customtkinter.StringVar()
        self.audio_quality_dropdown = customtkinter.CTkOptionMenu(self, variable=self.audio_quality_var, values=["Select audio quality"], font=SUBTITLE_FONT)
        self.audio_quality_dropdown.set("Select audio quality")
        self.audio_quality_dropdown.pack(pady=2)

        #Input field 2
        #Add Subtitle 2
        self.subtitle = customtkinter.CTkLabel(self, text="Insert directory:", font=SUBTITLE_FONT)
        self.subtitle.pack(pady=20)
        #Add Download field
        self.dir_var = customtkinter.StringVar()
        self.dir_field = customtkinter.CTkEntry(self, width=400, height=40, textvariable=self.dir_var, font=SUBTITLE_FONT, placeholder_text="Enter a directory to save the file", placeholder_text_color="white")
        self.dir_field.pack(pady=10)
        self.dir_var.set(DEFAULT_DOWNLOAD_DIR)

        #Progress bar and percentage
        #Add progress bar
        self.percentage_var = customtkinter.StringVar()
        self.progress_bar = customtkinter.CTkProgressBar(self, width=400, height=20, corner_radius=8, border_width=0, progress_color="gray", bg_color="gray14")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        #Add progress percentage text
        self.progress_label = customtkinter.CTkLabel(self, text="0%", font=SUBTITLE_FONT)
        self.progress_label.pack(pady=2)

        #Add buttons
        #Add Download Video Button
        self.download_video_button = customtkinter.CTkButton(self, width=140, height=30, corner_radius=8, border_width=1, text="Download as video", command=lambda: threading.Thread(target=self.start_video_download).start())
        self.download_video_button.pack(pady=2)
        #Add Download Audio Button
        self.download_audio_button = customtkinter.CTkButton(self, width=140, height=30, corner_radius=8, border_width=1, text="Download as audio", command=lambda: threading.Thread(target=self.start_audio_download).start())
        self.download_audio_button.pack(pady=2)

        #Add error feedback text (we make it invisible so it can be later changed)
        self.status_label = customtkinter.CTkLabel(self, text_color="gray14", text="", font=SUBTITLE_FONT)
        self.status_label.pack()

    def on_url_change(self) -> None:
        """Update dropdown menu options on URL change."""
        yt_link = self.url_var.get()
        logger.info("The link is: %s", yt_link)
        #Check if the link is valid
        try:
            yt_object = YouTube(yt_link)
            title = yt_object.title

            video_qualities = []
            audio_qualities = []

            for stream in yt_object.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution'):
                quality = f"{stream.resolution}@{stream.fps}fps"
                logger.info(quality)
                video_qualities.append(quality)

            for stream in yt_object.streams.filter(only_audio=True):
                audio_info = f"{stream.abr} - {stream.audio_codec}"
                logger.info(audio_info)
                audio_qualities.append(audio_info)

            self.video_quality_dropdown.configure(values=video_qualities)
            self.audio_quality_dropdown.configure(values=audio_qualities)

            self.status_label.configure(text=f"Chosen video: {title}", text_color="green")
        except Exception as e:
            logger.exception("An error occurred: ")
            self.status_label.configure(text=f"An error occurred: {e}", text_color="red")


    def start_video_download(self) -> None:
        """Download videos."""
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        try:
            logger.debug("The link is: %s", self.url_var.get())
            dir_path = Path(self.dir_var.get().strip())
            if dir_path.is_dir():
                self.download_dir = dir_path
                self.status_label.configure(text="Download directory set successfully!", text_color="green")
            else:
                self.status_label.configure(text="Invalid directory. Using default download directory instead.", text_color="yellow")
                self.download_dir = DEFAULT_DOWNLOAD_DIR
            logger.debug("The dir is: %s", self.download_dir)

            yt_link = self.url_var.get()
            yt_object = YouTube(yt_link, on_progress_callback=self.on_progress)
            video_stream = yt_object.streams.filter(
                file_extension='mp4',
                only_video=True,
                resolution=self.video_quality_var.get().split("@")[0],
                fps=int(self.video_quality_var.get().split("@")[1].removesuffix("fps")),
            ).first()

            if video_stream is None:
                message = "No video sources found."
                logger.error(message)
                self.status_label.configure(text_color="red", text=message)
                return

            audio_stream = yt_object.streams.filter(
                file_extension='mp4',
                only_audio=True,
                abr=self.audio_quality_var.get().split("-")[0],
            ).first()

            if not audio_stream:
                self.status_label.configure(text="Selected audio quality not available. Using max audio quality instead.", text_color="yellow")
                audio_stream = yt_object.streams.filter(only_audio=True).order_by('abr').last()

            if audio_stream is None:
                message = "No audio sources found."
                logger.error(message)
                self.status_label.configure(text_color="red", text=message)
                return

        except Exception as e:
            logger.exception("An error occurred: ")
            self.status_label.configure(text_color="red", text=f"An error occurred: {e}")
            return

        try:
            self.status_label.configure(text="Downloading Video...", text_color="yellow")
            video_stream.download(output_path=self.download_dir, filename='video.mp4')
        except HTTPError as e:
            error_msg = "An error occurred while downloading the video."
            logger.exception(error_msg)
            self.status_label.configure(text=f"{error_msg}\nError: {e}", text_color="red")
            return
        try:
            self.status_label.configure(text="Downloading Audio...", text_color="yellow")
            audio_stream.download(output_path=self.download_dir, filename='audio.mp4')
        except HTTPError as e:
            error_msg = "An error occurred while downloading the audio."
            logger.exception(error_msg)
            self.status_label.configure(text=f"{error_msg}\nError: {e}", text_color="red")
            return

        try:
            self.status_label.configure(text="Combining video...", text_color="yellow")
            video_clip = VideoFileClip(self.download_dir / 'video.mp4')
        except OSError as e:
            error_msg = "An error occurred while making the video clip."
            logger.exception(error_msg)
            self.status_label.configure(text=f"{error_msg}\nError: {e}", text_color="red")
            return
        try:
            self.status_label.configure(text="Combining audio...", text_color="yellow")
            audio_clip = AudioFileClip(self.download_dir / 'audio.mp4')
        except OSError as e:
            error_msg = "An error occurred while making the audio clip."
            logger.exception(error_msg)
            self.status_label.configure(text=f"{error_msg}\nError: {e}", text_color="red")
            return

        try:
            self.status_label.configure(text="Combining video with audio...", text_color="yellow")
            final_clip = video_clip.set_audio(audio_clip)
        except Exception as e:
            error_msg = "An error occurred while combining the video with audio."
            logger.exception(error_msg)
            self.status_label.configure(text=f"{error_msg}\nError: {e}", text_color="red")
            return
        try:
            self.status_label.configure(text="Writing final video...", text_color="yellow")
            final_clip.write_videofile(self.download_dir / f"{yt_object.title}.mp4")
        except OSError as e:
            error_msg = "An error occurred while writing the final video."
            logger.exception(error_msg)
            self.status_label.configure(text=f"{error_msg}\nError: {e}", text_color="red")
            return

        #Delete the video and audio files
        #Non metto la try/except perchè se non vanno a buon fine non mi interessa
        (self.download_dir / 'video.mp4').unlink()
        (self.download_dir / 'audio.mp4').unlink()

        self.status_label.configure(text="Download completed!", text_color="green")

    def start_audio_download(self) -> None:
        """Download audio."""
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        try:
            logger.info("The link is: %s", self.url_var.get())
            dir_path = Path(self.dir_var.get().strip())
            if dir_path.is_dir():
                self.download_dir = dir_path
                self.status_label.configure(text="Download directory set successfully!", text_color="green")
            else:
                self.status_label.configure(text="Invalid directory. Using default download directory instead.", text_color="yellow")
                self.download_dir = DEFAULT_DOWNLOAD_DIR
            logger.info("The dir is: %s", self.download_dir)

            yt_link = self.url_var.get()
            yt_object = YouTube(yt_link, on_progress_callback=self.on_progress)
            #Use the user selection to download the audio
            audio_stream = yt_object.streams.filter(only_audio=True, abr=self.audio_quality_var.get().split("-")[0]).first()
            self.status_label.configure(text=f"Downloading:\n{yt_object.title}\nIn:{self.download_dir}", text_color="yellow")
            audio_file = audio_stream.download(output_path=self.download_dir)
            if audio_file is None:
                message = "Download failed."
                logger.error(message)
                self.status_label.configure(text_color="red", text=message)
                return

            audio_file = Path(audio_file)

            # Convert to mp3
            audio_file.rename(audio_file.parent / f'{audio_file.stem}.mp3')

            self.status_label.configure(text="Download completed!", text_color="green")
        except Exception as e:
            self.status_label.configure(text_color="red", text=f"An error occurred: {e}")
            logger.exception("An error occurred: ")

    def on_progress(self, stream: Any, _chunk: bytes, bytes_remaining: int) -> None:  # noqa: ANN401
        """Progress callback."""
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = bytes_downloaded / total_size
        self.progress_bar.set(percentage)
        self.progress_label.configure(text=f"{percentage:.2%}")

#Run app
YTDLInstance = YTDLApp()
YTDLInstance.mainloop()
