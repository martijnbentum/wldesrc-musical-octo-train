import read_xml
import load_eeg
from pathlib import Path
from progressbar import progressbar

pmn_channels = 'F7, F3, Fz, F4, F8, FC5, FC1, FC2, FC6, T7, T8'
pmn_channels = pmn_channels.split(', ')
pmn_time_window = [.15,.35]
n400_channels = 'C3, C4, Cz, CP5, CP1, CP2, CP6, P7, P3, Pz, P4, P8, O1, O2'
n400_channels = n400_channels.split(', ')
n400_time_window = [.3,.5]
baseline_time_window = [-.2,.0]

header = 'participant,exp_id,block,word,pmn_baseline,pmn,n400_baseline,n400'
header += ',n_channels_pmn,n_channels_n400'
header = header.split(',')

def check_channels_available_for_pmn(channels):
    count = 0
    for channel in channels:
        if channel in pmn_channels: count += 1
    return count

def check_channels_available_for_n400(channels):
    count = 0
    for channel in channels:
        if channel in n400_channels: count += 1
    return count

def check_if_block_ok(block, participant):
    if block in participant.bad_blocks: return False
    return True

def handle_participants(participant_ids = range(1,48)):
    """
    Handles multiple participants. 
    """
    for pp_id in progressbar(participant_ids):
        handle_participant(pp_id)

def handle_participant(pp_id= 1, participant = None, overwrite = False):
    if participant:
        pp_id = participant.pp_id
    filename = f'../eeg_data/pp{pp_id}_eeg_data.tsv'
    if overwrite is False:
        path = Path(filename)
        if path.exists(): 
            print('file exists doing nothing', filename)
            return
    if participant is None:
        participant = read_xml.load_participant(pp_id, add_words = True)
        _ = load_eeg.load_word_epochs_participant(participant)
    output = []
    print('handling participant', pp_id)
    print(participant)
    n_blocks = 0
    for block in progressbar(participant.blocks):
        o = handle_block(block, participant)
        if o is False: continue
        output.extend(o)
        n_blocks += 1
    print('n_blocks', n_blocks, 'of', len(participant.blocks))
    with open(filename, 'w') as f:
        f.write('\t'.join(header) + '\n')
        f.write('\n'.join(['\t'.join(map(str, line)) for line in output]))
    return output

    
def handle_block(block, participant):
    if not check_if_block_ok(block, participant): 
        return False
    print('handling block', block.name)
    n_channels_pmn = check_channels_available_for_pmn(block.ch)
    n_channels_n400 = check_channels_available_for_n400(block.ch)
    all_channels = block.ch
    eegs = block.extracted_eeg_words
    word_indices = block.extracted_word_indices
    pp_id = participant.pp_id
    exp_id = block.exp_type
    output= []
    for eeg, word_index in zip(eegs, word_indices):
        word = block.words[word_index]
        if not word.usable: raise ValueError('word not useable', word)
        word_identifier = word.stats.word_code
        pmn_baseline = compute_value(eeg, baseline_time_window, pmn_channels,
            all_channels)
        n400_baseline = compute_value(eeg, baseline_time_window, n400_channels,
            all_channels)
        pmn = compute_value(eeg, pmn_time_window, pmn_channels, all_channels)
        n400 = compute_value(eeg, n400_time_window, n400_channels, all_channels)
        output.append([pp_id,exp_id,block.name,word_identifier,pmn_baseline,pmn,
            n400_baseline,n400,n_channels_pmn, n_channels_n400])
    return output

def compute_value(eeg, window, channels, all_channels):
    m = select_matrix(eeg, window, channels, all_channels)
    return m.mean()

def select_matrix(m, time_window, target_channels, all_channels):
    row_indices = channels_to_row_index(all_channels, target_channels)
    start_sample, end_sample = time_window_to_sample_indices(time_window)
    return m[row_indices, start_sample:end_sample]

def channels_to_row_index(all_channels, target_channels):
    row_indices = [all_channels.index(channel) for channel in target_channels
        if channel in all_channels]
    return row_indices

def select_matrix_rows_based_channel_set(m, all_channels, target_channels):
    """
    Selects the rows of a matrix m that correspond to the channels in 
    target_channels.
    """
    row_indices = channels_to_row_index(all_channels, target_channels)
    selected_rows = m[row_indices, :]
    # print('target_channels', target_channels, 'row_indices', row_indices,)
    return selected_rows

def select_columns_based_on_sample_indices(m, start_sample, end_sample):
    """
    Selects the columns of a matrix m that correspond to the time window.
    """
    start, end = start_sample, end_sample
    window= m[:, start_sample:end_sample]
    return window 

def seconds_to_sample(seconds, offset = 300, sample_rate = 1000):
    """
    Converts seconds to sample indices.
    """
    return int(seconds * sample_rate + offset)

def time_window_to_sample_indices(time_window, sample_rate = 1000):
    """
    Converts a time window in seconds to sample indices.
    """
    start, end = time_window
    start_sample = seconds_to_sample(start)
    end_sample = seconds_to_sample(end)
    # print(time_window, start_sample, end_sample)
    return start_sample, end_sample
    
    

    
    
