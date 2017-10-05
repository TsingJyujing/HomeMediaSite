from moviepy.editor import VideoFileClip

import images2gif
import math
from PIL import Image


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
    image_list = list()
    frame_count = int(math.floor(video_cap.duration * video_cap.fps))
    frame_delta = int(math.floor(frame_count / img_count))
    img_index = range(0, frame_count, frame_delta)
    img_index = img_index[:img_count]
    for frame_id in img_index:
        frame = video_cap.get_frame(frame_id/video_cap.fps)
        img = Image.fromarray(frame[:, :, [2, 1, 0]])
        image_list.append(img)

    images2gif.writeGif()
    images2gif.writeGif(
        filename=file_name,
        images=image_list,
        duration=duration,
        repeat=True,
        subRectangles=False
    )


if __name__ == "__main__":
    vcap = get_video_cap("buffer/video_temp_15EE78F076B.mp4")
    print(get_video_basic_info(vcap))
    get_video_preview(vcap, "buffer/out.gif")
