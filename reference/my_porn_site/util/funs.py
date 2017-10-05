# coding:utf-8


def time2duration(time_secs):
    time_secs = int(time_secs)
    if time_secs < 60:
        return "0:00:%d" % time_secs
    elif time_secs < 3600:
        return "0:%02d:%02d" % (time_secs / 60, time_secs % 60)
    else:
        h = time_secs / 3600
        m = (time_secs - 3600 * h) / 60
        return "%d:%02d:%02d" % (h, m, time_secs % 60)