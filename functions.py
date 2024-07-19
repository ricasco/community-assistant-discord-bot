import discord
import logging
import requests
import os
import json
from datetime import datetime, timedelta

# Assuming user_message_limits is a global dictionary to track user limits
user_message_limits = {}

ROADMAP_PHRASES = ["!roadmap", "/roadmap"]
TOKENOMICS_PHRASES = ["!tokenomics", "/tokenomics"]
AFFILIATE_PHRASES = ["!affiliate", "/affiliate"]
COMMAND_PHRASES = ["!help", "/help"]
PRICE_PHRASES = ["!price", "/price"]

# URLs or paths to images
ROADMAP_IMAGE_URL = "ROADMAP.png"   
PRICE_IMAGE_URL = "PRICE.png"

async def handle_roadmap_request(message, bot):
    if bot.user.mentioned_in(message) and any(phrase.lower() in message.content.lower() for phrase in ROADMAP_PHRASES):
        roadmap_response = "🛣 For more information about our roadmap ask detailed questions in the chat to get an answer or visit the related page on our docs https://botbuddy.gitbook.io/botbuddy-docs/roadmap"
        await message.channel.send(roadmap_response)
        await message.channel.send(file=discord.File(ROADMAP_IMAGE_URL))
        return True
    return False

async def handle_price_request(message, bot):
    if bot.user.mentioned_in(message) and any(phrase.lower() in 
    message.content.lower() for phrase in PRICE_PHRASES):
        price_response = "For more information about our Community Assistant and its prices visit the related page on our docs: https://botbuddy.gitbook.io/botbuddy-docs/our-services/telegram-discord-community-assistant"
        await message.channel.send(price_response)
        await message.channel.send(file=discord.File(PRICE_IMAGE_URL))
        return True
    return False

async def handle_tokenomics_request(message, bot):
    if bot.user.mentioned_in(message) and any(phrase.lower() in message.content.lower() for phrase in TOKENOMICS_PHRASES):
        tokenomics_response = "The tokenomics of $BOT has not yet been revealed. You can find some hints and more detailed information by visiting: https://botbuddy.gitbook.io/botbuddy-docs/tokenomics-usdbot."
        await message.channel.send(tokenomics_response)
        return True
    return False

async def handle_affiliate_request(message, bot):
    if bot.user.mentioned_in(message) and any(phrase.lower() in 
    message.content.lower() for phrase in AFFILIATE_PHRASES):
        affiliate_response = "For more information about our Affiliate Program ask detailed questions in the chat to get an answer or visit the related page on our docs https://botbuddy.gitbook.io/botbuddy-docs/affiliate-program-bot-airdrop"
        await message.channel.send(affiliate_response)
        return True
    return False

async def handle_command_request(message, bot):
    if bot.user.mentioned_in(message) and any(phrase.lower() in 
    message.content.lower() for phrase in COMMAND_PHRASES):
        command_response = "🤖 Hello Buddy!\n\n" \
          "Here's the list of commands available:\n" \
          "!price  → to display the prices of the Community Assistant.\n\n" \
          "!tokenomics → to display the link to the tokenomics page of the docs.\n\n" \
          "!affiliate → to display the link to the Affiliate Program page of the docs.\n\n" \
          "!roadmap → to display the roadmap of BotBuddy and the link to the roadmap page of the docs."
        await message.channel.send(command_response)
        return True
    return False

async def handle_referenced_roadmap_request(referenced_message, bot, original_asker):
  if any(phrase.lower() in referenced_message.content.lower() for phrase in ROADMAP_PHRASES):
      roadmap_response = "🛣 For more information about our roadmap ask detailed questions in the chat to get an answer or visit the related page on our docs https://botbuddy.gitbook.io/botbuddy-docs/roadmap"
      if original_asker:
          roadmap_response += f" 📢: {original_asker}"
      await referenced_message.channel.send(roadmap_response)
      await referenced_message.channel.send(file=discord.File(ROADMAP_IMAGE_URL))
      return True
  return False

async def handle_referenced_price_request(referenced_message, bot, original_asker):
  if any(phrase.lower() in referenced_message.content.lower() for phrase in PRICE_PHRASES):
      price_response = "For more information about our Community Assistant and its prices visit the related page on our docs: https://botbuddy.gitbook.io/botbuddy-docs/our-services/telegram-discord-community-assistant"
      if original_asker:
          price_response += f" 📢: {original_asker}"
      await referenced_message.channel.send(price_response)
      await referenced_message.channel.send(file=discord.File(PRICE_IMAGE_URL))
      return True
  return False

