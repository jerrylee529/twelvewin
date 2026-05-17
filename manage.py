# -*- coding: utf-8 -*-

import argparse
import datetime
import sys
import unittest

from app import app, db
from app.models import User


def run_tests():
    """Runs the unit tests without coverage."""
    tests = unittest.TestLoader().discover(start_dir='tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    return 0 if result.wasSuccessful() else 1


def create_db():
    """Creates the db tables."""
    with app.app_context():
        db.create_all()


def drop_db():
    """Drops the db tables."""
    with app.app_context():
        db.drop_all()


def create_admin():
    """Creates the admin user."""
    with app.app_context():
        db.session.add(User(
            email="ad@min.com",
            password="admin",
            admin=True,
            confirmed=True,
            confirmed_on=datetime.datetime.now(),
        ))
        db.session.commit()


def runserver(host='127.0.0.1', port=5000):
    app.run(host=host, port=port, debug=False, use_debugger=False, use_reloader=False)


def build_parser():
    parser = argparse.ArgumentParser(description='twelvewin management script')
    subparsers = parser.add_subparsers(dest='command')

    runserver_parser = subparsers.add_parser('runserver', add_help=False)
    runserver_parser.add_argument('-h', '--host', dest='host', default='127.0.0.1')
    runserver_parser.add_argument('-p', '--port', dest='port', type=int, default=5000)
    runserver_parser.add_argument('--help', action='help')

    subparsers.add_parser('test')
    subparsers.add_parser('create_db')
    subparsers.add_parser('drop_db')
    subparsers.add_parser('create_admin')

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == 'runserver':
        runserver(host=args.host, port=args.port)
        return 0
    if args.command == 'test':
        return run_tests()
    if args.command == 'create_db':
        create_db()
        return 0
    if args.command == 'drop_db':
        drop_db()
        return 0
    if args.command == 'create_admin':
        create_admin()
        return 0

    parser.print_help()
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
