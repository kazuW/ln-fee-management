import sqlite3
import csv
import argparse
import sys
import io
import os

from config import (
    database_file,
    fixed_channel_list,
    control_channel_list,
    inboundFee_base,
    inboundFee_ratio,
    LocalFee_ratio,
    data_period,
    fee_decreasing_threshold
)
from db.database import Database
from services.fee_calculator import FeeCalculator
from services.data_analyzer import DataAnalyzer

# エンコーディングを設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Lightning Network Fee Manager')
    parser.add_argument('--initial', action='store_true', help='Initial fee setup mode')
    parser.add_argument('--channel_download', action='store_true', help='Download all channel info to CSV')
    args = parser.parse_args()

    db = Database(database_file)
    db.connect()

    # Load fixed channel list
    fixed_channels = load_channel_list(fixed_channel_list)
    control_channels = load_channel_list(control_channel_list)

    print(f"Loaded {len(fixed_channels)} fixed channels...")
    print(f"Loaded {len(control_channels)} control channels...")

    # Initialize fee calculator and data analyzer
    fee_calculator = FeeCalculator(config=None, db_connection=db.conn)
    data_analyzer = DataAnalyzer(db_connection=db.conn, config=None)

    # Process channels
    channels = db.get_channels()

    print(f"Processing {len(channels)} channels...")
    
    # 全てのチャネル情報をCSVに出力
    if args.channel_download:
        download_all_channels(channels)
        print(f"Downloaded {len(channels)} channels to data/all_channel_list.csv")
        db.close()
        return

    print(f"Mode: {'Initial setup' if args.initial else 'Regular analysis'}")

    # Iterate through all channels
    if args.initial:
        for channel in channels:
            # Initial setup mode
            process_channel_initial_mode(channel, db, fee_calculator, fixed_channels, control_channels)
    else:
        for channel in channels:
            # Regular analysis mode
            process_channel_regular_mode(channel, db, fee_calculator, data_analyzer, fixed_channels, control_channels)

    db.close()

def process_channel_initial_mode(channel, db, fee_calculator, fixed_channels, control_channels):
    """Process a channel in initial setup mode"""
    #print(f"Processing channel {channel.channel_id}...")
    channel_data = db.get_recent_channel_data(channel.channel_id, data_period)

    if len(channel_data) == 0:
        print(f"No data available for channel {channel.channel_id}")
        return

    latest_data = channel_data[-1]

    if latest_data.active == 0:
        # Skip inactive channels
        # print(f"Skipping inactive channel {channel.channel_name}")
        return

    if channel.channel_id in fixed_channels:
        # Set fixed fee for this channel
        fixed_fee = int(fixed_channels[channel.channel_id]) - inboundFee_base

        #debug fixed_fee, latest_data.local_fee, inbound_fee, latest_data.local_infee
        #print(f"fixed_fee={fixed_fee}, latest_data.local_fee={latest_data.local_fee}, inbound_fee={inboundFee_base}, latest_data.local_infee={latest_data.local_infee}")

        if fixed_fee == latest_data.local_fee and inboundFee_base == latest_data.local_infee:
            # Skip if fees are already set
            # print(f"Fees are already set for channel {channel.channel_name}")
            return

        print(f"Set fixed fee={fixed_fee} & inbound fee={inboundFee_base} for channel {channel.channel_name}")
        fee_calculator.set_fee_api(channel, fixed_fee, inboundFee_base, latest_data.local_balance)
        
        return
    
    if channel.channel_id in control_channels:
        # For non-fixed channels, get the latest data
        local_balance_ratio = latest_data.local_balance / channel.capacity
        
        # Calculate ratio index (0-4)
        ratio_index = min(int(local_balance_ratio * 5), 4)
        
        # Set inbound fee based on ratio
        if latest_data.amboss_fee is not None:
            if latest_data.amboss_fee > 5000:
                latest_data.amboss_fee = 5000

            inbound_fee = int(inboundFee_base + (latest_data.amboss_fee * inboundFee_ratio[ratio_index]))

            if inbound_fee > 0:
                inbound_fee = 0
        
        # Set local fee based on amboss fee and ratio
        if latest_data.amboss_fee is not None:
            if latest_data.amboss_fee > 5000:
                latest_data.amboss_fee = 5000

            local_fee = int(latest_data.amboss_fee * LocalFee_ratio[ratio_index]) - inboundFee_base
        
        if local_fee == latest_data.local_fee and inbound_fee == latest_data.local_infee:
            # Skip if fees are already set
            # print(f"Fees are already set for channel {channel.channel_name} (ratio: {local_balance_ratio:.2f})")
            return
        
        print(f"Set initial local fee {local_fee} and inbound fee {inbound_fee} for channel {channel.channel_name} (ratio: {local_balance_ratio:.2f})")
        fee_calculator.set_fee_api(channel, local_fee, inbound_fee, latest_data.local_balance)

