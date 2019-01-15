def cmd_str(*args, params=[]):
    params = ["<{}>".format(p.lower()) for p in params]
    args = [a.lower() for a in args]
    return " ".join(args+params)
