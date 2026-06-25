# Discord Pollinations Bot

A Discord bot that answers questions using the free Pollinations AI text API. Mention the bot or use `!ask` to get AI-generated responses.

## Run & Operate

- Run the **Discord Bot** workflow in Replit to start the bot
- Required secret: `DISCORD_BOT_TOKEN` — your Discord bot token

## Stack

- Python 3.11
- discord.py
- requests
- Pollinations AI text API (free, no key needed — `https://text.pollinations.ai/`)

## Where things live

- `discord-bot/bot.py` — main bot file (commands, event handlers, Pollinations API calls)

## Architecture decisions

- Bot uses discord.py's `commands.Bot` with `message_content` intent enabled
- Pollinations AI is called synchronously via `requests`, offloaded to a thread executor so it doesn't block the async event loop
- Long AI responses (>2000 chars) are automatically split into Discord-safe chunks
- Bot responds to both `!ask <prompt>` commands and direct @mentions

## Product

- `!ask <question>` — ask the bot anything; it queries Pollinations AI and replies
- @mention the bot with any message to get an AI response

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- `DISCORD_BOT_TOKEN` must be set as a secret before starting the workflow
- The Discord application must have **Message Content Intent** enabled in the Discord Developer Portal (Bot → Privileged Gateway Intents)

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
