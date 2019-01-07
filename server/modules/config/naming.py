

# constant dot dict
class cddict(object):
    def __init__(self, *args, **kwargs):
        self.__data = dict(*args, **kwargs)

    def __getattr__(self, key):
        return self.__data.get(key)


short = cddict(
    name=cddict(
        questionnaire='quest',
        question='questions',
        subscriber='sub',
        subscription='subscr',
        report='report'
    ),
    method=cddict(
        list='ls',
        create='create',
        update='update',
        set='set',
        delete='delete'
    ),
    param=cddict(
        days='days'
    )
)
