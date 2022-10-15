import os
import twitter_handler
from dotenv import load_dotenv
from database_handler import DatabaseHandler
from telegram import Update, InputMediaPhoto
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext

async def start(update: Update, context: ContextTypes.context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!"
    )

async def add(update: Update, context: ContextTypes.context):
    if not dbmgr.tg_user_exists(update.effective_chat.id):
        dbmgr.add_tg_user(update.effective_chat.id)
    if len(context.args) != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please enter 1 twitter handle to add."
        )
    else: 
        handle = context.args[0]
        twitter_id = twitter.get_user_id(handle)
        tweets = twitter.get_newest_tweet(twitter_id, count=1)
        if len(tweets) == 1:
            #Add twitter user to db if not exist
            tweet = tweets[0]._json
            last_id = tweet["id_str"]
            dbmgr.add_twitter_user(twitter_id, handle, last_id)
            dbmgr.add_chat_follow(update.effective_chat.id, twitter_id)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Added " + context.args[0] + " to your list."
            )
            

        else:
            await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Cannot add " + context.args[0] + " to your list. User is either protected, has no tweets, or has the bot blocked."
                )

async def remove(update: Update, context: ContextTypes.context):
    if not dbmgr.tg_user_exists(update.effective_chat.id):
        dbmgr.add_tg_user(update.effective_chat.id)
    if len(context.args) != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please enter 1 twitter handle to remove."
        )
    else:
        twtr_id = twitter.get_user_id(context.args[0])
        dbmgr.remove_follow(update.effective_chat.id, twtr_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Subscription removed successfully."
        )
        
async def list(update: Update, context: ContextTypes.context):
    if not dbmgr.tg_user_exists(update.effective_chat.id):
        dbmgr.add_tg_user(update.effective_chat.id)

    follows = dbmgr.get_user_follow_ids(str(update.effective_chat.id))
    follows_formatted = []
    for follow in follows:
        follow_str = follow[0]
        follows_formatted.append(follow_str)
    output_str = "You are following\n" + ("-"*45) + "\n"
    for follow in follows_formatted:
        output_str = output_str + follow + "\n"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=output_str
    )
    dbmgr.list_twitter_users()

async def unknown(update: Update, context: ContextTypes.context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

async def fetch_and_send_data(context: CallbackContext):
    twitter_users = dbmgr.list_twitter_users()
    for twitter_user in twitter_users:
        twitter_id = twitter_user[0]
        twitter_handle = twitter_user[1]
        last_tweet_id = twitter_user[2]

        tweets = twitter.get_newest_tweet(twitter_id, since_id=last_tweet_id)
        if tweets != "-1":
            #tweets = dbmgr.update_twitter_user(twitter_user[0])
            for tweet in reversed(tweets):
                qrt = False
                rt = False
                json = tweet._json
                media_type = ""
                media = ""
                media_error_thrown = False
                try:
                    tweet_extended_entities = json["extended_entities"]
                    media, media_type= twitter.get_media(tweet_extended_entities["media"])
                except KeyError: #No Media
                    media_error_thrown = True
                    pass

                if media_error_thrown:
                    try:
                        tweet_entities = json["entities"]
                        media, media_type= twitter.get_media(tweet_entities["media"])
                    except KeyError:
                        pass

                
                qrt_text = ""
                try:
                    qrt_section = json["quoted_status"]
                    qrt = True
                    qrt_user = qrt_section["user"]
                    qrt_text = "RT from: " + qrt_user["screen_name"] + ": " + qrt_section["full_text"]
                    try:
                        qrt_entities = qrt_section["extended_entities"]
                        qrt_media, qrt_media_type = twitter.get_media(qrt_entities["media"])
                    except KeyError:#No Twitter Media
                        print("No QRT Media")
                except KeyError: #No Quote Retweet
                    print("No Quote Retweet")
                
                rt_section = ""
                rt_text = ""
                rt_media = ""

                if not qrt:
                    try:
                        rt_section = json["retweeted_status"]
                        rt = True
                        rt_user = rt_section["user"]
                        rt_text = "RT from " + rt_user["screen_name"] + ": " + rt_section["full_text"]
                        try:
                            rt_ext_entities = rt_section["extended_entities"]
                            media, media_type = twitter.get_media(rt_ext_entities["media"])

                        except KeyError: #No RT Media
                            print("NO RT MEDIA")
                    except KeyError: #No RT
                        print("No retweet")
                


                output = "New Tweet by {}\n".format(twitter_user[1]) + ("=" * 20) + "\n"
                if rt:
                    output += rt_text
                elif qrt:
                    output += tweet.full_text + "\n" + "="*10 + "Quoted Text" + "="*10 + "\n" + qrt_text
                else:
                    output += tweet.full_text
                media_list = []
                count = 0
                if media_type == "photo":
                    for photo in media:
                        if count == 0:
                            media_list.append(InputMediaPhoto(media=photo, caption=output))
                        else:
                            media_list.append(InputMediaPhoto(media=photo))
                        count += 1
                elif media_type == "video" or media_type == "animated_gif":
                    media_list.append(media[0])
                
                if len(tweets) > 0:
                    last_id = tweets[0].id
                    dbmgr.update_twitter_user(twitter_id, last_id)
                    tg_users = dbmgr.get_users_who_follow_id(twitter_user[0])
                    for tg_user in tg_users: # Send to users
                        if media_type == "photo": #If there's a photo, send as a group 
                            await context.bot.send_media_group(chat_id=tg_user[0], media=media_list)
                        elif media_type == "video" or media_type == "animated_gif": #Send Video
                            await context.bot.send_video(chat_id=tg_user[0], video=media_list[0], caption=output)
                        else: #No media, just text.
                            await context.bot.sendMessage(chat_id=tg_user[0], text=output)
                        if qrt and len(qrt_media) > 0:
                            if qrt_media_type == "photo":
                                qrt_media_list = []
                                count = 0
                                for photo in qrt_media:
                                    if count == 0:
                                        qrt_media_list.append(InputMediaPhoto(media=photo, caption=("Quoted Media")))
                                    else:
                                        qrt_media_list.append(InputMediaPhoto(media=photo))
                                    count += 1
                                await context.bot.send_media_group(chat_id=tg_user[0], media=qrt_media_list)
                            elif qrt_media_type == "video" or qrt_media_type == "animated_gif":
                                await context.bot.send_video(chat_id=tg_user[0], video=qrt_media_list[0], caption="Quoted Media")
                else:
                    pass   

async def credits(update: Update, context: CallbackContext):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Written by Michael Handlin"
        )

if __name__ == '__main__':
    global twitter
    global dbmgr
    load_dotenv()
    interval = 300
    dbmgr = DatabaseHandler("tttgbot_db")
    twitter = twitter_handler.TwitterHandler()
    #application = ApplicationBuilder().token(keys.telegram_token).build()
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    job = application.job_queue
    job.run_once(fetch_and_send_data, 0)
    job.run_repeating(fetch_and_send_data, interval)

    start_handler = CommandHandler('start', start)
    add_handler = CommandHandler('add', add)
    remove_handler = CommandHandler('remove', remove)
    list_handler = CommandHandler('list', list)
    credits_handler = CommandHandler('credits', credits)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    
    application.add_handler(start_handler)
    application.add_handler(add_handler)
    application.add_handler(remove_handler)
    application.add_handler(list_handler)
    application.add_handler(credits_handler)
    application.add_handler(unknown_handler)
    application.run_polling()
