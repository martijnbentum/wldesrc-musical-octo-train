pmn_channels = 'F7, F3, Fz, F4, F8, FC5, FC1, FC2, FC6, T7, T8'
pmn_channels = pmn_channels.split(', ')
pmn_time_window = [150,350]
n400_channels = 'C3, C4, Cz, CP5, CP1, CP2, CP6, P7, P3, Pz, P4, P8, O1, O2'
n400_channels = n400_channels.split(', ')
n400_time_window = [300,500]
baseline_time_window = [-200,0]

def check_minimal_n_channels_available_for_pmn(channels):
    count = 0
    for channel in channels:
        if channel in pmn_channels: count += 1
    if count < 8: return False
    return True

def check_minimal_n_channels_available_for_n400(channels):
    count = 0
    for channel in channels:
        if channel in n400_channels: count += 1
    if count < 10: return False
    return True

def check_if_block_ok(block, participant):
    if b in participant['bad_blocks']: return False
    return True

def compute_value(eeg, window, channels, all_channels):
    pass
    
def handle_block(block, participant, section = 'n400'):
    if not check_if_block_ok(block, participant): 
        return False

    if section == 'n400':
        f = check_minimal_n_channels_available_for_n400
        channels = n400_channels
        window = n400_time_window
        compute_value = compute_n400
    elif section == 'pmn':
        f = check_minimal_n_channels_available_for_pmn
        channels = pmn_channels
        window = pmn_time_window
        compute_value = compute_pmn
    else:
        raise ValueError('section must be either n400 or pmn')
    if not f(block.ch):
        return False
    all_channels = block.ch
    eegs = block.extracted_eeg_words
    words = block.extracted_word_indices
    line = []
    for eeg, word in zip(eegs, words):
        baseline = compute_baseline(eeg, word, baseline_time_window, channels,
        all_channels)
        value = compute_value(eeg, word, window, channels, all_channels)
        output.append([word,baseline,value])
    return output


    
    
