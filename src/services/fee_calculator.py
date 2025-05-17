import requests
import codecs
import json
import os

class FeeCalculator:
    def __init__(self, config, db_connection):
        """
        Initialize FeeCalculator with optional config and database connection
        
        Args:
            config: Configuration object or dict
            db_connection: Database connection
        """
        self.config = config
        self.db_connection = db_connection
        # API関連の設定を取得
        self.api_url = config.get_api_url() if config else None
        self.macaroon_path = config.get_macaroon_path() if config else None
        self.tls_path = config.get_tls_path() if config else None
        self.basefee_msat = config.get_basefee_msat() if config else 0
        self.time_lock_delta = config.get_time_lock_delta() if config else 0

    def get_latest_data(self, channel_id):
        # This method should retrieve the latest data for the given channel_id from the database
        pass  # Implementation will depend on the database structure and queries used

    def set_fee_api(self, channel, fee, infee, local_balance=None):
        """
        Set local fee & inbound fee for a channel using lightning-api.
        
        Args:
            channel_id: Channel ID
            fee: Fee amount
            infee: Inbound fee amount
        """

        if infee > 0:
            print(f"parameter error infee={infee}")
            return False

        max_htlc_msat = int(local_balance / 3 * 2 * 1000)

        # グローバル変数ではなくインスタンス変数を使用
        url = f'{self.api_url}/v1/chanpolicy'
        macaroon = codecs.encode(open(self.macaroon_path, 'rb').read(), 'hex')
        headers = {'Grpc-Metadata-macaroon': macaroon}

        inboundFee = {
            'base_fee_msat': 0,
            'fee_rate_ppm': infee
        }

        funding_txid_str = channel.channel_point.split(':')[0]
        output_index = int(channel.channel_point.split(':')[1])

        channelPoint = {
            'funding_txid_str': funding_txid_str,
            'output_index': output_index
        }

        data = {
            'chan_point': channelPoint, #<ChannelPoint>
            'base_fee_msat': self.basefee_msat,  #<int64>
            'fee_rate_ppm':  fee,           #<uint32>
            'time_lock_delta': self.time_lock_delta, #<uint32>
            'max_htlc_msat': max_htlc_msat,     #<uint64>
            'inbound_fee': inboundFee,           #<InboundFee>
        }

        # Debug_modeもconfigから取得
        debug_mode = self.config.get_debug_mode() if hasattr(self.config, 'get_debug_mode') else False
        
        if debug_mode:
            #print data
            print(f"Setting done for channel {channel.channel_name}: {channel.channel_id}")
            print("#### data ####")
            print(data)
            print("##############")
            return True

        # 既存のreturnを削除し、APIリクエストを実装
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), verify=self.tls_path)
            response.raise_for_status()
            print(f"Setting done for channel {channel.channel_name}: {channel.channel_id}")
        except requests.exceptions.RequestException as e:
            print(f"Error setting fee for channel {channel.channel_name} ({channel.channel_id}): {e}")
            return False

        return True
