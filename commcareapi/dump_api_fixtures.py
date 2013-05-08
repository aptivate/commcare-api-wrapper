#!/usr/bin/env python

import argparse
from commcareapi.comm_care_data import CommCareAPI, CommCareResources
import json


def main():
    parser = argparse.ArgumentParser(description='Dump API data for testing.')
    parser.add_argument('-u', help='username (eg. "user@example.org")', required=True)
    parser.add_argument('-p', help='password', required=True)
    parser.add_argument('-d', help='domain', required=True)

    subparsers = parser.add_subparsers(dest='resource')
    case_parser = subparsers.add_parser('case', help='list cases or get case')
    case_parser.add_argument('uuid', nargs='?', default=None)

    form_parser = subparsers.add_parser('form', help='get form')
    form_parser.add_argument('uuid', nargs='?')

    args = parser.parse_args()

    api = CommCareAPI(args.d, args.u, args.p)
    handler = CommCareResources(api)

    if args.resource == 'case':
        if args.uuid:
            resp = handler.case(args.uuid).case_data
        else:
            resp = [j.case_data for j in handler.list_cases()]

    elif args.resource == 'form':
        assert (args.uuid is not None)
        resp = handler.form(args.uuid).form_data

    else:
        exit(1)

    print json.dumps(resp, indent=4)

if __name__ == '__main__':
        main()
