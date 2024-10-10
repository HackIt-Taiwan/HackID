import os

class Config:
    MONGO_URI = "mongodb+srv://YuWhisper:xZTh0NAsjZQ35R2U@cs-test-db.3mhjd.mongodb.net/?retryWrites=true&w=majority&appName=CS-Test-DB"
    FERNET_KEY = os.environ.get('FERNET_KEY', 'xVgUnNEvGWFiJ17zKCGwhIVjNMhEeqKKDEvJV3YBU14=')

class TestingConfig(Config):
    TESTING = True
    MONGO_URI = "mongodb+srv://YuWhisper:xZTh0NAsjZQ35R2U@cs-test-db.3mhjd.mongodb.net/cs_test_db?retryWrites=true&w=majority&appName=CS-Test-DB"
    FERNET_KEY = os.environ.get('TESTING_FERNET_KEY', 'SyZqbhFAQsDNg51J7VM1RTUQfI-jrteD0CXU4IHRN_I=')
