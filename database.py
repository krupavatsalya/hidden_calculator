import mysql.connector
import json
import os

class Db:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.connection = None
        self.cursor = None
        self.initialized = False
        self.database_initialize()

    def database_initialize(self):
        # Load user credentials from a JSON file
        with open("data.json", 'r') as json_file:
            user_credentials = json.load(json_file)
        
        # Check if the provided password matches
        if user_credentials["password"] == self.password:
            try:
                # Establish connection to the MySQL database
                self.connection = mysql.connector.connect(**user_credentials)
                self.cursor = self.connection.cursor()
                
                print("Connection to MySQL database successful")
                self.initialized = True
            except mysql.connector.Error as e:
                print(f"Error connecting to MySQL database: {e}")
                raise  # Raise the exception to notify the caller
        else:
            print("Incorrect password")

    def create_table(self):
        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS hidden_data (email TEXT primary key, password TEXT)")
            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Error creating table: {e}")

    def insert_table(self, email, password):
        try:
            query = 'INSERT INTO hidden_data (email, password) VALUES (%s, %s)'
            self.cursor.execute(query, (email, password))
            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Error inserting into table: {e}")

    def search(self):
        emails=[]
        try:
            self.cursor.execute('SELECT email FROM hidden_data')
            rows = self.cursor.fetchall()
            # Convert the list of tuples to a list of strings
            emails = [row[0] for row in rows]
            return emails
        except mysql.connector.Error as e:
            print(f"Error querying table: {e}")

    def delete_table(self):
        self.cursor.execute("DROP table hidden_data")
        print("DELETED")

    def cursor_close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def search_password(self, email, expression):
        query = 'SELECT password FROM hidden_data WHERE email=%s'
        self.cursor.execute(query, (email,))
        rows = self.cursor.fetchall()

        # Convert the list of tuples to a list of strings
        passwords = [row[0] for row in rows]

        # Check if the provided expression matches any password in the list
        return expression in passwords


def main():
    # Initialize the database connection with credentials
    database = Db("saikumar-007", "Saikumar20@")
    if database.initialized:
        database.create_table()
        database.search()
        database.cursor_close()
    else:
        print("Invalid credentials. Please try again.")

if __name__ == "__main__":
    main()
