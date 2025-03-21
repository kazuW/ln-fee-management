class DataAnalyzer:
    def __init__(self, db_connection=None, config=None):
        """
        Initialize DataAnalyzer with optional database connection and configuration
        
        Args:
            db_connection: Database connection 
            config: Configuration object or dict
        """
        self.db_connection = db_connection
        self.config = config

    def analyze_channel_data(self, channel_id):
        # Fetch the latest data for the given channel_id
        latest_data = self.fetch_latest_data(channel_id)
        if not latest_data:
            return

        # Analyze the data to determine local fee adjustments
        local_balance_ratio = latest_data['local_balance'] / latest_data['capacity']
        historical_data = self.fetch_historical_data(channel_id)

        if len(historical_data) >= self.config['min_data_num']:
            if self.is_within_tolerance(historical_data, local_balance_ratio):
                self.adjust_local_fee(channel_id, latest_data['local_fee'] * 0.9)
            else:
                self.set_local_fee_based_on_amboss(channel_id, latest_data['amboss_fee'])

    def fetch_latest_data(self, channel_id):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM channel_datas WHERE channel_id = ? ORDER BY date DESC LIMIT 1", (channel_id,))
        return cursor.fetchone()

    def fetch_historical_data(self, channel_id):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM channel_datas WHERE channel_id = ? ORDER BY date DESC LIMIT ?", (channel_id, self.config['data_period']))
        return cursor.fetchall()

    def is_within_tolerance(self, channel_data, capacity):
        """
        Check if all channel data entries have local balance ratios within the same range.
        Ranges are: 100-80%, 80-60%, 60-40%, 40-20%, 20-0%
        
        Args:
            channel_data: List of channel data objects
            capacity: Channel capacity
            
        Returns:
            bool: True if all entries are within the same range
        """
        if not channel_data:
            return False
            
        # Calculate range for each data point (as bit flags)
        ranges = []
        for data in channel_data:
            local_ratio = data.local_balance / capacity
            range_flags = self._get_range_flags(local_ratio)
            ranges.append(range_flags)
        
        # Check if all ranges have at least one common range
        common_range = ranges[0]
        for r in ranges[1:]:
            common_range &= r
            
        return common_range > 0

    def is_within_tolerance_1(self, channel_data, capacity):
        """
        Check if latest channel data and previous data have local balance ratios within the same range.
        Ranges are: 100-80%, 80-60%, 60-40%, 40-20%, 20-0%
        
        Args:
            channel_data: List of channel data objects
            capacity: Channel capacity
            
        Returns:
            bool: True if the latest two entries are within the same range
        """
        if len(channel_data) < 2:  # 少なくとも2つのデータポイントが必要
            return False
            
        # Calculate range for each data point (as bit flags)
        ranges = []
        for data in channel_data:
            local_ratio = data.local_balance / capacity
            range_flags = self._get_range_flags(local_ratio)
            ranges.append(range_flags)
        
        # 最新の2つのデータポイントのみをチェック (channel_dataは時系列順なので末尾が最新)
        latest_range = ranges[-1]  # 最新のデータポイント
        previous_range = ranges[-2]  # 1つ前のデータポイント
        
        # Check if the latest two entries have at least one common range
        common_range = latest_range & previous_range
            
        return common_range > 0

    def _get_range_flags(self, ratio):
        """
        Convert a ratio to a binary flag representation of which range it belongs to.
        
        Args:
            ratio: Local balance ratio (0-1)
            
        Returns:
            int: Binary representation of ranges (e.g. 00100)
        """
        flags = 0
        
        if 0.8 <= ratio <= 1.0:
            flags |= 0b10000
        if 0.6 <= ratio < 0.8:
            flags |= 0b01000
        if 0.4 <= ratio < 0.6:
            flags |= 0b00100
        if 0.2 <= ratio < 0.4:
            flags |= 0b00010
        if 0.0 <= ratio < 0.2:
            flags |= 0b00001
            
        return flags

    def is_same_localfee(self, channel_data, capacity):
        """
        ローカル手数料がすべて同じかどうかを確認する
        
        Args:
            channel_data: チャネルデータのリスト
            capacity: チャネルの容量
            
        Returns:
            bool: データが許容範囲内ならTrue、そうでなければFalse
        """
        # 過去のlocal_feeが全て同じかチェック
        if len(channel_data) <= 1:
            return False
        
        # 最初のfee値を基準にする
        base_fee = channel_data[0].local_fee
        
        # 全てのfeeが同じかチェック
        all_fees_same = all(data.local_fee == base_fee for data in channel_data)
        
        # もし全てのfeeが同じでなければ、条件を満たさない
        if not all_fees_same:
            return False

        return True

    def adjust_local_fee(self, channel_id, new_fee):
        cursor = self.db_connection.cursor()
        cursor.execute("UPDATE channel_datas SET local_fee = ? WHERE channel_id = ?", (new_fee, channel_id))
        self.db_connection.commit()

    def set_local_fee_based_on_amboss(self, channel_id, amboss_fee):
        local_fee_ratio = self.config['LocalFee_ratio']
        new_fee = amboss_fee * local_fee_ratio
        self.adjust_local_fee(channel_id, new_fee)