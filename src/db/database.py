import sqlite3
from datetime import datetime, timedelta
from models.channel import Channel
from models.channel_data import ChannelData

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                channel_id TEXT NOT NULL UNIQUE,
                channel_point TEXT NOT NULL,
                capacity INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_datas (
                channel_id TEXT NOT NULL,
                date TEXT NOT NULL,
                local_balance INTEGER,
                local_fee INTEGER,
                local_infee INTEGER,
                remote_balance INTEGER,
                remote_fee INTEGER,
                remote_infee INTEGER,
                num_updates INTEGER,
                amboss_fee INTEGER,
                active INTEGER,
                FOREIGN KEY (channel_id) REFERENCES channel_lists (channel_id)
            )
        ''')
        self.conn.commit()

    def get_latest_channel_data(self, channel_id, data_period):
        query = '''
            SELECT * FROM channel_datas
            WHERE channel_id = ?
            ORDER BY date DESC
            LIMIT ?
        '''
        self.cursor.execute(query, (channel_id, data_period))
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def get_channels(self):
        """
        Get all channels from the channel_lists table
        
        Returns:
            list: List of Channel objects
        """
        if not self.cursor:
            return []
            
        try:
            self.cursor.execute("""
                SELECT id, channel_name, channel_id, channel_point, capacity
                FROM channel_lists
            """)
            
            channels = []
            for row in self.cursor.fetchall():
                channel = Channel(
                    id=row[0],
                    channel_name=row[1],
                    channel_id=row[2],
                    channel_point=row[3],
                    capacity=row[4]
                )
                channels.append(channel)
            
            return channels
        except sqlite3.Error as e:
            print(f"Error fetching channels: {e}")
            return []

    def get_recent_channel_data(self, channel_id, limit):
        """
        Get the most recent N channel data records for the specified channel
        
        Args:
            channel_id: The channel ID
            limit: Number of most recent records to retrieve
            
        Returns:
            list: List of ChannelData objects
        """
        if not self.cursor:
            return []
            
        try:
            self.cursor.execute("""
                SELECT channel_id, date, local_balance, local_fee, local_infee,
                       remote_balance, remote_fee, remote_infee, num_updates,
                       amboss_fee, active
                FROM channel_datas
                WHERE channel_id = ?
                ORDER BY date DESC
                LIMIT ?
            """, (channel_id, limit))
            
            rows = self.cursor.fetchall()
            
            # 日付の降順で取得したデータを昇順に並べ替え
            rows.reverse()
            
            channel_data_list = []
            for row in rows:
                channel_data = ChannelData(
                    channel_id=row[0],
                    date=row[1],
                    local_balance=row[2],
                    local_fee=row[3],
                    local_infee=row[4],
                    remote_balance=row[5],
                    remote_fee=row[6],
                    remote_infee=row[7],
                    num_updates=row[8],
                    amboss_fee=row[9],
                    active=bool(row[10])
                )
                channel_data_list.append(channel_data)
            
            return channel_data_list
        except sqlite3.Error as e:
            print(f"Error fetching channel data: {e}")
            return []