from moviepy.editor import *
from PIL import Image, ImageFilter, ImageDraw
import numpy as np
import json


def generate_intro(video, audio, title, file_path):
    # Function to apply blur using PIL
    def apply_blur(frame):
        img = Image.fromarray(frame)
        img = img.filter(ImageFilter.GaussianBlur(radius=15))
        return np.array(img)

    # Function to create a rounded rectangle mask
    def create_rounded_rectangle_mask(size, radius):
        width, height = size
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)
        return np.array(mask) / 255.0

    duration = audio.duration + 0.5

    # Apply the blur to the background video
    video = video.fl_image(apply_blur)

    # few constants
    vid_width, vid_height = video.w, video.h
    box_width, box_height = int(vid_width * 0.8), int(vid_height * 0.25)
    corner_x, corner_y = (vid_width / 2) - (box_width / 2), (vid_height / 2) - (
        box_height / 2
    )
    padding = int(vid_width * 0.025)

    # Create a textbox background
    box = ColorClip(
        size=(box_width, box_height), color=(255, 255, 255), duration=duration
    )
    box = box.set_position("center")

    # Apply the rounded rectangle mask to the ColorClip
    mask = create_rounded_rectangle_mask(
        (box_width, box_height), radius=int(vid_width * 0.05)
    )
    box = box.set_mask(ImageClip(mask, ismask=True))

    # Reddit icon
    reddit_icon = (
        ImageClip("assets/icons/profile_pic.png")
        .set_duration(duration)
        .resize(height=int(vid_height * 0.04))
    )
    reddit_icon = reddit_icon.set_position(
        (corner_x + padding + 10, corner_y + padding + 10)
    )

    # Profile page name
    title_text = (
        TextClip(
            "let.it.reddit",
            font="Helvetica-Bold",
            kerning=2,
            fontsize=int(vid_height * 0.026),
            color="black",
        )
        .set_position(
            (
                corner_x + padding + reddit_icon.size[0] + padding,
                corner_y + int(vid_width * 0.035),
            )
        )
        .set_duration(duration)
    )

    # Verified icon
    verified_icon = (
        ImageClip("assets/icons/verified_icon.png")
        .set_duration(duration)
        .resize(height=int(vid_width * 0.05))
    )
    verified_icon = verified_icon.set_position(
        (
            corner_x
            + padding
            + reddit_icon.size[0]
            + padding
            + title_text.size[0]
            + padding,
            corner_y + int(vid_width * 0.03),
        )
    )

    # Badge icons
    badge_icons = [
        (
            ImageClip(f"assets/icons/badge_{i}.png")
            .set_duration(duration)
            .resize(height=int(vid_width * 0.04))
        )
        for i in range(1, 10)
    ]
    badge_positions = [
        (
            corner_x
            + padding
            + reddit_icon.size[0]
            + padding
            + (i * (badge_icons[0].size[0] + 5)),
            corner_y + int(vid_width * 0.085),
        )
        for i in range(9)
    ]
    badge_clips = [
        badge_icons[i].set_position(pos) for i, pos in enumerate(badge_positions)
    ]

    # Title text
    question_text = (
        TextClip(
            title,
            font="Helvetica-Light",
            fontsize=int(vid_height * 0.026),
            color="black",
            size=(box_width - int(vid_width * 0.07), int(box_height * 0.5)),
            align="West",
            method="caption",
            stroke_color="black",
        )
        .set_position(
            (corner_x + int(vid_width * 0.035), corner_y + int(vid_height * 0.078))
        )
        .set_duration(duration)
    )

    # Heart icon
    heart_icon = (
        ImageClip("assets/icons/heart_icon.png")
        .set_duration(duration)
        .resize(height=int(vid_height * 0.018))
    )
    heart_icon = heart_icon.set_position(
        (
            corner_x + int(vid_width * 0.035),
            corner_y + box_height - int(vid_height * 0.039),
        )
    )

    like_count = (
        TextClip("99+", fontsize=int(vid_height * 0.021), color="black")
        .set_position(
            (
                corner_x + int(vid_width * 0.035) + heart_icon.size[0] + 10,
                corner_y + box_height - int(vid_height * 0.039),
            )
        )
        .set_duration(duration)
    )

    # Comment icon
    comment_count = TextClip(
        "99+", fontsize=int(vid_height * 0.021), color="black"
    ).set_duration(duration)
    comment_count = comment_count.set_position(
        (
            corner_x + box_width - int(vid_width * 0.035) - comment_count.size[0],
            corner_y + box_height - int(vid_height * 0.039),
        )
    )
    comment_icon = (
        ImageClip("assets/icons/comment_icon.png")
        .set_duration(duration)
        .resize(height=int(vid_height * 0.018))
    )
    comment_icon = comment_icon.set_position(
        (
            corner_x
            + box_width
            - int(vid_width * 0.035)
            - comment_count.size[0]
            - comment_icon.size[0]
            - 10,
            corner_y + box_height - int(vid_height * 0.039),
        )
    )

    # Combine all elements
    elements = [
        box,
        reddit_icon,
        verified_icon,
        *badge_clips,
        title_text,
        question_text,
        heart_icon,
        comment_icon,
        like_count,
        comment_count,
    ]

    # removing that glitch at the end of the audio file
    audio = audio.subclip(0, -0.15)

    final_clip = CompositeVideoClip([video] + elements)
    final_clip = final_clip.subclip(0, duration)
    final_clip = final_clip.set_audio(audio)

    # Save the final video
    final_clip.write_videofile(
        f"stories/english/{file_path}/title.mp4",
        fps=video.fps,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
    )


# with open("stories.json") as f:
#     stories = json.load(f)

# for i, story in enumerate(stories):
#     file_path = story["title"].replace(" ", "_")

#     video = VideoFileClip(f"assets/videos/subwaysurfers{i%8}.mov")
#     video = video.without_audio()

#     audio = AudioFileClip(f"stories/english/{file_path}/title.mp3")
#     title = story["title"]

#     generate_intro(video, audio, title, file_path)
