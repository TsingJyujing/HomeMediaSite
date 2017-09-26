# coding:utf-8





def get_request_with_default(request, key, default_value):
    try:
        return request.GET[key]
    except:
        return default_value


def get_request_get(request, key):
    return get_request_with_default(request, key, None)
