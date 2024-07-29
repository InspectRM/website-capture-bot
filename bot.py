import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime
import asyncio
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the token from environment variables
token = os.getenv('DISCORD_TOKEN')

if not token:
    raise ValueError("No DISCORD_TOKEN found in environment variables")

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

# Initialize the bot with the command prefix and intents
bot = commands.Bot(command_prefix=',', intents=intents)

class DateView(discord.ui.View):
    @discord.ui.button(label="Show Date", style=discord.ButtonStyle.primary, emoji="📅")
    async def show_date(self, interaction: discord.Interaction, button: discord.ui.Button):
        today_date = datetime.today().strftime('%Y-%m-%d')
        embed = discord.Embed(
            title="📅 Today's Date",
            description=f"**{today_date}**",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Have a great day!")
        await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command(name='date')
async def date(ctx):
    view = DateView()
    await ctx.send("Click the button to see today's date:", view=view)

@bot.command(name='add')
async def add(ctx, *, expression: str):
    try:
        # Evaluate the arithmetic expression
        result = eval(expression)
        embed = discord.Embed(
            title="🧮 Calculation Result",
            description=f"The result of `{expression}` is **{result}**",
            color=discord.Color.green()
        )
        embed.set_footer(text="Calculator Bot")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="⚠️ Error",
            description=f"An error occurred: **{str(e)}**",
            color=discord.Color.red()
        )
        embed.set_footer(text="Calculator Bot")
        await ctx.send(embed=embed)

@bot.command(name='dm')
async def dm(ctx, user: discord.User, *, message: str):
    try:
        loading_message = await ctx.send("Sending DM... ✉️")

        # Simulate loading animation by editing the message
        for i in range(3):
            await asyncio.sleep(0.5)
            await loading_message.edit(content="Sending DM. ✉️")
            await asyncio.sleep(0.5)
            await loading_message.edit(content="Sending DM.. ✉️")
            await asyncio.sleep(0.5)
            await loading_message.edit(content="Sending DM... ✉️")

        # Create an embed message to send as DM
        embed = discord.Embed(
            title="📩 You have a new message!",
            description=f"**{message}**",
            color=discord.Color.purple()
        )
        embed.set_footer(text="Sent via Bad Bot")
        await user.send(embed=embed)

        await loading_message.edit(content=f"Successfully sent a DM to {user.mention}. ✅")
    except Exception as e:
        await loading_message.edit(content=f"Failed to send DM: {str(e)} ❌")

