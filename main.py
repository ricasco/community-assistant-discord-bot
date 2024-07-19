from typing import Final
import os
import logging
import discord
from discord.ext import commands
from langchain_community.vectorstores import Qdrant
from langchain_openai.embeddings import OpenAIEmbeddings
import qdrant_client
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from sklearn.metrics.pairwise import cosine_similarity
from langdetect import detect
import asyncio
from functions import handle_roadmap_request, handle_referenced_roadmap_request, filter_ai_sentences, append_campaign, append_how_to_buy, get_crypto_price_info, get_crypto_market_cap, handle_potential_spam, check_user_message_limit, handle_mute_request, handle_unmute_request, handle_tokenomics_request, handle_referenced_tokenomics_request, handle_affiliate_request, handle_referenced_affiliate_request, handle_command_request, handle_price_request, handle_referenced_price_request

# Set environment variables for Qdrant
os.environ['QDRANT_HOST'] = os.getenv("QDRANT_HOST")
os.environ['QDRANT_API_KEY'] = os.getenv("QDRANT_API_KEY")
os.environ['QDRANT_COLLECTION'] = os.getenv("QDRANT_COLLECTION")
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

# Discord bot token
TOKEN: Final = os.getenv("DISCORD_BOT_TOKEN")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Global variable to track if bot is active
bot_active = True

# Create Qdrant client and collection
client = qdrant_client.QdrantClient(os.getenv("QDRANT_HOST"), api_key=os.getenv("QDRANT_API_KEY"))
collection_config = qdrant_client.http.models.VectorParams(size=1536, distance=qdrant_client.http.models.Distance.COSINE)
client.recreate_collection(collection_name=os.getenv("QDRANT_COLLECTION"), vectors_config=collection_config)

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Qdrant(client=client, collection_name=os.getenv("QDRANT_COLLECTION"), embeddings=embeddings)

# Instantiate the ChatOpenAI object with the gpt-4-turbo-preview model
llm = ChatOpenAI(model="gpt-4-turbo-preview")

# Use this llm object when setting up the RetrievalQA
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())

def get_chunks(text):
    separator = "\n\n"
    qna_pairs = text.split(separator)
    chunks = [pair for pair in qna_pairs if pair]
    return chunks

with open("botbuddy.txt") as f:
    raw_text = f.read()
texts = get_chunks(raw_text)
vectorstore.add_texts(texts)

