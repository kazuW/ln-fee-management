import requests
import codecs
import json
import os
from config import (
    api_url,
    macaroon_path,
    tls_path,
    basefee_msat,
    time_lock_delta,
    Debug_mode
)

class FeeCalculator:
    def __init__(self, config=None, db_connection=None):
        """
        Initialize FeeCalculator with optional config and database connection
        
        Args:
            config: Configuration object or dict
            db_connection: Database connection
        """
        self.config = config
        self.db_connection = db_connection

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

        url = f'{api_url}/v1/chanpolicy'
        macaroon = codecs.encode(open(macaroon_path, 'rb').read(), 'hex')
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
            'base_fee_msat': basefee_msat,  #<int64>
            'fee_rate_ppm':  fee,           #<uint32>
            'time_lock_delta': time_lock_delta, #<uint32>
            'max_htlc_msat': max_htlc_msat,     #<uint64>
            'inbound_fee': inboundFee,           #<InboundFee>
        }

        if Debug_mode:
            #print data
            print(f"Setting done for channel {channel.channel_name}: {channel.channel_id}")
            print("#### data ####")
            print(data)
            print("##############")
            return True

        # 既存のreturnを削除し、APIリクエストを実装
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), verify=tls_path)  # TLS_PATH → tls_path に修正
            response.raise_for_status()
            print(f"Setting done for channel {channel.channel_name}: {channel.channel_id}")
        except requests.exceptions.RequestException as e:
            print(f"Error setting fee for channel {channel.channel_name} ({channel.channel_id}): {e}")
            return False

        return True
