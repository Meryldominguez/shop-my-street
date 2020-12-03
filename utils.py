import functools





def login_required(func):
    @functools.wraps(func)
    def wrapper():
        if g.user:
            pass
        else:
            