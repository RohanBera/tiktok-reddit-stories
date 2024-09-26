from moviepy.editor import *

# from PIL import Image, ImageFilter, ImageDraw
# import numpy as np
import json

from body import generate_subtitles, generate_video
from tts import tts, speed_up
from title import generate_intro


# GENERATE AUDIO FOR ALL STORIES
print("[+] Generating audio for all stories...")
tts()

print("[+] Speeding up audio for all stories...")
speed_up("stories/english")
# speed_up("stories/hindi")

# GENERATE SUBTITLES FOR ALL STORIES
print("[+] Generating subtitles for all stories...")
generate_subtitles("stories/english")
# generate_subtitles("stories/hindi")

# GENERATE TITLE VIDEO FOR ALL STORIES
print("[+] Generating title for all stories...")

with open("stories.json") as f:
    stories = json.load(f)

for i, story in enumerate(stories):
    file_path = story["title"].replace(" ", "_")

    video = VideoFileClip(f"assets/videos/subwaysurfers{(i)%15}.mov")
    video = video.without_audio()

    audio = AudioFileClip(f"stories/english/{file_path}/title.mp3")
    title = story["title"]

    generate_intro(video, audio, title, file_path)


# GENERATE VIDEO FOR ALL STORIES
# print("[+] Generating video for all stories...")
# generate_video("stories/english")
