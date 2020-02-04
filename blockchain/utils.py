#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

import hashlib
import itertools
from multiprocessing import (
	cpu_count,
	Pool,
	Process,
	Queue
)

from flask import current_app, json


def dumps(*args, **kwargs):
	if len(args) == 1:
		data = args[0]
	else:
		data = args

	return json.dumps(
		data,
		use_decimal=True,
		**kwargs,
	)


def jsonify(*args, **kwargs):
	indent = None
	separators = (",", ":")

	if current_app.config["JSONIFY_PRETTYPRINT_REGULAR"] or current_app.debug:
		indent = 2
		separators = (", ", ": ")

	return current_app.response_class(
		dumps(
			*args,
			indent=indent,
			separators=separators,
		) + "\n",
		mimetype=current_app.config["JSONIFY_MIMETYPE"],
	)


def do_pooled_pow(last_proof, last_hash, difficulty):
	queue = Queue()
	with Pool() as p:
		result = p.starmap_async(pool_worker, ((
			queue,
			i,
			last_proof,
			last_hash,
			difficulty,
		) for i in itertools.count()), chunksize=100)

		proof = queue.get()
		result.wait()
		p.terminate()

	return proof


def pool_worker(queue, proof, last_proof, last_hash, difficulty):
	if valid_proof(last_proof, proof, last_hash):
		queue.put(proof)
		return proof

	return None


def do_process_pow(last_proof, last_hash, difficulty):
	queue = Queue()
	processes = [
		Process(
			target=process_worker,
			args=(
				queue,
				last_proof,
				last_hash,
				difficulty,
				step,
			)
		) for step in range(cpu_count())
	]
	for p in processes:
		p.start()

	proof = queue.get()
	for p in processes:
		p.terminate()

	return proof


def process_worker(queue, last_proof, last_hash, difficulty, step):
	proof = step
	while not valid_proof(last_proof, proof, last_hash, difficulty):
		proof += step

	queue.put(proof)

	return


def valid_proof(last_proof, proof, last_hash, difficulty):
	"""
	Validates the Proof

	:param last_proof: <int> Previous Proof
	:param proof: <int> Current Proof
	:param last_hash: <str> The hash of the Previous Block
	:return: <bool> True if correct, False if not.
	"""

	guess = f'{last_proof}{proof}{last_hash}'.encode()
	guess_hash = hashlib.sha256(guess)
	binary_hash = ''.join(format(n, '08b') for n in guess_hash.digest())

	return binary_hash[:difficulty] == '0' * difficulty
