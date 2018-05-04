

def further_allowed_domains_confirm(list_, url_):
    if list_:
        for x in list_:
            if x in url_:
                return True
    else:
        return False







