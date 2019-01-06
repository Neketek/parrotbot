class Str(object):
    @staticmethod
    def bool(v):
        vl = v.lower()
        if vl in ['true', 't', '1']:
            return True
        elif vl in ['false', 'f', '0']:
            return False
        else:
            raise ValueError("{} is not boolean str".format(v))
