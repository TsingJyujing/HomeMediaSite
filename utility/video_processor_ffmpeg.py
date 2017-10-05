from moviepy.editor import VideoFileClip,VideoClip
import math


def get_video_cap(video_file_name):
    return VideoFileClip(video_file_name)


def get_video_basic_info(video_cap):
    """
    :param video_cap: cv2.VideoCapture
    :return: 
    """

    frame_size = video_cap.size
    return {
        "frame_rate": video_cap.fps,
        "size": {
            "width": frame_size[0],
            "height": frame_size[1],
        },
        "time": video_cap.duration
    }


def get_video_preview(video_cap, file_name="out.gif", img_count=15, duration=0.5):
    """
    :param file_name:
    :param video_cap: cv2.VideoCapture
    :param img_count: int
    :param duration:  float
    :return: 
    """

    vc = VideoClip(make_frame=lambda t:video_cap.get_frame(t*video_cap.duration/8),duration=7.5).set_fps(2)
    print(vc.fps)
    vc.to_gif(file_name)


if __name__ == "__main__":
    vcap = get_video_cap("buffer/video_temp_15EE78F076B.mp4")
    print(get_video_basic_info(vcap))
    get_video_preview(vcap, "buffer/out.gif")
