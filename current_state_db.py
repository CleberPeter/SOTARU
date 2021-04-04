from pymongo import MongoClient

class Current_State_DB:
    def __init__(self, name, port = 27017):
        self.name = name
        db_client = MongoClient('localhost', port)
        self.db = db_client['dOTA_' + self.name]

    def delete_table(self, table):
        table = self.db[table]
        table.delete_many({})

    def read_registers(self, table):
        table = self.db[table]
        return table.find()

    def read_register(self, table, query):
        table = self.db[table]
        return table.find(query)

    def insert_author(self, author):
        query = {}
        query['name'] = author['name']
        
        authors_table = self.db['authors']
        
        if self.read_register('authors', query).count() == 0:
            authors_table.insert_one(author)
            return (True, '')
        else:
            return (False, 'author already registered.')