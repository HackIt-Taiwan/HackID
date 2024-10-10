class Config:
    MONGO_URI = "mongodb+srv://YuWhisper:xZTh0NAsjZQ35R2U@cs-test-db.3mhjd.mongodb.net/?retryWrites=true&w=majority&appName=CS-Test-DB"

class TestingConfig(Config):
    TESTING = True
    MONGO_URI = "mongodb+srv://YuWhisper:xZTh0NAsjZQ35R2U@cs-test-db.3mhjd.mongodb.net/cs_test_db?retryWrites=true&w=majority&appName=CS-Test-DB"
