# main.py
import os
import signal
import json
from websockets.sync.client import connect
import requests


class EnvMissingException(Exception):
    pass


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


def parse_repost(uri: str, bluesky_fqdn: str = "bsky.app") -> str:
    """
    Parses an atproto uri from a repost commit action into an actual
    Bluesky URL.

    :param uri: the atproto URI of a repost, ie:
    at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.post/3lg5g64vptc23

    :param bluesky_fqdn: the string of the expected bluesky destination.
    defaults to "bsky.app".
    """

    split_uri = uri.split("/")
    did = split_uri[2]
    post = split_uri[4]
    return f"https://{bluesky_fqdn}/profile/{did}/post/{post}"


BLUESKY_FOLLOW = os.environ.get("BLUESKY_FOLLOW", None)
if not BLUESKY_FOLLOW:
    raise EnvMissingException(
        "BLUESKY_FOLLOW environment variable must be set to a comma-separated list of DIDs."
    )

JETSTREAM_URL = os.environ.get("JETSTREAM_URL", "jetstream2.us-west.bsky.network")

BLUESKY_URL = os.environ.get("BLUESKY_URL", "bsky.app")

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", None)
if not DISCORD_WEBHOOK:
    raise EnvMissingException("DISCORD_WEBHOOK environment variable must be set.")


def main():
    killer = GracefulKiller()
    bluesky_follow = BLUESKY_FOLLOW.split(",")
    jetstream_url = f"wss://{JETSTREAM_URL}/subscribe?wantedCollections=app.bsky.feed.post&wantedCollections=app.bsky.feed.repost"
    for entry in bluesky_follow:
        jetstream_url += f"&wantedDids={entry}"
    print(f"jetstream url: {jetstream_url}")
    with connect(jetstream_url) as websocket:
        print(f"connected to jetstream URL: {jetstream_url}")
        while not killer.kill_now:
            msg = json.loads(websocket.recv())
            if (
                msg["commit"]["operation"] == "create"
                and msg["commit"]["collection"] == "app.bsky.feed.repost"
            ):
                post = parse_repost(
                    msg["commit"]["record"]["subject"]["uri"], BLUESKY_URL
                )
                print(f"repost: {post}")
            if (
                msg["commit"]["operation"] == "create"
                and msg["commit"]["collection"] == "app.bsky.feed.post"
            ):
                post = f'https://{BLUESKY_URL}/profile/{msg["did"]}/post/{msg["commit"]["rkey"]}'
                print(f"post: {post}")
            requests.post(url=DISCORD_WEBHOOK, data={"content": post}, timeout=30)


if __name__ == "__main__":
    main()
