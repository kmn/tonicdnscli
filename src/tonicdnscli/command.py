#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Copyright (C) 2012 Kouhei Maeda <mkouhei@palmtb.net>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


# Check text file exisitense
def checkInfile(filename):
    import os.path
    import sys
    if os.path.isfile(filename):
        domain = os.path.basename(filename).split('.txt')[0]
        return domain
    else:
        sys.stderr.write("ERROR: %s : No such file\n" % filename)
        sys.exit(1)


# Convert text file to JSON
def getJSON(domain, filename, act):
    import converter
    o = converter.JSONConvert(domain)
    with open(filename, 'r') as f:
        o.separateInputFile(f)
    for listitem in o.separated_list:
        o.readRecords(listitem.splitlines())
        o.genData(act)
    return o.dict_records


# get token
def token(username, password, server):
    from tdauth import authInfo
    a = authInfo(username, password, server)
    a.getToken()
    return a.token


# get password
def getPassword(args):
    password = ''
    if args.password:
        password = args.password
    elif args.P:
        while True:
            if password:
                break
            else:
                from getpass import getpass
                password = getpass(prompt='TonicDNS user password: ')
    return password


# Convert and print JSON
def show(args):
    import json
    domain = checkInfile(args.infile)
    print(json.dumps(getJSON(domain, args.infile, True),
                     sort_keys=True, indent=2))


# Retrieve records
def get(args):
    import processing
    domain = args.domain
    password = getPassword(args)
    t = token(args.user, password, args.server)
    processing.getZone(args.server, t, domain)


# Create records
def create(args):
    import processing
    domain = checkInfile(args.infile)
    password = getPassword(args)
    t = token(args.user, password, args.server)
    processing.createRecords(args.server, t, domain,
                             getJSON(domain, args.infile, True))


# Delete records
def delete(args):
    import processing
    domain = checkInfile(args.infile)
    password = getPassword(args)
    t = token(args.user, password, args.server)
    processing.deleteRecords(args.server, t,
                             getJSON(domain, args.infile, False))


# Define sub-commands and command line options
def parse_options():
    import argparse
    from __init__ import __version__

    parser = argparse.ArgumentParser(description='usage')

    parser.add_argument('-v', '--version', action='version',
                        version=__version__)

    subparsers = parser.add_subparsers(help='commands')

    # Convert and print JSON
    parser_show = subparsers.add_parser('show',
                                         help='show converted JSON')
    parser_show.add_argument('infile', action='store',
                               help='pre-converted text file')
    parser_show.set_defaults(func=show)

    # Retrieve records
    parser_get = subparsers.add_parser(
        'get', help='retrieve records of specific zone')
    parser_get.add_argument('--domain', action='store', required=True,
                            help='specify domain FQDN')
    parser_get.add_argument(
        '-s', dest='server', required=True,
        help='specify TonicDNS Server hostname or IP address')
    parser_get.add_argument('-u', dest='user', required=True,
                           help='TonicDNS username')
    group_get = parser_get.add_mutually_exclusive_group(required=True)
    group_get.add_argument('-p', dest='password',
                           help='TonicDNS password')
    group_get.add_argument('-P', action='store_true',
                            help='TonicDNS password prompt')
    parser_get.set_defaults(func=get)

    # Create records
    parser_create = subparsers.add_parser(
        'create', help='create records of specific zone')
    parser_create.add_argument('infile', action='store',
                                 help='pre-converted text file')
    parser_create.add_argument('-s', dest='server', required=True,
                               help='specify TonicDNS hostname or IP address')
    parser_create.add_argument('-u', dest='user', required=True,
                               help='TonicDNS username')
    group_create = parser_create.add_mutually_exclusive_group(required=True)
    group_create.add_argument('-p', dest='password',
                               help='TonicDNS password')
    group_create.add_argument('-P', action='store_true',
                               help='TonicDNS password prompt')
    parser_create.set_defaults(func=create)

    # Delete records
    parser_delete = subparsers.add_parser(
        'delete', help='delete records of specific zone')
    parser_delete.add_argument('infile', action='store',
                                 help='pre-converted text file')
    parser_delete.add_argument('-s', dest='server', required=True,
                               help='specify TonicDNS hostname or IP address')
    parser_delete.add_argument('-u', dest='user', required=True,
                               help='TonicDNS username')
    group_delete = parser_delete.add_mutually_exclusive_group(required=True)
    group_delete.add_argument('-p', dest='password',
                               help='TonicDNS password')
    group_delete.add_argument('-P', action='store_true',
                               help='TonicDNS password prompt')
    parser_delete.set_defaults(func=delete)

    args = parser.parse_args()
    return args


def main():
    import sys

    try:
        args = parse_options()
        args.func(args)
    except RuntimeError as e:
        sys.stderr.write("ERROR: %s\n" % e)
        return
    except UnboundLocalError as e:
        sys.stderr.write("ERROR: %s\n" % e)
        return

if __name__ == "__main__":
    main()