async def handle_referenced_tokenomics_request(referenced_message, bot, original_asker):
  if any(phrase.lower() in referenced_message.content.lower() for phrase in TOKENOMICS_PHRASES):
      tokenomics_response = "The tokenomics of $BOT has not yet been revealed. You can find some hints and more detailed information by visiting: https://botbuddy.gitbook.io/botbuddy-docs/tokenomics-usdbot."
      if original_asker:
        tokenomics_response += f" 📢: {original_asker}"
      await referenced_message.channel.send(tokenomics_response)
      return True
  return False

async def handle_referenced_affiliate_request(referenced_message, bot, original_asker):
  if any(phrase.lower() in referenced_message.content.lower() for phrase in AFFILIATE_PHRASES):
      affiliate_response = "For more information about our Affiliate Program ask detailed questions in the chat to get an answer or visit the related page on our docs https://botbuddy.gitbook.io/botbuddy-docs/affiliate-program-bot-airdrop"
      if original_asker:
        affiliate_response += f" 📢: {original_asker}"
      await referenced_message.channel.send(affiliate_response)
      return True
  return False

def filter_ai_sentences(response_text):
    filtered_sentences = []
    for sentence in response_text.split('.'):
        # Check if the sentence starts with 'I am' or 'I'm'
        if not sentence.strip().startswith('I am') and not sentence.strip().startswith("I'm") and not sentence.strip().startswith("I cannot") and not sentence.strip().startswith("My purpose") and not sentence.strip().startswith("It is not specified") and not sentence.strip().startswith("I can't") and not sentence.strip().startswith("It's not specified") and not sentence.strip().startswith("I do not know") and not sentence.strip().startswith("I don't know") and not sentence.strip().startswith("The context") and not sentence.strip().startswith("If you have") and not sentence.strip().startswith("Please provide") and not sentence.strip().startswith("Based on the given context") and not sentence.strip().startswith("Can I") and not sentence.strip().startswith("Can you"):
            filtered_sentences.append(sentence)
    return '.'.join(filtered_sentences).strip()

def append_campaign(query, response):
    campaign_keyword = "points campaign"
    campaign_link = "https://forms.gle/PG3gWvYzjSG2tqHx6"
    additional_text = "Fill this form to participate in the Points Campaign: " + campaign_link

    # Check if 'OTC' is in the user's query
    if campaign_keyword.lower() in query.lower():
        # Check if the link is not in the response
        if campaign_link not in response:
            # Append the additional text to the response
            response += "\n" + additional_text

    return response

def append_how_to_buy(query, response):
    how_to_buy_keywords = [
        "how can I buy BOT",
        "where to purchase BOT",
        "how can I buy $BOT",
        "where can I buy BOT",
        "where can I buy $BOT"        
    ]
    how_to_buy_link = "https://botbuddy.gitbook.io/botbuddy-docs/tokenomics-usdbot"
    additional_text = "Visit https://botbuddy.gitbook.io/botbuddy-docs/tokenomics-usdbot for all the details regarding the BOT token"

    # Convert query to lower case for case-insensitive comparison
    query_lower = query.lower()

    # Check if any of the keywords are in the user's query
    if any(keyword.lower() in query_lower for keyword in how_to_buy_keywords):
        # Check if the link is not in the response
        if how_to_buy_link not in response:
            # Append the additional text to the response
            response += "\n" + additional_text

    return response

def get_crypto_market_cap(ticker):
    coingecko_api_url = os.getenv("COINGECKO_API_URL")

    try:
        coins_list_response = requests.get(f"{coingecko_api_url}/coins/list")
        if coins_list_response.status_code != 200:
            return "Please wait 60 seconds and try again, thank you 🙏"

        coins_list = coins_list_response.json()
        matching_coins = [coin for coin in coins_list if coin['symbol'].lower() == ticker.lower()]

        if not matching_coins:
            return "No data could be found for this specific ticker 🤔"

        max_market_cap = 0
        selected_coin = None
        for coin in matching_coins:
            coin_id = coin['id']
            url = f"{coingecko_api_url}/simple/price?ids={coin_id}&vs_currencies=usd&include_market_cap=true"
            response = requests.get(url)
            data = response.json()

            if coin_id in data and 'usd_market_cap' in data[coin_id]:
                market_cap = data[coin_id]['usd_market_cap']
                if market_cap > max_market_cap:
                    max_market_cap = market_cap
                    selected_coin = coin

        if not selected_coin:
            return "Please wait 60 seconds and try again, thank you 🙏"

        market_cap_formatted = f"${max_market_cap:,.0f}"
        # Assuming real-time or near real-time updates, adjust as needed
        last_updated = "1 minute ago"  

        return f"The market cap of {selected_coin['name']} (${ticker.upper()}) is: {market_cap_formatted} (Last updated: {last_updated})\n\n*Made with 💚 by * [*BotBuddy*](https://botbuddy\.co/)\n---\nData provided by CoinGecko"

    except Exception as e:
        exception_message = "Don't overdo the requests; please give me a minute to breathe 😤"
        return exception_message

