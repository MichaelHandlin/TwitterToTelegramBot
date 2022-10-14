from pickle import FALSE
import sqlite3

class DatabaseHandler:
    def __init__(self, dbname) -> None:
        self.db_name = dbname
        self.con = sqlite3.connect(dbname, check_same_thread=False)
        self.cur = self.con.cursor()
        self.create_database()

    def create_database(self):
        #check if tables created
        chat_created = False
        twitter_user_created = False
        chat_follows_created = False

        #Check for Chat Table
        res = self.cur.execute("SELECT name FROM sqlite_master WHERE name='chat'")
        if(res.fetchone() is not None):
            chat_created = True

        #Check for twitter_user table
        res = self.cur.execute("SELECT name FROM sqlite_master WHERE name='twitter_user'")
        if(res.fetchone() is not None):
            twitter_user_created = True

        #Check for chat_follows table
        res = self.cur.execute("SELECT name FROM sqlite_master WHERE name='chat_follows'")
        if(res.fetchone() is not None):
            chat_follows_created = True    

        #If not, create tables
        
        ## chat
        #+ telegram_chat_id: int primary key
        #...

        if not chat_created:
            self.cur.execute('''CREATE TABLE chat(
            telegram_chat_id TEXT PRIMARY KEY);''')

        # twitter_user
        #+ user_id: int primary key
        #+ username?: string (screen_name)
        #+ last_tweet_id: integer

        if not twitter_user_created:
            self.cur.execute('''CREATE TABLE twitter_user(
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                last_tweet_id TEXT);''')

        # chat_follows
        #(optional extra primary key?)
        #+ chat: chat.telegram_chat_id
        #+ twitter_user: twitter_user.user_id

        if not chat_follows_created:
            self.cur.execute('''CREATE TABLE chat_follows(
                follow_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                twitter_user_id TEXT,
                FOREIGN KEY(chat_id) REFERENCES chat(telegram_chat_id),
                FOREIGN KEY(twitter_user_id) REFERENCES twitter_user(user_id));''')
        
    def add_tg_user(self, telegram_chat_id):
        if not self.tg_user_exists(telegram_chat_id):
            sql = "INSERT INTO chat (telegram_chat_id) VALUES (?)"
            res = self.cur.execute(sql, [telegram_chat_id])
            self.con.commit()

    def add_twitter_user(self, user_id, twitter_handle, newest_tweet_id):
        if not self.twitter_user_exists(user_id):        
            sql = "INSERT INTO twitter_user (user_id, username, last_tweet_id) VALUES (?, ?, ?)"
            res = self.cur.execute(sql, [user_id, twitter_handle, newest_tweet_id])
            self.con.commit()

    def add_chat_follow(self, chat_id, twitter_user_id):
        #twitter_user_id = self.th.get_user_id(twitter_handle)
        #check to see if pair exists
        if not self.follow_exists(chat_id, twitter_user_id):
            sql = "INSERT INTO chat_follows (chat_id, twitter_user_id) VALUES (?, ?)"
            res = self.cur.execute(sql, [str(chat_id), str(twitter_user_id)])
            self.con.commit()
        sql = "SELECT * FROM chat_follows WHERE chat_id=(?)"

    def tg_user_exists(self, tg_user_id):
        sql = "SELECT telegram_chat_id FROM chat WHERE telegram_chat_id = (?)"
        res = self.cur.execute(sql, [tg_user_id])
        return res.fetchone() is not None

    def twitter_user_exists(self, twit_user_id):
        sql = "SELECT user_id FROM twitter_user WHERE user_id =(?)"
        res = self.cur.execute(sql, [twit_user_id])
        return res.fetchone() is not None

    def follow_exists(self, tg_user_id, twit_user_id):
        sql = "SELECT chat_id FROM chat_follows WHERE chat_id=(?) AND twitter_user_id=(?)"
        return self.cur.execute(sql, [tg_user_id, twit_user_id]).fetchone() is not None

    def list_tg_users(self):
        sql = "SELECT * FROM chat"
        res = self.cur.execute(sql)

    def list_twitter_users(self):
        sql = "SELECT * FROM twitter_user"
        res = self.cur.execute(sql)
        output_list = []
        for user in res.fetchall():
            output_list.append(user)
        return output_list

    def get_user_follow_ids(self, chat_id):
        sql = "SELECT twitter_user_id FROM chat_follows WHERE chat_id=(?)"
        res = self.cur.execute(sql, [chat_id]).fetchall()
        users = []
        for twitter_user in res:
            sql = "SELECT username FROM twitter_user WHERE user_id=(?)"
            res2 = self.cur.execute(sql, [twitter_user[0]])
            user = res2.fetchone()
            users.append(user)
        return users

    def get_users_who_follow_id(self, twitter_user_id):
        sql = "SELECT chat_id FROM chat_follows WHERE twitter_user_id=(?)"
        res = self.cur.execute(sql, [str(twitter_user_id)])

    def remove_follow(self, tg_user_id, twitter_id):
        sql = "SELECT * FROM chat_follows"
        res = self.cur.execute(sql)
        sql = "DELETE FROM chat_follows WHERE chat_id=(?) AND twitter_user_id=(?);"
        res = self.cur.execute(sql, [tg_user_id, twitter_id])
        self.con.commit()
        sql = "SELECT * FROM chat_follows"
        res = self.cur.execute(sql)

    #Gets the 5 newest tweets from a user, updates the database with the newest one's id, and returns the results of the query.
    def update_twitter_user(self, user_id, latest_tweet_id):
        sql = "UPDATE twitter_user SET last_tweet_id=(?) WHERE user_id=(?)"
        res = self.cur.execute(sql,[latest_tweet_id, user_id])
        self.con.commit()

    def get_twitter_user(self, twitter_id):
        sql = "SELECT * FROM twitter_user WHERE user_id=(?)"
        res = self.cur.execute(sql, [str(twitter_id)])
        return res.fetchone()