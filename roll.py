# -*- coding: utf-8 -*-

import sys
import os

from datetime import date
from shutil import copyfile
from itertools import izip

import yaml

from numpy.random import choice


class LunchRoll(object):

    def __init__(self, candidates, abbr):
        self._candidates_yaml = candidates
        with open(self._candidates_yaml, 'rb') as f:
            self._candidates_picked_records = yaml.load(f)
        if not self._record_check():
            print 'WARNING: Candidate records incomplete. Continue? [y/N]'
            to_continue = {'y': True, 'n': False}.get(raw_input().lower(), None) or False
            if not to_continue:
                sys.exit('Exiting..')
        self._abbr_switcher_path = abbr
        with open(self._abbr_switcher_path, 'rb') as f:
            self._abbr_switcher = yaml.load(f)

    def _record_check(self):
        required_record_count = date.today().isoweekday()
        record_count = sum(count for count in self._candidates_picked_records.itervalues())
        if required_record_count == 1:
            if record_count in [0, 1, 4]:
                return True
        if required_record_count in [record_count, record_count + 1]:
            return True
        return False

    def _record(self, pick):
        self._candidates_picked_records[pick] += 1
        self._dump()

    def _backup(self):
        copyfile(self._candidates_yaml, '{}.bak'.format(self._candidates_yaml))

    def _print_candidate_records(self, backup=False):
        to_print = []
        to_print_record = self._candidates_yaml
        if backup:
            to_print_record += '.bak'
        with open(to_print_record, 'rb') as f:
            for line in f:
                to_print.append(line.strip())
        for l in sorted(to_print):
            print '\t', l
        print

    def _dump(self):
        self._backup()
        with open(self._candidates_yaml, 'wb') as f:
            for candidate, picked_times in self._candidates_picked_records.iteritems():
                f.write('{}: {}\n'.format(candidate.encode('utf-8'), picked_times))

    def roll(self):
        if date.today().isoweekday() == 1:
            print 'Happy Monday! Initiating candidate records..'
            self._candidates_picked_records = {k: 0 for k in self._candidates_picked_records.iterkeys()}
            self._dump()

        probability = []
        num_candidates = len(self._candidates_picked_records)
        for candidate, picked_time in sorted(self._candidates_picked_records.iteritems()):
            probability.append(1 / float(num_candidates) * (0.5 ** picked_time) if picked_time != 0 else 0)
        num_non_picked_candidates = len([prob for prob in probability if prob == 0])
        residual_probability = (1 - sum(probability)) / float(num_non_picked_candidates)
        for i in xrange(len(probability)):
            if probability[i] == 0:
                probability[i] = residual_probability

        pick = choice(sorted(self._candidates_picked_records.iterkeys()), p=probability)
        self._record(pick)
        return pick.encode('utf-8')

    def revert(self):
        print 'The original candidate records:'
        self._print_candidate_records()
        print 'Reverting candidate records...'
        copyfile('{}.bak'.format(self._candidates_yaml), self._candidates_yaml)
        print 'Reverted:'
        self._print_candidate_records()

    def amend(self, candidates_to_amend):
        print 'The original candidate records:'
        self._print_candidate_records()
        to_amend_list = []
        for candidate_abbr in candidates_to_amend:
            candidate = self._revert_abbreviations(candidate_abbr)
            if candidate:
                to_amend_list.append(candidate)
            else:
                print '{} is not a valid abbreviation. Ignored.'.format(candidate_abbr)
        print 'Amending missing record(s): {}'.format(' '.join(to_amend_list).encode('utf-8'))
        for candidate in to_amend_list:
            self._record(candidate)
        print 'Amended:'
        self._print_candidate_records()

    def view(self):
        print 'Candidate records backup:'
        self._print_candidate_records(backup=True)
        print 'Candidate records:'
        self._print_candidate_records()

    def add(self, candidate_names, candidate_quantities, candidate_abbreviations):
        print 'The original candidate records:'
        self._print_candidate_records()
        for candidate_name, candidate_qty, candidate_abbr in izip(
                candidate_names, candidate_quantities, candidate_abbreviations):
            self._candidates_picked_records[candidate_name.decode('utf-8')] = candidate_qty
            with open(self._abbr_switcher_path, 'a') as f:
                f.write('{}: {}'.format(candidate_abbr, candidate_name))
        self._dump()
        print 'Records added:'
        self._print_candidate_records()

    def _revert_abbreviations(self, abbr):
        return self._abbr_switcher.get(abbr)

    def print_switcher(self):
        print 'Abbreviations for candidates:'
        with open(self._abbr_switcher_path, 'rb') as f:
            for line in f:
                print '\t{}'.format(line.strip())


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-r', action='store_true', dest='revert', help='revert to last candidate snapshot')
    parser.add_argument('-a', action='append', dest='amend_candidates', help='amend missing rollings')
    parser.add_argument('-v', dest='view', action='store_true', help='view current candidate records')
    parser.add_argument('-s', '--switcher', dest='switcher', action='store_true',
                        help='show candidate abbreviation switcher')
    parser.add_argument('--add', dest='add_name', action='append',
                        help='(together with add_qty and add_abbr) name of the new candidate being added')
    parser.add_argument('--qty', dest='add_qty', action='append',
                        help='(together with add_name and add_abbr) initial quantity of the new candidate being added')
    parser.add_argument('--abbr', dest='add_abbr', action='append',
                        help='(together with add_name and add_qty) abbreviation of the new candidate being added')
    parser.add_argument('-c', '--candidates', dest='candidates', default='candidates.yaml',
                        help='path to the candidate records yaml file')
    parser.add_argument('-A', '--Abbreviation', dest='abbreviation_file', default='abbr_switcher.yaml',
                        help='path to the abbreviation switcher yaml file')
    _args = parser.parse_args()

    candidate_file = os.path.abspath(_args.candidates)
    if not os.path.isfile(candidate_file):
        sys.exit('Candidates.yaml not found. Exiting.')
    abbr_switcher_file = os.path.abspath(_args.abbreviation_file)
    if not os.path.isfile(abbr_switcher_file):
        sys.exit('Abbr_switcher.yaml not found. Exiting.')

    roller = LunchRoll(candidate_file, abbr_switcher_file)
    if _args.add_name or _args.add_qty:
        if not (_args.add_name and _args.add_qty and _args.add_abbr):
            sys.exit('Please provide both the candidate name and its initial quantity to add it.')
        roller.add(_args.add_name, _args.add_qty, _args.add_abbr)
    if _args.view:
        roller.view()
    if _args.switcher:
        roller.print_switcher()
    if _args.revert:
        roller.revert()
    if _args.amend_candidates:
        roller.amend(_args.amend_candidates)
    if (not _args.view) and (not _args.revert) and (not _args.amend_candidates) and \
            (not _args.add_name) and (not _args.switcher):
        print roller.roll()
    print 'Candidates: reserved all rights to argue with the results.'
