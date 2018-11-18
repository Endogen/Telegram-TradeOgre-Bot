CREATE TABLE user_data (
    user_hash TEXT NOT NULL,
	user_id TEXT NOT NULL PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT,
	username TEXT,
	language TEXT,
	pair TEXT,
	api_key TEXT,
	api_secret TEXT,
	cmc_coin_id TEXT,
	cg_coin_id TEXT,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP
)