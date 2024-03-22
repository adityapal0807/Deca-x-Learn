from youtube_transcript_api import YouTubeTranscriptApi
import openai
from pytube import YouTube

openai.api_key = ''

# url = 'https://www.youtube.com/watch?v=UCGaKvZpJYc'
# print(url)

def get_video_id(url):
    video_id = url.replace('https://www.youtube.com/watch?v=', '')
    return video_id

def get_video_title(url):
    try:
        youtube_video = YouTube(url)
        video_title = youtube_video.title
        return video_title
    except Exception as e:
        print(f"Error fetching video title: {e}")
        video_title = "Unknown Video Title"


def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # output = ''
        # for x in transcript:
        #     sentence = x['text']
        #     output += f'{sentence}\n'
        # return output
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        transcript = []

# video_id = url.replace('https://www.youtube.com/watch?v=', '')
# print(video_id)

# Fetch video title using pytube


# Generate summary
# response_summary = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a journalist."},
#         {"role": "assistant", "content": "write a 100-word summary of this video"},
#         {"role": "user", "content": output}
#     ]
# )
# summary = response_summary["choices"][0]["message"]["content"]

# # Generate tags
# response_tags = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a journalist."},
#         {"role": "assistant", "content": "output a list of tags for this blog post in a python list such as ['item1', 'item2','item3']"},
#         {"role": "user", "content": output}
#     ]
# )
# tags = response_tags["choices"][0]["message"]["content"]

# print('>>>VIDEO TITLE:')
# print(video_title)
# print('>>>SUMMARY:')
# print(summary)
# print('>>>TAGS:')
# print(tags)
# print('>>>OUTPUT:')