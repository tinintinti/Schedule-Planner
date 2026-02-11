
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox


class Database:
    """Database connection manager"""
    
    @staticmethod
    def connect():
        """Connect to MariaDB database and return the connection"""
        try:
            conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="planner_db",
            use_pure=True  
        )
            if conn.is_connected():
                return conn
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database:\n{e}")
            raise e
    
    @staticmethod
    def reset_auto_increment():
        """Reset auto_increment counters for all tables"""
        try:
            conn = Database.connect()
            cursor = conn.cursor()
            
            cursor.execute("ALTER TABLE users AUTO_INCREMENT = 1")
            cursor.execute("ALTER TABLE activities AUTO_INCREMENT = 1")
            cursor.execute("ALTER TABLE tasks AUTO_INCREMENT = 1")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error resetting auto_increment: {e}")