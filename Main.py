import json
import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

# Load users from a JSON file
def load_user():
    try:
        with open('user.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        save_user([])  # Initialize the file with an empty list if it doesn't exist
        return []
    except json.JSONDecodeError:
        save_user([])  # Reset the file if it's corrupted
        return []

# Save users to a JSON file
def save_user(users):
    with open('user.json', 'w') as file:
        json.dump(users, file)

# Get a random task from tasks.txt
def get_random_task():
    with open('tasks.txt', 'r') as file:
        tasks = file.readlines()
    return random.choice([task.strip() for task in tasks if task.strip()])  # Ensure no empty tasks

# Enable daily tasks for a user
@bot.message_handler(commands=["enable_tasks"])
def enable_tasks(message):
    users = load_user()
    if message.chat.id not in users:
        users.append(message.chat.id)
        save_user(users)

        # Send a task immediately upon enabling
        immediate_task = get_random_task()
        bot.reply_to(message, f"Daily tasks enabled! Here's your first task:\n\n{immediate_task}")

        bot.reply_to(message, "You will also receive a productivity task every day at 7 AM.")
    else:
        bot.reply_to(message, "You are already enrolled in the daily task program.")

# Disable daily tasks for a user
@bot.message_handler(commands=["disable_tasks"])
def disable_tasks(message):
    users = load_user()
    if message.chat.id in users:
        users.remove(message.chat.id)
        save_user(users)
        bot.reply_to(message, "You have been removed from the daily task reminder.")
    else:
        bot.reply_to(message, "You are not enrolled in the daily task program.")

# Welcome message
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the bot! Type /help to see available commands.")

# Help message
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    Available commands:
    /start - Start the bot and get a welcome message.
    /enable_tasks - Enable daily task reminder.
    /disable_tasks - Disable daily task reminder.
    """
    bot.reply_to(message, help_text)

# Send daily tasks to all enrolled users
def send_daily_tasks():
    users = load_user()
    task = get_random_task()
    for user_id in users:
        try:
            bot.send_message(user_id, f"Good morning! Here's your productivity task for today:\n\n{task}")
        except Exception as e:
            print(f"Failed to send task to {user_id}: {e}")

# Schedule the daily task sending
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_tasks, 'cron', hour=7, minute=0)
scheduler.start()

# Run the bot
bot.polling()
