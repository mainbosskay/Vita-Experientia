#!/usr/bin/python3
"""Module for extraction and slicing of list segments"""
import re


def slice_range(range_str: str, items: list):
    """Slice list according to given range string"""
    if range_str is None:
        return items
    match_span = re.fullmatch(
        r'(?P<size>\d+)(?:,(?P<index>\d+))?',
        range_str
    )
    size = int(match_span.group('size'))
    index = 0
    if match_span.group('index') is not None:
        index = int(match_span.group('index'))
    start = size * index
    end = start + size
    return items[start: end]


def paginate_list(items=[], span=12, after=None, before=None,
                  top_pop=False, key_fxn=lambda k: k['id']):
    """Navigate list of items with optional key-based filtering"""
    result = []
    if after and before:
        return result
    elif after:
        add_item = False
        count = 0
        for item in items:
            if add_item:
                result.append(item)
                count += 1
                if count == span:
                    break
            elif key_fxn(item):
                add_item = True
    elif before:
        count = 0
        for item in items:
            if key_fxn(item):
                break
            else:
                count += 1
        start = count - (span + 1) if count > (span + 1) else 0
        end = count - 1 if count > 1 else 0
        result = items[start:end]
    else:
        result = items[0:span] if top_pop else items[-span:]
    return result
