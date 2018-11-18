import os
import sqlite3
import tradeogrebot.crypto as crypt


class Database:

    # Initialize database
    def __init__(self, password, db_path="data.db", sql_path="sql"):
        self._db_path = db_path
        self._password = password

        # Create 'data' directory if not present
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        sql = "SELECT name FROM sqlite_master"
        if not cur.execute(sql).fetchone():
            for _, _, files in os.walk(sql_path):
                for file in files:
                    with open(os.path.join(sql_path, file)) as f:
                        cur.execute(f.read())
                        con.commit()

            self.__init_cfg()
            con.close()

        else:
            self.__check_password()

    def __init_cfg(self):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        p = crypt.sha256_hash(self._password)
        sql = "INSERT INTO key_value VALUES (?, ?), (?, ?)"
        cur.execute(sql, ["password_hash", p, "update_hash", None])
        con.commit()
        con.close()

    def __check_password(self):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        sql = "SELECT value FROM key_value WHERE key = 'password_hash'"
        cur.execute(sql)
        con.commit()

        password_hash = cur.fetchone()[0]
        con.close()

        if crypt.sha256_hash(self._password) != password_hash:
            exit("ERROR: Wrong DB password")

    # Check if user is already present in database
    def user_exists(self, user_id):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        sql = "SELECT EXISTS(SELECT 1 FROM user_data WHERE user_hash = ?)"
        cur.execute(sql, [crypt.sha256_hash(user_id)])
        con.commit()

        r = cur.fetchone()
        con.close()

        return True if r[0] == 1 else False

    def add_user(self, user_data):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        id_hash = crypt.sha256_hash(user_data.id)

        p = f"{user_data.id}{self._password}"

        r = crypt.sha256_enc(user_data.first_name, p, p)
        first_name = r["encrypted"] if r else None
        r = crypt.sha256_enc(user_data.last_name, p, p)
        last_name = r["encrypted"] if r else None
        r = crypt.sha256_enc(user_data.language_code, p, p)
        lang = r["encrypted"] if r else None
        r = crypt.sha256_enc(user_data.username, p, p)
        username = r["encrypted"] if r else None
        r = crypt.sha256_enc(user_data.id, p, p)
        user_id = r["encrypted"] if r else None

        sql = "INSERT INTO user_data (user_hash, user_id, first_name, " \
              "last_name, username, language) VALUES (?, ?, ?, ?, ?, ?)"

        cur.execute(sql, [id_hash, user_id, first_name, last_name, username, lang])
        con.commit()
        con.close()

    def remove_user(self, user_id):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        sql = "DELETE FROM user_data WHERE user_hash = ?"
        cur.execute(sql, [crypt.sha256_hash(user_id)])
        con.commit()
        con.close()

    # Read every user data except the datetime that the entry was created
    def get_user_data(self, user_id):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        sql = "SELECT * FROM user_data WHERE user_hash = ?"
        cur.execute(sql, [crypt.sha256_hash(user_id)])
        con.commit()

        r = list(cur.fetchall()[0])
        con.close()

        # Decrypt data
        for i in range(1, len(r)-1):
            p = f"{user_id}{self._password}"
            value = crypt.sha256_dec(r[i], p, p)
            r[i] = value["decrypted"] if value else None

        return UserData(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10])

    def set_pair(self, user_id, pair):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        p = f"{user_id}{self._password}"
        pair = crypt.sha256_enc(pair, p, p)["encrypted"]

        id_hash = crypt.sha256_hash(user_id)

        sql = "UPDATE user_data SET pair = ? WHERE user_hash = ?"
        cur.execute(sql, [pair, id_hash])
        con.commit()
        con.close()

    def set_keys(self, user_id, api_key, api_secret):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        p = f"{user_id}{self._password}"
        api_key = crypt.sha256_enc(api_key, p, p)["encrypted"]
        api_secret = crypt.sha256_enc(api_secret, p, p)["encrypted"]

        id_hash = crypt.sha256_hash(user_id)

        sql = "UPDATE user_data SET api_key = ?, api_secret = ? WHERE user_hash = ?"
        cur.execute(sql, [api_key, api_secret, id_hash])
        con.commit()
        con.close()

    # Save CoinMarketCap coin ID
    def set_cmc_coin_id(self, user_id, coin_id):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        p = f"{user_id}{self._password}"
        coin_id = crypt.sha256_enc(coin_id, p, p)["encrypted"]

        id_hash = crypt.sha256_hash(user_id)

        sql = "UPDATE user_data SET cmc_coin_id = ? WHERE user_hash = ?"
        cur.execute(sql, [coin_id, id_hash])
        con.commit()
        con.close()

    # Save CoinGecko coin ID
    def set_cg_coin_id(self, user_id, coin_id):
        con = sqlite3.connect(self._db_path)
        cur = con.cursor()

        p = f"{user_id}{self._password}"
        coin_id = crypt.sha256_enc(coin_id, p, p)["encrypted"]

        id_hash = crypt.sha256_hash(user_id)

        sql = "UPDATE user_data SET cg_coin_id = ? WHERE user_hash = ?"
        cur.execute(sql, [coin_id, id_hash])
        con.commit()
        con.close()


class UserData:

    def __init__(self,
                 user_hash,
                 user_id,
                 first_name,
                 last_name=None,
                 username=None,
                 language=None,
                 pair=None,
                 api_key=None,
                 api_secret=None,
                 cmc_coin_id=None,
                 cg_coin_id=None):

        self.user_hash = user_hash
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language = language
        self.pair = pair
        self.api_key = api_key
        self.api_secret = api_secret
        self.cmc_coin_id = cmc_coin_id
        self.cg_coin_id = cg_coin_id
