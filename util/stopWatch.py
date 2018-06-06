from functools import wraps
import time


def stop_watch(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        start = time.time()
        result = func(*args, **kargs)
        elapsed_time = time.time() - start
        print('%s : %.2f msec' % (func.__name__, elapsed_time*1000))
        return result

    return wrapper


@stop_watch
def test(num):
    for i in range(num):
        x = i * 100
    return x


if __name__ == '__main__':
    test(100000)
