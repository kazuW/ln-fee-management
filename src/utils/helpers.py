def calculate_local_fee(amboss_fee, local_balance, capacity, local_fee_ratios):
    ratio = local_balance / capacity if capacity > 0 else 0
    if ratio >= 0.8:
        return amboss_fee * local_fee_ratios[0]
    elif ratio >= 0.6:
        return amboss_fee * local_fee_ratios[1]
    elif ratio >= 0.4:
        return amboss_fee * local_fee_ratios[2]
    elif ratio >= 0.2:
        return amboss_fee * local_fee_ratios[3]
    else:
        return amboss_fee * local_fee_ratios[4]

def calculate_inbound_fee(local_balance, capacity, inbound_fee_base, inbound_fee_ratios):
    ratio = local_balance / capacity if capacity > 0 else 0
    if ratio >= 0.8:
        return inbound_fee_base * inbound_fee_ratios[0]
    elif ratio >= 0.6:
        return inbound_fee_base * inbound_fee_ratios[1]
    elif ratio >= 0.4:
        return inbound_fee_base * inbound_fee_ratios[2]
    elif ratio >= 0.2:
        return inbound_fee_base * inbound_fee_ratios[3]
    else:
        return inbound_fee_base * inbound_fee_ratios[4]

def is_data_valid(data, min_data_num, local_balance_ratio_range):
    if len(data) < min_data_num:
        return False
    for entry in data:
        local_balance_ratio = entry['local_balance'] / entry['capacity'] if entry['capacity'] > 0 else 0
        if not any(lower <= local_balance_ratio <= upper for lower, upper in local_balance_ratio_range):
            return False
    return True

def get_local_balance_ratio_range():
    return [(0.8, 1.0), (0.6, 0.8), (0.4, 0.6), (0.2, 0.4), (0.0, 0.2)]