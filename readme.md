
# Discord Bot

A Discord bot that interacts with websites using Selenium and Discord's UI components.

## Features

- Display the current date with a button click.
- Perform arithmetic calculations.
- Send direct messages to users.
- Capture and interact with websites through screenshots.
- Interact with website input fields and buttons dynamically.

## Prerequisites

- Docker
- A Discord bot token (create a bot at the [Discord Developer Portal](https://discord.com/developers/applications))

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/discord-bot.git
cd discord-bot
```

### 2. Create a `.env` File

Create a `.env` file in the root directory of the project and add your Discord bot token:

```env
DISCORD_TOKEN=your-discord-bot-token
```

### 3. Build the Docker Image

Build the Docker image using the following command:

```bash
docker build -t discord-bot .
```

### 4. Run the Docker Container

Run the Docker container with your environment variables and DNS settings:

```bash
docker run -d --name discord-bot --env-file .env --dns 8.8.8.8 --dns 8.8.4.4 -p 4000:80 discord-bot
```

### 5. Interact with the Bot

Invite your bot to a Discord server using the OAuth2 URL generated in the Discord Developer Portal. Once the bot is in your server, you can use the following commands:

- `,date`: Displays the current date.
- `,add <expression>`: Evaluates an arithmetic expression.
- `,dm <user> <message>`: Sends a direct message to a user.
- `,website <url>`: Captures a screenshot of a website and allows interaction with input fields and buttons.

## Example Commands

### Display the Current Date

```bash
,date
```

### Perform Arithmetic Calculation

```bash
,add 2+2*2
```

### Send a Direct Message

```bash
,dm @username Hello, this is a test message!
```

### Capture a Website Screenshot

```bash
,website https://www.example.com
```

![image](https://github.com/user-attachments/assets/14ab2459-e60c-4801-bafb-295b0acc9d5e)


## License

This project is licensed under the MIT License.
