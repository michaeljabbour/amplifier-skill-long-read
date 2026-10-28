#!/usr/bin/env python3
"""Meaningful local functional checks; no provider calls or production activation."""
import asyncio
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

m=load('long_read',ROOT/'skills/long-read/scripts/long_read.py')
class Gate(unittest.TestCase):
    def test_bounded_resume_returns_exact_late_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source.txt';text=('ordinary filler line\n'*180)+'DistinctiveParser evidence at the end.\n';p.write_text(text)
            j=m.create_job(p,'DistinctiveParser',size=300,overlap=40);m.advance(j,budget=1)
            self.assertFalse(j['complete']);self.assertEqual(j['hits'],[])
            while not j['complete']:m.advance(j,budget=2)
            self.assertTrue(j['hits']);h=j['hits'][0];self.assertEqual(text[h['start']:h['end']],h['text']);self.assertIn('DistinctiveParser',h['text'])
    def test_source_change_and_result_limit_change_stop_resume(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'s.txt';p.write_text('evidence '*200);j=m.create_job(p,'evidence',size=300,overlap=10);m.advance(j,1,3)
            with self.assertRaises(ValueError):m.advance(j,1,8)
            p.write_text('new revision')
            with self.assertRaises(ValueError):m.advance(j,1,3)
    def test_existing_job_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'job.json';m.save(p,{'original':True},exclusive=True)
            with self.assertRaises(FileExistsError):m.save(p,{'original':False},exclusive=True)
            self.assertTrue(json.loads(p.read_text())['original'])
    def test_resume_rejects_retained_evidence_corruption_before_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'s.txt';p.write_text('alpha evidence\n'*100)
            original=m.create_job(p,'alpha',size=200,overlap=10);m.advance(original,1)
            for field,value in [('text','absent fabricated quote'),('start',999),('score',99),('chunk',5)]:
                with self.subTest(field=field):
                    job=copy.deepcopy(original);job['hits'][0][field]=value
                    prior=copy.deepcopy(job)
                    with self.assertRaises(ValueError):m.advance(job,1)
                    self.assertEqual(prior,job)

if __name__=='__main__':unittest.main(verbosity=2)
