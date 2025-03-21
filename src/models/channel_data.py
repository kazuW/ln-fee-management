class ChannelData:
    def __init__(self, channel_id, date, local_balance, local_fee, local_infee, remote_balance, remote_fee, remote_infee, num_updates, amboss_fee, active):
        self.channel_id = channel_id
        self.date = date
        self.local_balance = local_balance
        self.local_fee = local_fee
        self.local_infee = local_infee
        self.remote_balance = remote_balance
        self.remote_fee = remote_fee
        self.remote_fee = remote_infee
        self.amboss_fee = amboss_fee
        self.num_updates = num_updates
        self.active = active

    def calculate_inbound_fee(self, inbound_fee_base, inbound_fee_ratio):
        ratio = self.local_balance / self.remote_balance if self.remote_balance > 0 else 0
        return inbound_fee_base * inbound_fee_ratio[min(int(ratio * 5), 4)]

    def adjust_local_fee(self, local_fee_ratio):
        return self.amboss_fee * local_fee_ratio[min(int(self.local_balance / self.remote_balance * 5), 4)]