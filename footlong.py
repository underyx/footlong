#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import sys
import json
import argparse
from datetime import datetime

import requests

__version__ = '0.1.0'


def load_menu_data(source_url):
    return requests.get(source_url).json()


def filter_menu_data(places, filter_ids=None):
    return [
        place for place in places if not filter_ids or place['id'] in filter_ids
    ]


def generate_message(place):
    today = datetime.now().strftime('%Y-%m-%d')

    menus = {
        menu['name']: ''.join(
            '<li>{0}</li>'.format(course)
            for course in menu['itemDescription'].split('\n')
        )
        for menu in place['items'] if menu['date'] == today
    }

    return ''.join(
        '<strong>{0}:</strong><ul>{1}</ul>'.format(
            place['name'] + (' ' + menu_name if menu_name else ''), menu_items
        )
        for menu_name, menu_items in menus.items()
    )


def send_hipchat_notification(message, room, token):
    url = 'https://api.hipchat.com/v2/room/{0}/notification?auth_token={1}'
    data = {
        'message': message,
        'notify': True,
        'color': 'green'
    }

    return requests.post(
        url.format(room, token),
        json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--source-url', help='the source URL to retrieve data from',
        default='http://ebedmenu.hu/places/generate'
    )
    parser.add_argument(
        '-t', '--hipchat-token', help='the HipChat token to authenticate with'
    )
    parser.add_argument(
        '-r', '--hipchat-room', help='the HipChat room to notify'
    )
    parser.add_argument(
        '-p', '--place-ids', help='the IDs of the places to check', nargs='*',
        type=int
    )
    parser.add_argument(
        '-o', '--output', help='the file to write to',
        default=sys.stdout, type=lambda x: open(x, 'w')
    )
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + __version__
    )
    config = parser.parse_args(sys.argv[1:])

    places = load_menu_data(config.source_url)
    places = filter_menu_data(places, config.place_ids)
    for place in places:
        if not place['items']:
            continue

        message = generate_message(place)

        if config.hipchat_token:
            send_hipchat_notification(
                message, config.hipchat_room, config.hipchat_token
            )
        else:
            config.output.write(message + '\n')


if __name__ == '__main__':
    main()
