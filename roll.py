# -*- coding: utf-8 -*-

import sys

from datetime import date
from shutil import copyfile
from itertools import izip

import yaml

from numpy.random import choice


class LunchRoll(object):
    def __init__(self, candidates, args):
        self._candidates_yaml = candidates
        with open(self._candidates_yaml, 'rb') as f:
            self._candidates_picked_records = yaml.load(f)
        if date.today().isoweekday() == 1:
            print 'Happy Monday! Initiating candidate records..'
            self._candidates_picked_records = {k: 0 for k in self._candidates_picked_records.iterkeys()}
            self._dump()

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
            candidate = LunchRoll.revert_abbreviations(candidate_abbr)
            if candidate:
                to_amend_list.append(candidate)
            else:
                print '{} is not a valid abbreviation. Ignored.'.format(candidate_abbr)
        print 'Amending missing record(s): {}'.format(' '.join(to_amend_list))
        for candidate in to_amend_list:
            self._record(unicode(candidate, 'utf-8'))
        print 'Amended:'
        self._print_candidate_records()

    def view(self):
        print 'Candidate records backup:'
        self._print_candidate_records(backup=True)
        print 'Candidate records:'
        self._print_candidate_records()

    def add(self, candidate_names, candidate_quantities):
        print 'The original candidate records:'
        self._print_candidate_records()
        for candidate_name, candidate_qty in izip(candidate_names, candidate_quantities):
            self._candidates_picked_records[candidate_name] = candidate_qty
        self._dump()
        print 'Records added:'
        self._print_candidate_records()

    @staticmethod
    def revert_abbreviations(abbr):
        return {
            'Mc': '麦当劳',
            'cp': '土鸡星球',
            'MC': '市场创意',
            'p': '熊猫',
            'js': '就是沙拉',
            'cb': '转角烘焙店',
            'ch': '漆坡里',
        }.get(abbr)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-r', action='store_true', dest='revert',
                        help='revert to last candidate snapshot')
    parser.add_argument('-a', action='append', dest='amend_candidates',
                        help='amend missing rollings')
    parser.add_argument('-v', dest='view', action='store_true')
    parser.add_argument('--add', dest='add_name', action='append')
    parser.add_argument('--qty', dest='add_qty', action='append')
    _args = parser.parse_args()

    roller = LunchRoll('candidates.yaml', _args)
    if _args.add_name or _args.add_qty:
        if not (_args.add_qty and _args.add_qty):
            sys.exit('Please provide both the candidate name and its initial quantity to add it.')
        roller.add(_args.add_name, _args.add_qty)
    if _args.view:
        roller.view()
    if _args.revert:
        roller.revert()
    if _args.amend_candidates:
            roller.amend(_args.amend_candidates)
    if (not _args.view) and (not _args.revert) and (not _args.amend_candidates) and (not _args.add_name):
        print roller.roll()
    print 'Candidates: reserved all rights to argue with the results.'