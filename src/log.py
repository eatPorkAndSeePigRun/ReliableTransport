l = []


def log(fmt, *args):
    if args:
        msg = fmt % args
    else:
        msg = fmt
    l.append(msg)
    if len(l) >= 10000:
        save_log()
        l[:] = []


def save_log():
    with open("log.txt", "a+") as wf:
        wf.write("\n".join(l))
        wf.write("\n")