def escape_markdown(text):
    # For Discord, you'll want to escape backslashes, asterisks, underscores, and grave accents (different escaping rules compared to Telegram's MarkdownV2)
    return text.replace('\\', '\\\\').replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')

def get_crypto_price_info(ticker):
    coingecko_api_url = os.getenv("COINGECKO_API_URL")

    try:
        coins_list_response = requests.get(f"{coingecko_api_url}/coins/list")
        if coins_list_response.status_code != 200:
            return "Please slow down the requests. Let me breathe for a minute 😤"

        coins_list = coins_list_response.json()
        if not isinstance(coins_list, list):
            return "Unexpected response format from API."

        # Filter all coins matching the ticker
        matching_coins = [coin for coin in coins_list if coin['symbol'].lower() == ticker.lower()]
        if not matching_coins:
            return "No data found for this specific ticker 🤔"

        # Fetch market data for matching coins
        coin_ids = ','.join([coin['id'] for coin in matching_coins])
        markets_response = requests.get(f"{coingecko_api_url}/coins/markets", params={'vs_currency': 'usd', 'ids': coin_ids})
        if markets_response.status_code != 200:
            return "Error fetching market data for matching coins."

        markets_data = markets_response.json()
        if not markets_data:
            return "No market data available for matching coins."

        # Find the coin with the highest market cap
        coin = max(markets_data, key=lambda x: x.get('market_cap', 0))

        # Check for valid coin data
        coin_id = coin['id']
        coin_data_response = requests.get(f"{coingecko_api_url}/coins/{coin_id}")
        if coin_data_response.status_code != 200:
            return "Too many requests in too short a time. Let me breathe for a minute 😤"

        coin_data = coin_data_response.json()
        if not isinstance(coin_data, dict):
            return "Unexpected coin data format."

        # Extracting data...
        if 'market_data' not in coin_data or 'current_price' not in coin_data['market_data']:
            return "Market data not available for " + ticker + "."

        market_data = coin_data['market_data']
        name = coin_data.get('name', 'N/A')
        symbol = ticker.upper()
        price = str(market_data.get('current_price', {}).get('usd', 'N/A'))
        price_change_1h_data = market_data.get('price_change_percentage_1h_in_currency', {}).get('usd', 'N/A')
        price_change_1h = "{:.2f}".format(float(price_change_1h_data)) if price_change_1h_data != 'N/A' else "0.00"
        price_change_24h_data = market_data.get('price_change_percentage_24h_in_currency', {}).get('usd', 'N/A')
        price_change_24h = "{:.2f}".format(float(price_change_24h_data)) if price_change_24h_data != 'N/A' else "0.00"
        price_change_7d_data = market_data.get('price_change_percentage_7d_in_currency', {}).get('usd', 'N/A')
        price_change_7d = "{:.2f}".format(float(price_change_7d_data)) if price_change_7d_data != 'N/A' else "0.00"
        high_24h = str(market_data.get('high_24h', {}).get('usd', 'N/A'))
        low_24h = str(market_data.get('low_24h', {}).get('usd', 'N/A'))
        volume_24h = f"{float(market_data.get('total_volume', {}).get('usd', 0)):,.0f}"
        market_cap = f"{float(market_data.get('market_cap', {}).get('usd', 0)):,.0f}"

        response_message = (
            f"**{escape_markdown(name)} | ${escape_markdown(symbol)}**\n"
            f"💸 Price: ${escape_markdown(price)}\n"
            f"▶️ 1h: {escape_markdown(price_change_1h)}%\n"
            f"▶️ 24h: {escape_markdown(price_change_24h)}%\n"
            f"▶️ 7d: {escape_markdown(price_change_7d)}%\n"
            f"⚖️ 24h High/Low: ${escape_markdown(high_24h)} | ${escape_markdown(low_24h)}\n"
            f"📊 24h Volume: ${escape_markdown(volume_24h)}\n"
            f"💹 Market Cap: ${escape_markdown(market_cap)}\n"
            f"📈 [Chart](https://www.coingecko.com/en/coins/{coin_id})\n\n"
            f"*Made with 💚 by * [*BotBuddy*](https://botbuddy\.co/)\n\-\-\-\n_Data provided by CoinGecko_"
        )

        return response_message
    except Exception as e:
        return "Failed to fetch price info for " + ticker + ": " + str(e)

