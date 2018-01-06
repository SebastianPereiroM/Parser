# -*- coding: utf-8 -*-

import sys


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
sys.stdout.flush()


def task_with_progress(task_message, total_count, gen_function, suppress_progress_bar=False):
    print(task_message)
    result = []
    count = 0
    progress(count, total_count)
    for item in gen_function:
        result.append(item)
        count += 1
        if not suppress_progress_bar:
            progress(count, total_count)
    print()
    return result
