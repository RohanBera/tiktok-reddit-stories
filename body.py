import assemblyai as aai
import multiprocessing
import os
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

aai.settings.api_key = "767469f01f3545739f75c8e7b7a93f01"
num_cores = multiprocessing.cpu_count()


def find_longest_word(word_list):
    longest_word = max(word_list, key=len)
    return longest_word


def generate_subtitles(dir):
    transcriber = aai.Transcriber()

    for title in os.listdir(dir):
        transcript = transcriber.transcribe(f"{dir}/{title}/voice.mp3")
        longest_word = max(transcript.text.split(), key=len)
        print(longest_word)

        if transcript.status == aai.TranscriptStatus.error:
            print(f"[-] {transcript.error}")
        else:
            srt_content = transcript.export_subtitles_srt(
                chars_per_caption=len(longest_word)
            )

            with open(f"{dir}/{title}/captions.srt", "w") as f:
                f.write(srt_content)

            print("[+] Captions generated successfully.")


def add_gif(dir):
    # Function to generate progress bar image at each frame
    def make_progress_bar(duration, width=600, height=900, bar_height=10):
        def make_frame(t):
            progress = t / duration  # Current progress (0 to 1)
            img = np.zeros((bar_height, width, 3), dtype=np.uint8)  # Create black bar
            img[:, : int(progress * width)] = [
                255,
                255,
                255,
            ]  # Fill the bar with white based on progress
            return img

        return VideoClip(make_frame, duration=duration).set_position(
            ("center", height * 0.95)
        )

    # Function to animate the GIF position
    def move_gif(t):
        progress = t / result.duration
        x_position = progress * result.size[0] - gif_clip.size[0] * 0.5
        return (x_position, result.size[1] * 0.95 - gif_clip.size[1])

    for i, title in enumerate(os.listdir(dir)):
        result = VideoFileClip(f"{dir}/{title}/result.mp4")

        progress_bar = make_progress_bar(
            result.duration, width=result.size[0], height=result.size[1], bar_height=1
        )

        # Load the GIF, ensure transparency, and resize it
        gif_clip = (
            VideoFileClip(f"assets/seek_video/gif{(i) % 13}.gif", has_mask=True)
            .loop()
            .set_duration(result.duration)
            .resize(height=100)
        )

        # Set the position of the GIF using the function that calculates its movement
        gif_clip = gif_clip.set_position(move_gif)

        result_with_gif = CompositeVideoClip(
            [result, progress_bar.set_duration(result.duration), gif_clip]
        )

        result_with_gif.write_videofile(
            f"{dir}/{title}/result_with_gif.mp4",
            fps=result.fps,
            threads=num_cores,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            preset="ultrafast",
        )


def generate_video(dir):
    for i, title in enumerate(os.listdir(dir)):

        audio = AudioFileClip(f"{dir}/{title}/voice.mp3")
        audio = audio.subclip(0, -0.15)

        # 14 cuz only 14 videos
        video = (
            VideoFileClip(f"assets/videos/subwaysurfers{(i)%15}.mov")
            .loop()
            .set_duration(audio.duration)
        )
        video = video.without_audio()
        # video = video.subclip(0, audio.duration)

        vid_width, vid_height = video.w, video.h

        generator = lambda txt: TextClip(
            txt,
            font="Helvetica-Bold",
            fontsize=int(vid_width * 0.13),
            stroke_color="black",
            stroke_width=6,
            color="white",
            kerning=-1,
        )
        generator_stroke = lambda txt: TextClip(
            txt,
            font="Helvetica-Bold",
            fontsize=int(vid_width * 0.13),
            color="white",
            kerning=-1,
        )

        subtitles = SubtitlesClip(f"{dir}/{title}/captions.srt", generator)
        subtitles_stroke = SubtitlesClip(
            f"{dir}/{title}/captions.srt", generator_stroke
        )

        watermark = (
            TextClip(
                "@let.it.reddit",
                font="Helvetica-Bold",
                fontsize=int(vid_width * 0.05),
                color="white",
                align="West",
                method="caption",
            )
            .set_duration(audio.duration)
            .set_position((int(vid_width * 0.5), int(vid_height * 0.8)))
            .set_opacity(0.3)
        )

        body_video = CompositeVideoClip(
            [
                video,
                subtitles.set_pos(("center", "center")),
                subtitles_stroke.set_pos(("center", "center")),
                # watermark,
            ]
        )
        body_video = body_video.set_audio(audio)
        title_video = VideoFileClip(f"{dir}/{title}/title.mp4")

        # 9 cuz only 9 songs
        audio = AudioFileClip(f"assets/audios/song{i%9}.mp3")
        audio = audio.volumex(0.2)

        # removing that fuckall noise
        title_video.audio = title_video.audio.subclip(0, -0.7)

        result = concatenate_videoclips([title_video, body_video])
        result_audio = CompositeAudioClip([result.audio, audio])
        result_audio = afx.audio_loop(result_audio, duration=result.duration)
        result.audio = result_audio

        # Load the GIF, ensure transparency, and resize it
        # gif_clip = (
        #     VideoFileClip("assets/seek_video/duck.gif", has_mask=True)
        #     .loop()
        #     .set_duration(result.duration)
        #     .resize(height=100)
        # )

        # # Function to animate the GIF position
        # def move_gif(t):
        #     progress = t / result.duration
        #     x_position = progress * (result.size[0] - gif_clip.size[0])
        #     # 85% from the top, adjust as necessary
        #     return (x_position, result.size[1] * 0.85)

        # # Set the position of the GIF using the function that calculates its movement
        # gif_clip = gif_clip.set_position(move_gif)

        # result_with_gif = CompositeVideoClip([result, gif_clip])

        result.write_videofile(
            f"{dir}/{title}/result.mp4",
            fps=body_video.fps,
            threads=num_cores,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            preset="ultrafast",
        )


# generate_subtitles("stories/english")
# generate_subtitles("stories/hindi")

# generate_video("stories/english")
add_gif("stories/english")
