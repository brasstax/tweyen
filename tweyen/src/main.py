# main.py
import os
import signal
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


BLUESKY_FOLLOW = os.environ.get("BLUESKY_FOLLOW", None)
if not BLUESKY_FOLLOW:
    raise EnvMissingException(
        "BLUESKY_FOLLOW environment variable must be set to a comma-separated list of DIDs."
    )

JETSTREAM_URL = os.environ.get("JETSTREAM_URL", "jetstream2.us-west.bsky.network")

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", None)
if not DISCORD_WEBHOOK:
    raise EnvMissingException("DISCORD_WEBHOOK environment variable must be set.")


def main():
    killer = GracefulKiller()
    bluesky_follow = BLUESKY_FOLLOW.split(",")
    jetstream_url = f"wss://{JETSTREAM_URL}/subscribe?wantedCollections=app.bsky.feed.post&wantedCollections=app.bsky.feed.repost"
    for entry in bluesky_follow:
        jetstream_url += f"&wantedDids={entry}"
    with connect(jetstream_url) as websocket:
        while not killer.kill_now:
            msg = websocket.recv()
            print(msg)

if __name__ == "__main__":
    main()
