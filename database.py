from exceptions import UserExistsException, UserDoesntExistException


import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

#-----------------------------------------------------------------------------------

#User class to represent a user in the system
class User:
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
    """

    def __init__(self, id : int, username : str):
        self.id = id
        self.username = username
        print(f"User created: {self}")

    def __repr__(self):
        return f"<User: {self.username} id: {self.id}>"
    

#------------------------------------------------------------------------------------

#Workout_program class to represent a workout program in the system    
class Workout_Program:
    """
    Represents a Workout Program owned by a user

    Attributes:
        id (int): The unique identifier for the workout program.
        user_id (int): The unique identifier of the user who owns the workout program.
        name (str): The name of the workout program.
    """ 

    def __init__(self, id : int, user_id : int, name : str, description : str = None, created_at : str = None, currently_active : bool = True):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.currently_active = currently_active

    def __repr__(self):
        return f"<Workot Program: id: {self.id} name: {self.name} owned by: {self.user_id}"

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

    def __init__(self, db_name='workout.db'):
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
                created_at TEXT,
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
    
    # Database management methods

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
    
    # User management methods
    
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
    
    # Workout program management methods
    
    def retrieve_all_workout_programs(self) -> list[Workout_Program]:
        """
        Will retrieve all workout programs in the database and return them as a list of Workout_Program objects
        
        Returns:
            List[Workout_Program]: A list of all Workout_Program objects in the database.
        """

        self._cur.execute("SELECT id, user_id, name, description, created_at, currently_active FROM workout_programs")
        results = self._cur.fetchall()

        workout_program_list = []
        for result in results:
            new_workout_program = Workout_Program(result[0], result[1], result[2], result[3], result[4], result[5])
            workout_program_list.append(new_workout_program)

        return workout_program_list
    
    def retrieve_workout_program_by_id(self, program_id : int) -> Workout_Program:
        """
        Retrieves a workout program from the database based on the provided program ID.

        Args:
            program_id (int): The unique identifier of the workout program to retrieve.

        Returns:
            Workout_Program: A Workout_Program object representing the retrieved workout program if it exists, or None if it does not exist.
        """

        self._cur.execute("SELECT id, user_id, name, description, created_at, currently_active FROM workout_programs WHERE id = ?", (program_id,))
        result = self._cur.fetchone()

        if result:
            return Workout_Program(result[0], result[1], result[2], result[3], result[4], result[5])
        else:
            return None

    def create_workout_program(self, name : str, user_id : int, description : str = None, created_at : str = None, currently_active : bool = True) -> Workout_Program:
        """
        Creates a new workout program in the database with the provided name and user ID.

        Args:
            name (str): The name of the new workout program to create.
            user_id (int): The unique identifier of the user who owns the new workout program.
            description (str, optional): A description of the new workout program. Defaults to None.
            created_at (str, optional): The timestamp of when the new workout program was created. Defaults to None, which will use the current timestamp.
            currently_active (bool, optional): Whether the new workout program is currently active. Defaults to True.

        Returns:
            Workout_Program: A Workout_Program object representing the newly created workout program if the operation is successful.
        """

        if not created_at:
            created_at = datetime.now().isoformat()

        self._cur.execute(
            "INSERT INTO workout_programs (name, user_id, description, created_at, currently_active) VALUES (?, ?, ?, ?, ?)", 
            (name, user_id, description, created_at, currently_active)
        )
        self._conn.commit()

        new_program_id = self._cur.lastrowid
        new_workout_program = self.retrieve_workout_program_by_id(new_program_id)

        return new_workout_program

    def update_workout_program(self, program_id : int, name : str = None, description : str = None, currently_active : bool = None) -> Workout_Program:
        """
        Updates an existing workout program in the database with the provided information.

        Args:
            program_id (int): The unique identifier of the workout program to update.
            name (str, optional): The new name for the workout program. Defaults to None, which will not update the name.
            description (str, optional): The new description for the workout program. Defaults to None, which will not update the description.
            currently_active (bool, optional): The new active status for the workout program. Defaults to None, which will not update the active status.

        Raises:
            Exception: If there is an error retrieving the existing workout program from the database.

        Returns:
            Workout_Program: A Workout_Program object representing the updated workout program if the operation is successful, or None if no workout program with the provided ID exists.
        """

        try:
            existing_program = self.retrieve_workout_program_by_id(program_id)
        except Exception as e:
            print(f"Error occurred while retrieving workout program: {e}")
            return None

        updated_name = name if name is not None else existing_program.name
        updated_description = description if description is not None else existing_program.description
        updated_currently_active = currently_active if currently_active is not None else existing_program.currently_active

        self._cur.execute(
            "UPDATE workout_programs SET name = ?, description = ?, currently_active = ? WHERE id = ?", 
            (updated_name, updated_description, updated_currently_active, program_id)
        )
        self._conn.commit()

        return existing_program
#------------------------------------------------------------------------------------