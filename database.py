import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash
from exceptions import UserExistsException, UserDoesntExistException

#-----------------------------------------------------------------------------------

#User class to represent a user in the system
class User:
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
    """

    def __init__(self, id : int, username : str) -> None:
        self.id = id
        self.username = username
        print(f"User created: {self}")

    def __repr__(self):
        return f"<User: {self.username} id: {self.id}>"

#------------------------------------------------------------------------------------


# Database class to handle all database operations
class Database:
    """
    Handles all database operations for the workout application.

    Attributes:
        _conn (sqlite3.Connection): Internal connection object to the SQLite database.
        _cur (sqlite3.Cursor): Internal cursor object for executing SQL commands.
        _table_schema (dict): Internal dictionary containing the SQL schema for each table in the database.
    """

    def __init__(self, db_name='workout.db') -> None:
        self._conn = sqlite3.connect(db_name)
        self._cur = self._conn.cursor()

        self._table_schema = {
            "users": '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                pass TEXT NOT NULL
            )
            ''',

            "workout_programs": '''
            CREATE TABLE IF NOT EXISTS workout_programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                currently_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''',

            "workouts": '''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (program_id) REFERENCES workout_programs(id)
            )
            '''
        }
    
    def drop_tables(self) -> None:
        """
        drops all tables in the database if they exist.

        Raises:
            Exception: If there is an error dropping any of the tables.
        """

        for t in self._table_schema.keys():
            try:
                self._cur.execute(f"DROP TABLE IF EXISTS {t}")
                print(f"Table {t} successfully dropped")
            except Exception as e:
                print(f"Error dropping table {t}: {e}")

        self._conn.commit()
        
    def create_tables(self) -> None:
        """
        Creates the necessary tables in the database based on the defined schema.
        
        Raises:
            Exception: If there is an error creating any of the tables.
        """

        for t in self._table_schema.keys():
            try:
                self._cur.execute(self._table_schema[t])
                print(f"Table {t} successfully loaded")
            except Exception as e:
                print(f"Error creating table {t}: {e}")
        
        self._conn.commit()

    def get_user(self, username : str, password : str) -> User:
        """
        Retrieves a user from the database based on the provided username and password.

        Args:
            username (str): The username of the user to retrieve.
            password (str): The unhashed password of the user to retrieve.
        
        Raises:
            UserDoesntExistException: If no user with the provided username and password exists in the database.

        Returns:
            User: A User object representing the retrieved user if the username and password are correct.   
        """

        self._cur.execute("SELECT id, name, pass FROM users WHERE name = ?", (username,))
        result = self._cur.fetchone()

        if result and check_password_hash(result[2], password):
            return User(result[0], result[1])
        else:
            raise UserDoesntExistException("User does not exist")
    
    def get_user_by_name(self, username : str) -> User:
        """
        Retrieves a user from the database based on the provided username.

        Args:
            username (str): The username of the user to retrieve.
        
        Raises:
            UserDoesntExistException: If no user with the provided username exists in the database.

        RETURNS:
            User: A User object representing the retrieved user if the username exists.   
        """

        self._cur.execute("SELECT id, name FROM users WHERE name = ?", (username,))
        result = self._cur.fetchone()

        if result:
            return User(result[0], result[1])
        else:
            raise UserDoesntExistException("User does not exist")
    
    def create_user(self, username : str, password : str) -> User:
        """
        Creates a new user in the database with the provided username and password.
        
        Args:
            username (str): The username of the new user to create.
            password (str): The unhashed password of the new user to create.
        
        Raises:
            UserExistsException: If a user with the provided username already exists in the database.
            Exception: If there is an error inserting the new user into the database.
        
        Returns:
            User: A User object representing the newly created user if the operation is successful.
        """

        try:
            already_user = self.get_user_by_name(username)
        except UserDoesntExistException:
            already_user = None

        if already_user:
            raise UserExistsException("Username already exists.")

        self._cur.execute("INSERT INTO users (name, pass) VALUES (?, ?)", (username, generate_password_hash(password)))
        self._conn.commit()

        new_user = self.get_user(username, password)

        return new_user


#------------------------------------------------------------------------------------
