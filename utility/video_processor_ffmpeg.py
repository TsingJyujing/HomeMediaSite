import os
from moviepy.editor import VideoFileClip, VideoClip
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
    vc = VideoClip(
        make_frame=lambda t: video_cap.get_frame(t / (img_count * duration)),
        duration=img_count * duration
    )
    vc = vc.set_fps(
        math.ceil(1 / duration)
    )
    vc.write_gif(file_name)


if __name__ == "__main__":

    wrong_file = "D:/File/Downloads/P/4335292_young_japanese_chubby_big_boobs_jk_riko.mp4"
    vcap = get_video_cap(wrong_file)
    print(get_video_basic_info(vcap))
    get_video_preview(vcap, "D:/File/Downloads/P/out.gif")
    vcap.reader.close()


    test_dir = "D:/File/Downloads/P"
    for file in os.listdir(test_dir):
        vcap = get_video_cap(os.path.join(test_dir, file))
        print(get_video_basic_info(vcap))
        get_video_preview(vcap, os.path.join(test_dir, file + ".gif"))
        vcap.reader.close()

