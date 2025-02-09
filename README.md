# Tweyen
Gets Bluesky posts/reposts of a list of users and posts them into Discord webhooks.

# Environment variables

copy `.env.sample` to `.env` and configure them there, or set them in your environment variables.

* `BLUESKY_FOLLOW`: a comma-separated list of Bluesky DIDs.
* `JETSTREAM_URL`: a Jetstream endpoint; by default, we use `jetstream2.us-west.bsky.network`. You can get a list of Jetstream instances [here](https://docs.bsky.app/blog/jetstream).
* `DISCORD_WEBHOOK`: the discord webhook to send posts/reposts to.

# Running
## Development
`dotenv run -- bot`

## Docker
`docker compose up`

# TODO
When restarting the bot, it seems to sometimes repost the same URL. Should probably cache this better.
