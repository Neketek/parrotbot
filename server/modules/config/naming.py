

# constant dot dict
class cddict(object):
    def __init__(self, *args, **kwargs):
        self.__data = dict(*args, **kwargs)

    def __getattr__(self, key):
        return self.__data.get(key)


short = cddict(
    name=cddict(
        questionnaire='q',
        question='qs',
        subscriber='s',
        subscription='ss',
        report='r'
    ),
    method=cddict(
        list='ls',
        create='c',
        update='u',
        set='s',
        delete='d'
    ),
    param=cddict(
        days='days'
    )
)
