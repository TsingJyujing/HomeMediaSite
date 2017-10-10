from config import is_unix

if is_unix:
    from .video_processor_ffmpeg import *
else:
    from .video_processor_opencv import *