def process_channel_regular_mode(channel, db, fee_calculator, data_analyzer, fixed_channels, control_channels):
    """Process a channel in regular analysis mode"""
    #print(f"Processing channel {channel.channel_id}...")
    channel_data = db.get_recent_channel_data(channel.channel_id, data_period)

    if len(channel_data) == 0:
        print(f"No data available for channel {channel.channel_id}")
        return

    latest_data = channel_data[-1]

    if latest_data.active == 0:
        # Skip inactive channels
        # print(f"Skipping inactive channel {channel.channel_name}")
        return

    if channel.channel_id in fixed_channels:
        # Set fixed fee for this channel
        fixed_fee = int(fixed_channels[channel.channel_id]) - inboundFee_base

        #debug fixed_fee, latest_data.local_fee, inbound_fee, latest_data.local_infee
        #print(f"fixed_fee={fixed_fee}, latest_data.local_fee={latest_data.local_fee}, inbound_fee={inboundFee_base}, latest_data.local_infee={latest_data.local_infee}")

        if fixed_fee == latest_data.local_fee and inboundFee_base == latest_data.local_infee:
            # Skip if fees are already set
            # print(f"Fees are already set for channel {channel.channel_name}")
            return

        print(f"Set fixed fee={fixed_fee} & inbound fee={inboundFee_base} for channel {channel.channel_name}")
        fee_calculator.set_fee_api(channel, fixed_fee, inboundFee_base, latest_data.local_balance)
        return

    if channel.channel_id in control_channels:

        if len(channel_data) < data_period:
            # print(f"Skipping channel {channel.channel_name}: insufficient data ({len(channel_data)}/{data_period})")
            return
        
        local_balance_ratio = latest_data.local_balance / channel.capacity
        within_tolerance = data_analyzer.is_within_tolerance(channel_data, channel.capacity)
        within_tolerance_1 = data_analyzer.is_within_tolerance_1(channel_data, channel.capacity)        
        same_localfee = data_analyzer.is_same_localfee(channel_data, channel.capacity)

        # Regular mode: analyze data and adjust fees
        if local_balance_ratio >= fee_decreasing_threshold and within_tolerance and same_localfee:

            new_inbound_fee = latest_data.local_infee
            new_local_fee = int((latest_data.local_fee + inboundFee_base) * 0.9 - inboundFee_base)

            if new_local_fee < -inboundFee_base:
                new_local_fee = -inboundFee_base
                
            print(f"Decreasing local fee {latest_data.local_fee} --> {new_local_fee} for channel {channel.channel_name} (ratio: {local_balance_ratio:.2f})")
            fee_calculator.set_fee_api(channel, new_local_fee, new_inbound_fee, latest_data.local_balance)

        elif not within_tolerance_1:
            ratio_index = min(int(local_balance_ratio * 5), 4)
            
            # Set inbound fee based on ratio
            if latest_data.amboss_fee is not None:
                if latest_data.amboss_fee > 5000:
                    latest_data.amboss_fee = 5000
                
                new_inbound_fee = int(inboundFee_base + (latest_data.amboss_fee * inboundFee_ratio[ratio_index]))
        
            if new_inbound_fee > 0:
                new_inbound_fee = 0

            # Set local fee based on amboss fee and ratio
            if latest_data.amboss_fee is not None:
                if latest_data.amboss_fee > 5000:
                    latest_data.amboss_fee = 5000

                new_local_fee = int(latest_data.amboss_fee * LocalFee_ratio[ratio_index]) - inboundFee_base

            print(f"Ratio changed: local fee {latest_data.local_fee} --> {new_local_fee} for channel {channel.channel_name} (ratio: {local_balance_ratio:.2f})")
            fee_calculator.set_fee_api(channel, new_local_fee, new_inbound_fee, latest_data.local_balance)

def download_all_channels(channels):
    """
    すべてのチャネル情報をCSVに出力する
    
    Args:
        channels: チャネルのリスト
    """
    os.makedirs("data", exist_ok=True)
    output_file = "data/all_channel_list.csv"
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # ヘッダー行を書き込む
        writer.writerow(["channel_name", "channel_id", "fee"])
        
        # 各チャネルの情報を書き込む
        for channel in channels:
            # 現在のfeeは0として出力（この値は後で手動で編集可能）
            writer.writerow([channel.channel_name, channel.channel_id, 0])
    
    print(f"チャネル情報を {output_file} に出力しました。")

def load_channel_list(filename):
    """
    Load channel list from CSV file
    
    Args:
        filename: CSV filename
        
    Returns:
        dict: Dictionary with channel IDs as keys and fees as values
    """
    channels = {}
    try:
        # UTF-8エンコーディングを明示的に指定
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # ヘッダー行をスキップ
            for row in reader:
                if len(row) >= 3:
                    channels[row[1]] = row[2]  # channel_id をキーとして fee を値として保存
    except FileNotFoundError:
        print(f"Warning: Channel list file {filename} not found")
    except Exception as e:
        print(f"Error loading channel list: {e}")
    
    return channels

if __name__ == "__main__":
    main()