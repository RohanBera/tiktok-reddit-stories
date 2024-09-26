from gtts import gTTS
import json
import os
from deep_translator import GoogleTranslator
from pydub import AudioSegment

with open("stories.json") as f:
    stories = json.load(f)


def tts():
    # create stories dir
    if not os.path.exists("stories"):
        os.mkdir("stories")
    if not os.path.exists("stories/english"):
        os.mkdir("stories/english")
    # if not os.path.exists("stories/hindi"):
    #     os.mkdir("stories/hindi")

    for story in stories:
        title = story["title"].replace(" ", "_")

        if not os.path.exists(f"stories/english/{title}"):
            os.mkdir(f"stories/english/{title}")

        # if not os.path.exists(f"stories/hindi/{title}"):
        #     os.mkdir(f"stories/hindi/{title}")

        # english
        english_story = gTTS(text=story["story"], lang="en")
        english_story.save(f"stories/english/{title}/voice.mp3")

        english_title = gTTS(text=story["long_title"], lang="en")
        english_title.save(f"stories/english/{title}/title.mp3")

        # google trans doenst seem to work
        # hindi_story = translator.translate(story['story'], src='en', dest='hi').text

        # hindi
        # hindi_story = GoogleTranslator(source="en", target="hi").translate(
        #     story["story"]
        # )

        # myobj = gTTS(hindi_story, lang="hi", tld="co.in")
        # myobj.save(f"stories/hindi/{title}/voice.mp3")


def speed_up(dir):
    for title in os.listdir(dir):
        mp3_files = [f for f in os.listdir(f"{dir}/{title}") if f.endswith(".mp3")]
        # for file in os.listdir(f"{dir}/{title}"):
        for file in mp3_files:
            sound = AudioSegment.from_file(f"{dir}/{title}/{file}")
            speed = 1.25

            sound_with_altered_frame_rate = sound._spawn(
                sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed)}
            )

            sped_up_sound = sound_with_altered_frame_rate.set_frame_rate(
                sound.frame_rate
            )
            sped_up_sound.export(f"{dir}/{title}/{file}", format="mp3")


# tts()
# speed_up("stories/english")
# speed_up("stories/hindi")
