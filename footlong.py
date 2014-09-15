import sys
import argparse
from datetime import datetime

import requests
import hypchat

__version__ = '0.1.0'


def load_menu_data(source_url):
    return requests.get(source_url).json()


def filter_menu_data(places, filter_ids=None):
    return [
        place for place in places if not filter_ids or place['id'] in filter_ids
    ]


def generate_message(place):
    today = datetime.now().strftime('%Y-%m-%d')

    items = ''.join(
        '<li>{0}</li>'.format(item['itemDescription'])
        for item in place['items'] if item['date'] == today
    )

    return '<strong>{0}:</strong><ul>{1}</ul>'.format(place['name'], items)


def send_hipchat_notification(message, token, rooms):
    hipchat = hypchat.HypChat(token)

    for room_name in rooms:
        room = hipchat.get_room(room_name)
        room.notification(message, color='green', notify=True)


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
        '-r', '--hipchat-rooms', help='the HipChat rooms to notify', nargs='*'
    )
    parser.add_argument(
        '-p', '--place-ids', help='the IDs of the places to check', nargs='*'
    )
    parser.add_argument(
        '-o', '--output', help='the file to write to', default=sys.stdout
    )
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + __version__
    )
    config = parser.parse_args(sys.argv)

    places = load_menu_data(config.source_url)
    places = filter_menu_data(places, config.place_ids)
    for place in places:
        message = generate_message(place)
        if config.hipchat_token:
            send_hipchat_notification(
                message, config.hipchat_token, config.hipchat_rooms
            )
        else:
            with open(config.output, 'w') as output:
                output.write(message) + '\n'


if __name__ == '__main__':
    main()
