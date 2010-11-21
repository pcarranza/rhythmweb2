'''
RhythmDBTree

shell.props.db

shell.props.db.entry_count()

-------------------------
def do_each(entry):
    print db.entry_get(entry, rhythmdb.PROP_TITLE)

shell.props.db.entry_foreach(do_each)
'''



class RBDBHandler():
    
    db = None
    
    def __init__(self, db):
        self.db = db
        
        
    def list(self, size=10):
        _list = ''
        
    @staticmethod
    def _entry(entry):
        