async def handle_potential_spam(message, client):
    # Load spam keywords from file
    with open("spamkw.json", "r") as file:
        data = json.load(file)
        spam_keywords = data["spam_keywords"]

    user_id = message.author.id
    channel_id = message.channel.id
    text = message.content.lower()

    for keyword in spam_keywords:
        if keyword.lower() in text:
            try:
                # Ban the user from the server
                guild = message.guild
                member = guild.get_member(user_id)
                if member:  # Check if the member is still in the server
                    await guild.ban(member, reason="Spamming")
                    # Delete the message from the channel
                    await message.delete()
                    # Notify the channel
                    await message.channel.send("I've just removed someone for spamming. Stay alert 😈")
                    # Send a private message to the user
                    try:
                        await member.send("If you think you've been banned by mistake from the server, contact the admin @usernameisrich")
                    except discord.HTTPException:
                        # If the user has DMs disabled, this will fail
                        pass
                    return True
            except Exception as e:
                print(f"Failed to ban user or delete message: {e}")
                return False
    return False

def check_user_message_limit(user_id: int) -> bool:
    current_time = datetime.now()
    user_data = user_message_limits.get(user_id)

    if user_data is None or current_time - user_data['first_message_time'] > timedelta(days=1):
        user_message_limits[user_id] = {'count': 1, 'first_message_time': current_time}
        return False

    if user_data['count'] >= 15:  # You can adjust the limit as needed
        return True

    user_data['count'] += 1
    return False

async def handle_mute_request(message, bot):
    try:
        # Logging the request for debugging
        logging.info(f"Handling mute request: {message.content}")

        # Check if the message author has the necessary permissions
        if not message.author.guild_permissions.manage_roles:
            await message.reply("You must have the 'Manage Roles' permission to use this command.")
            return

        # Extracting the mentioned user from the message
        if len(message.mentions) == 0:
            await message.reply("Please mention a user to mute.")
            return
        user_to_mute = message.mentions[0]  # Gets the first mentioned user

        # Check if the bot has permission to manage roles
        if not message.guild.me.guild_permissions.manage_roles:
            await message.reply("I do not have permission to manage roles.")
            return

        # Finding or creating a Muted role
        muted_role = discord.utils.get(message.guild.roles, name="Muted")
        if not muted_role:
            # If there isn't a Muted role, we'll create it
            try:
                muted_role = await message.guild.create_role(name="Muted", reason="Create Muted role for muting members")
                for channel in message.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)
            except Exception as e:
                logging.error(f"Failed to create or set Muted role: {e}")
                await message.reply("Failed to create or set a 'Muted' role. Please check my permissions.")
                return

        # Adding the Muted role to the user
        if muted_role not in user_to_mute.roles:
            await user_to_mute.add_roles(muted_role)
            await message.reply(f"{user_to_mute.mention} has been muted.")
        else:
            await message.reply(f"{user_to_mute.mention} is already muted.")

    except Exception as e:
        logging.error(f"Error in handle_mute_request: {e}")
        await message.reply("An error occurred while processing the mute request.")

async def handle_unmute_request(message, bot):
    try:
        # Logging the request for debugging
        logging.info(f"Handling unmute request: {message.content}")

        # Check if the message author has the necessary permissions
        if not message.author.guild_permissions.manage_roles:
            await message.reply("You must have the 'Manage Roles' permission to use this command.")
            return

        # Extracting the mentioned user from the message
        if len(message.mentions) == 0:
            await message.reply("Please mention a user to unmute.")
            return
        user_to_unmute = message.mentions[0]  # Gets the first mentioned user

        # Check if the bot has permission to manage roles
        if not message.guild.me.guild_permissions.manage_roles:
            await message.reply("I do not have permission to manage roles.")
            return

        # Finding the Muted role
        muted_role = discord.utils.get(message.guild.roles, name="Muted")
        if not muted_role:
            await message.reply("There is no 'Muted' role in this server.")
            return

        # Removing the Muted role from the user
        if muted_role in user_to_unmute.roles:
            await user_to_unmute.remove_roles(muted_role)
            await message.reply(f"{user_to_unmute.mention} has been unmuted.")
        else:
            await message.reply(f"{user_to_unmute.mention} is not muted.")

    except Exception as e:
        logging.error(f"Error in handle_unmute_request: {e}")
        await message.reply("An error occurred while processing the unmute request.")