# Set up the Discord bot
intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Define your admin and trigger phrases here
ADMIN_ID = 843933324254773298  # Replace with the actual admin Discord ID
ADMIN_PHRASES = ["I need an admin", "i need admin", "is there any admin" "looking for admin", "looking for support", "I need support", "how can I contact an admin", "looking for an admin"]
DEVELOPER_PHRASES = ["Who needs developer", "Does anyone need developer", "do you need developer", "looking for developer", "do you need a developer"]
AIRDROP_PHRASES = ["Wen airdrop", "When airdrop", "wen IDO", "when IDO", "wen TGE", "when TGE"]
DUMP_PHRASES = ["why dump", "Why the token is dumping"]
PROPOSAL_PHRASES = ["marketing proposal", "listing proposal", "commercial proposal", "partnership proposal", "regarding partnership"]
# Define your admin and selected users' IDs here
EXCLUDED_USER_IDS = {}  # Add User IDs here

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    global bot_active  # Access the global variable

    # Custom mute and unmute handler
    if message.content.startswith('!mute '):  # Checking if the message is a mute command
        await handle_mute_request(message, bot)
        return  # Prevent further processing if it's a mute command

    if message.content.startswith('!unmute '):  # Checking if the message is an unmute command
        await handle_unmute_request(message, bot)
        return  # Prevent further processing if it's an unmute command
      
    # Ensure this line is included to process other commands
    await bot.process_commands(message)

    if message.author == bot.user:
        return

    user_id = message.author.id  # Get the user ID of the message author
    over_limit = check_user_message_limit(user_id)
    if over_limit:
        await message.channel.send("You have reached the maximum number of messages allowed in 24 hours.")
        return  # Stop processing this message

    # Inside your event listener for message
    if message.content.lower() in ["/enable", "/disable"]:
        # Hardcoded ADMIN_ID for testing
        if message.author.id == ADMIN_ID:  # Replace with actual admin ID
            if message.content.lower() == "/enable" and not bot_active:
                bot_active = True
                await message.channel.send("Since now I will start to hear all your messages, take care 👀")
            elif message.content.lower() == "/disable" and bot_active:
                bot_active = False
                await message.channel.send("Since now I will respond only if mentioned.")
        else:
            await message.channel.send("What are you trying to do? 🤌")
        return

    # Check for potential spam in messages
    if message.author.id not in EXCLUDED_USER_IDS:  # Assuming EXCLUDED_USER_IDS is a set of IDs that should not be checked for spam
        if await handle_potential_spam(message, bot):
            logging.info(f"User {message.author} banned for spam.")
            return

    # Check if the message starts with price command for crypto
    user_input_lower = message.content.lower()

    # Add the crypto market cap command handling here
    if message.content.lower().startswith("mcap ") or message.content.lower().startswith("/mcap ") or message.content.lower().startswith("/mc ") or message.content.lower().startswith("mc "):
        _, ticker = message.content.lower().split(maxsplit=1) 
        market_cap_message = get_crypto_market_cap(ticker)
        await message.channel.send(market_cap_message)
        return

    # Check if the message starts with price command for crypto
    if user_input_lower.startswith("price ") or user_input_lower.startswith("prezzo ") or user_input_lower.startswith("chart ") or user_input_lower.startswith("grafico ") or user_input_lower.startswith("/p "):
        _, ticker = user_input_lower.split(maxsplit=1)  # Assumes the command format is "price [ticker]"
        price_info_message = get_crypto_price_info(ticker)
        await message.channel.send(price_info_message)
        return  # Stop further processing

    # Check for roadmap requests
    if await handle_roadmap_request(message, bot):
        return

    # Check for tokenomics requests
    if await handle_tokenomics_request(message, bot):
        return

    # Check for affiliate requests
    if await handle_affiliate_request(message, bot):
        return

    # Check for command requests
    if await handle_command_request(message, bot):
        return

    # Check for price requests
    if await handle_price_request(message, bot):
        return

    # Handle start command
    if "/start" in message.content.lower():
        start_message = "Hello! I'm Leo, the BotBuddy Community Assistant. Ask me whatever you want regarding BotBuddy and the upcoming token $BOT."
        await message.channel.send(start_message)
        return

    # Handle admin request
    if any(phrase.lower() in message.content.lower() for phrase in ADMIN_PHRASES):
        await message.channel.send(f"<@{ADMIN_ID}> someone needs assistance!")
        return

    # Handle developer request
    if any(phrase.lower() in message.content.lower() for phrase in DEVELOPER_PHRASES):
        await message.channel.send(f"You are welcome to send your CV to cv@botbuddy.co. Our team will contact you if there's room for further discussion.")
        return

    # Handle airdrop request
    if any(phrase.lower() in message.content.lower() for phrase in AIRDROP_PHRASES):
        await message.channel.send(f"The TGE and related Airdrop of the $BOT token will happen on Q2. You can find more detailed information by visiting https://botbuddy.gitbook.io/botbuddy-docs/tokenomics-usdbot.")
        return

    # Handle dump request
    if any(phrase.lower() in message.content.lower() for phrase in DUMP_PHRASES):
        await message.channel.send(f"Where were you during the pump? Remember nobody queues for a flat rollercoaster, and if this is not your cup of tea, I can suggest you to start studying the Government Bonds")
        return

    # Handle proposal request
    if any(phrase.lower() in message.content.lower() for phrase in PROPOSAL_PHRASES):
        await message.channel.send(f"For proposals, please email: proposal@botbuddy.co")
        return

    # Ignore messages shorter than 10 characters (place this right after admin checks)
    if len(message.content) < 10:
        logging.info("Ignoring message due to insufficient length.")
        return  # Skip further processing for this message

    try:
        # New logic for handling mentions in replies
        if message.reference and isinstance(message.reference, discord.MessageReference) and bot.user.mentioned_in(message):
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            original_asker = referenced_message.author.mention
            if bot.user.mentioned_in(message):
                if await handle_referenced_roadmap_request(referenced_message, bot, original_asker):
                    return
                if await handle_referenced_tokenomics_request(referenced_message, bot, original_asker):
                  return

                if await handle_referenced_affiliate_request(referenced_message, bot, original_asker):
                  return

                if await handle_referenced_price_request(referenced_message, bot, original_asker):
                  return

        # Check if the bot is mentioned in the message
        if bot.user.mentioned_in(message):
            original_asker = None  # Initialize original_asker here

            # If the message is a reply, fetch the referenced message
            if message.reference and isinstance(message.reference, discord.MessageReference):
                referenced_message = await message.channel.fetch_message(message.reference.message_id)
                text = referenced_message.content
                original_asker = referenced_message.author.mention  # Set the original_asker here
            else:
                text = message.content.replace(bot.user.mention, '').strip()

            response = await handle_query(text)

            # Append the original asker's mention to the response if available
            if original_asker:
                response += f" 📢: {original_asker}"

            await message.channel.send(response)
            return  # Ensure the bot does not proceed to cosine similarity check for these cases
    except Exception as e:
        logging.error(f"Error in on_message: {e}")
        await message.channel.send("Sorry, I didn't understand. Try to ask including more details.")

    # New logic for handling mentions in replies even when the bot is disabled
    if message.reference and isinstance(message.reference, discord.MessageReference):
          referenced_message = await message.channel.fetch_message(message.reference.message_id)
          original_asker = referenced_message.author.mention  # Get the original asker's mention

          if bot.user.mentioned_in(message) or bot.user.mentioned_in(referenced_message):
              response = await handle_query(referenced_message.content)
              if response:
                  response += f"\n\n📢 {original_asker}"  # Append the original asker's mention
                  await message.reply(response)
              return

    # If bot is disabled, only respond to mentions
    if not bot_active:
        if bot.user.mentioned_in(message):
            # Process the message as it mentions the bot
            response = await handle_query(message.content)
            if response:
                await message.reply(response)
        return  # Do not process other messages when bot is disabled

    # Language detection for messages longer than 100 characters
    if len(message.content) > 100:
        try:
            detected_language = detect(message.content)
            if detected_language != 'en':  # Assuming you want to process only English messages
                logging.info(f"Ignoring non-English message: {message.content}")
                return
        except Exception as e:
            logging.error(f"Language detection failed: {e}")
            return

    # Check if the author is an excluded user
    if message.author.id in EXCLUDED_USER_IDS:
        # Check if the bot is mentioned in the message for a response
        if bot.user.mentioned_in(message):
            response = await handle_query(message.content)
            if response:
                await message.reply(response)
        return  # Skip further processing for excluded users

    # Process all other messages to see if they are related to datalake.txt
    response = await handle_query(message.content)
    if response:
        await message.reply(response)

