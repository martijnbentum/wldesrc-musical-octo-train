import json
import load_eeg
import read_xml


def make_words_read_aloud_books(participant = None, 
    filename = '../words_read_aloud_books.json'):
    if participant is None:
        participant = load_xml.load_participant(pp_id = 1, add_words = True)
        load_word_epochs_participant(participant, unload_eeg = False)
    words = []
    blocks = [b for b in participant.blocks if b.exp_type == 'o']
    for block in blocks:
        for word in block.words:
            words.append(word)
    w = Words(words)
    w.save_json(filename)
    return w

class Words:
    def __init__(self, words):
        self.word_infos = words
        self._set_info()

    def _set_info(self):
        self.words =[]
        for word in self.word_infos:
            word = Word(word)
            self.words.append(word)

    def __repr__(self):
        return f"Words: {len(self.words)}"

    def to_dict(self):
        return {word.word_number: word.to_dict() for word in self.words}

    def save_json(self, path = None):
        if path is None:
            path = '../words.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)


class Word:
    def __init__(self, word): 
        self.word_info = word
        self._set_info()
        word = self.word

    def _set_info(self):
        self.word = self.word_info.word_utf8_nocode
        self.block_name = '_'.join(self.word_info.block_name.split('_')[1:])
        self.wav_filename = self.word_info.block.wav_filename
        self.end_of_sentence = eval(self.word_info.eol)
        self.start_time = self.word_info.st
        self.end_time = self.word_info.et
        self.duration = round(self.word_info.et - self.word_info.st, 3)
        self.word_id = self.word_info.name
        self.word_index_in_block = self.word_info.word_index_in_block
        self.speaker_id = self.word_info.sid
        self.usable = self.word_info.usable
        self.content_word = self.word_info.pos.content_word
        self.pos_simple = self.word_info.pos.pos_simple
        self.pos_tag = self.word_info.pos.pos_tag
        self.word_frequency = self.word_info.stats.word_frequency
        self.word_number = self.word_info.stats.word_number

        self.names = ['word', 'block_name', 'wav_filename', 'end_of_sentence',
            'start_time', 'end_time','duration', 'word_id', 
            'word_index_in_block', 'speaker_id','usable', 'content_word', 
            'pos_simple', 'pos_tag', 'word_frequency', 'word_number']
            
            

    def __repr__(self):
        return f"Word: {self.word} | {self.word_number}"

    def to_dict(self):
        d = {}
        for name in self.names:
            d[name] = getattr(self, name) 
        return d
        