class WebsiteView(View):
    def __init__(self, url, input_fields, button_fields, selected_field=None, selected_button=None):
        super().__init__(timeout=None)
        self.url = url
        self.input_fields = input_fields
        self.button_fields = button_fields
        self.selected_field = selected_field
        self.selected_button = selected_button

    @discord.ui.button(label="Select another field", style=discord.ButtonStyle.primary, emoji="🔄")
    async def select_another_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await select_interaction(interaction.message.channel, self.url, self.input_fields, self.button_fields)

    @discord.ui.button(label="Re-enter text", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def reenter_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await enter_text(interaction.message.channel, self.url, self.selected_field)

    @discord.ui.button(label="Click another button", style=discord.ButtonStyle.success, emoji="🖱️")
    async def click_another_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await select_button(interaction.message.channel, self.url, self.button_fields)

    @discord.ui.button(label="Click button", style=discord.ButtonStyle.danger, emoji="🖱️")
    async def click_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await click_button(interaction.message.channel, self.url, self.selected_button)

async def select_interaction(channel, url, input_fields, button_fields):
    options = "1. Enter text in input field\n2. Click a button\n\nPlease type the number of the action you want to perform:"

    await channel.send(f"Select an action:\n{options}")

    def check(m):
        return m.author != bot.user and m.channel == channel

    user_response = await bot.wait_for('message', check=check)
    try:
        action = int(user_response.content.strip())
        if action == 1:
            await select_input_field(channel, url, input_fields)
        elif action == 2:
            await select_button(channel, url, button_fields)
        else:
            raise ValueError("Invalid selection")
    except (ValueError, IndexError):
        await channel.send("Invalid selection. Please try again.")
        await select_interaction(channel, url, input_fields, button_fields)

async def select_input_field(channel, url, input_fields):
    input_field_options = "\n".join([f"{i + 1}. Type: {field.get_attribute('type')} | Name/ID: {field.get_attribute('name') or field.get_attribute('id') or 'Unnamed'}" for i, field in enumerate(input_fields)])

    await channel.send(f"Found the following input fields:\n{input_field_options}\n\nPlease type the number of the input field you want to interact with:")

    def check(m):
        return m.author != bot.user and m.channel == channel

    user_response = await bot.wait_for('message', check=check)
    try:
        field_index = int(user_response.content.strip()) - 1
        selected_field = input_fields[field_index]
    except (ValueError, IndexError):
        await channel.send("Invalid selection. Please try again.")
        await select_input_field(channel, url, input_fields)
        return

    await enter_text(channel, url, selected_field)

async def enter_text(channel, url, selected_field):
    await channel.send("Please type the text you want to enter in the selected input field:")

    def check(m):
        return m.author != bot.user and m.channel == channel

    user_input = await bot.wait_for('message', check=check)
    input_text = user_input.content.strip()

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-site-isolation-trials')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    field = driver.find_element(By.NAME, selected_field.get_attribute('name') or selected_field.get_attribute('id'))
    field.send_keys(input_text + Keys.RETURN)
    screenshot_path = f"screenshot.png"
    driver.save_screenshot(screenshot_path)
    driver.quit()

    img = Image.open(screenshot_path)
    img.thumbnail((1280, 720))
    img.save(screenshot_path)

    file = discord.File(screenshot_path, filename="screenshot.png")
    embed = discord.Embed(
        title="🌐 Website Screenshot After Interaction",
        description=f"Here is a screenshot of [this website]({url}) after interaction.",
        color=discord.Color.blurple()
    )
    embed.set_image(url="attachment://screenshot.png")
    embed.set_footer(text="Interact with the buttons below")

    await channel.send(file=file, embed=embed, view=WebsiteView(url, [], [], selected_field))
    os.remove(screenshot_path)

async def select_button(channel, url, button_fields):
    button_field_options = "\n".join([f"{i + 1}. Type: {field.get_attribute('type')} | Name/ID: {field.get_attribute('name') or field.get_attribute('id') or 'Unnamed'}" for i, field in enumerate(button_fields)])

    await channel.send(f"Found the following buttons:\n{button_field_options}\n\nPlease type the number of the button you want to interact with:")

    def check(m):
        return m.author != bot.user and m.channel == channel

    user_response = await bot.wait_for('message', check=check)
    try:
        button_index = int(user_response.content.strip()) - 1
        selected_button = button_fields[button_index]
    except (ValueError, IndexError):
        await channel.send("Invalid selection. Please try again.")
        await select_button(channel, url, button_fields)
        return

    await click_button(channel, url, selected_button)

async def click_button(channel, url, selected_button):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-site-isolation-trials')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    button = driver.find_element(By.NAME, selected_button.get_attribute('name') or selected_button.get_attribute('id'))
    button.click()
    screenshot_path = f"screenshot.png"
    driver.save_screenshot(screenshot_path)
    driver.quit()

    img = Image.open(screenshot_path)
    img.thumbnail((1280, 720))
    img.save(screenshot_path)

    file = discord.File(screenshot_path, filename="screenshot.png")
    embed = discord.Embed(
        title="🌐 Website Screenshot After Interaction",
        description=f"Here is a screenshot of [this website]({url}) after interaction.",
        color=discord.Color.blurple()
    )
    embed.set_image(url="attachment://screenshot.png")
    embed.set_footer(text="Interact with the buttons below")

    await channel.send(file=file, embed=embed, view=WebsiteView(url, [], [], selected_button))
    os.remove(screenshot_path)

@bot.command(name='website')
async def website(ctx, url: str):
    loading_message = await ctx.send("Capturing website... 🌐")

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-site-isolation-trials')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        screenshot_path = f"screenshot.png"
        driver.save_screenshot(screenshot_path)

        img = Image.open(screenshot_path)
        img.thumbnail((1280, 720))
        img.save(screenshot_path)

        file = discord.File(screenshot_path, filename="screenshot.png")
        embed = discord.Embed(
            title="🌐 Website Screenshot",
            description=f"Here is a screenshot of [this website]({url}).",
            color=discord.Color.blurple()
        )
        embed.set_image(url="attachment://screenshot.png")
        embed.set_footer(text="Interact with the buttons below")
        await ctx.send(file=file, embed=embed)

        input_fields = driver.find_elements(By.TAG_NAME, 'input')
        button_fields = driver.find_elements(By.TAG_NAME, 'button')

        if not input_fields and not button_fields:
            await loading_message.edit(content="No input fields or buttons found on the page.")
            driver.quit()
            return

        await select_interaction(ctx.channel, url, input_fields, button_fields)
        os.remove(screenshot_path)
    except Exception as e:
        await loading_message.edit(content=f"Failed to capture website: {str(e)} ❌")
        driver.quit()

# Run the bot with the token
bot.run(token)