# Define your list of keywords
KEYWORDS = [
    "BotBuddy", "Bot Buddy", "Co-founder", "CEO", "CTO", "Solidity", "Developer", "Advisor", "Web3", "Community Assistant", "Website Widget", "Telegram", "Discord", "tokenomics", "TGE", "$BOT", "Control Panel", "Coingecko", "spam", "security", "multi-language", "bot points", "Airdrop", "Galxe", "cold emailing", "KOL", "campaign", "Centralized Exchanges", "CEX", "blockchain integrations", "AI Software House", "Trading Bot", "DAO", "DeFi", "dApp", "GameFi", "Web2", "SME", "docs", "Medium", "Announcements", "Twitter", "LinkedIn", "email", "roadmap", "DEX", "Affiliate", "Affiliate Program", "AI Widget"
]

# Function to check if any keyword is in the text
def contains_keyword(text):
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

async def handle_query(query):
    # First, check if the query contains any of the defined keywords
    if not contains_keyword(query):
        return None 

    try:
        # Generate embeddings for the query
        query_embedding = embeddings.embed_query(query)

        # Invoke the retriever with the query
        retrieval_results = qa.invoke({
            'input_documents': [],  # Adjust this as needed
            "query": query
        }, return_only_outputs=True)

        # Retrieve the best match document's embedding
        response_text = retrieval_results.get('result', None)
        if response_text:          
            response_embedding = embeddings.embed_query(response_text)

            # Calculate cosine similarity
            similarity = cosine_similarity([query_embedding], [response_embedding])[0][0]

            # Apply the filter to the response text
            filtered_response = filter_ai_sentences(response_text)

            # Append OTC information if relevant
            filtered_response = append_campaign(query, filtered_response)

            # Append how to buy information if relevant
            filtered_response = append_how_to_buy(query, filtered_response)

            # Check if the similarity is above a certain threshold
            if similarity > 0.84:  # Adjust threshold based on testing
                return filtered_response
            else:
                return None  # Skip sending a response when similarity is below the threshold
        else:
            return None  # Skip sending a response when no answer is found
    except Exception as e:
        logging.error(f"Error in handle_query: {e}")
        return None  # Skip sending a response in case of an error

bot.run(TOKEN)