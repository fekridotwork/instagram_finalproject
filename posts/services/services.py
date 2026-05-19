import re

from ..models import Hashtag


HASHTAG_PATTERN = r"#([\w\u0600-\u06FF]+)"


def extract_hashtag_names(text):
    if not text:
        return []

    names = re.findall(HASHTAG_PATTERN, text)
    return list({name.lower() for name in names})


def sync_post_hashtags(post):
    hashtag_names = extract_hashtag_names(post.caption)

    hashtags = [
        Hashtag.objects.get_or_create(name=name)[0]
        for name in hashtag_names
    ]

    post.hashtags.set(hashtags)