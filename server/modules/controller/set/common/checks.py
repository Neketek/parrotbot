

def compare_found_expected(
    found,
    expected,
    extract=lambda x: x,
    prefix=""
):
    if len(found) == len(expected):
        return
    found = [extract(i) for i in found]
    not_found = [i for i in expected if i not in found]
    raise ValueError("{} *{}* not found".format(prefix, ",".join(not_found)))
