#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from decimal import Decimal
from uuid import uuid4

from flask import Blueprint, request

from .blockchain import Blockchain
from .utils import jsonify


app = Blueprint('app', __name__)
identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
	# We run the proof of work algorithm to get the next proof...
	last_block = blockchain.last_block
	proof = blockchain.proof_of_work(last_block)

	# We must receive a reward for finding the proof.
	# The sender is '0' to signify that this node has mined a new coin.
	blockchain.new_transaction(
		sender='0',
		recipient=identifier,
		amount=Decimal(1),
	)

	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, previous_hash)

	return jsonify({
		'msg': 'New Block Forged',
		'index': block['index'],
		'transactions': block['transactions'],
		'proof': block['proof'],
		'previous_hash': block['previous_hash'],
	}), 200


@app.route('/transactions', methods=['POST'])
def create_transaction():
	sender = request.json.get('sender')
	recipient = request.json.get('recipient')
	amount = request.json.get('amount')
	if None in (sender, recipient, amount):
		return {'msg': 'Missing parameter'}, 400

	index = blockchain.new_transaction(
		sender,
		recipient,
		Decimal(amount),
	)

	return jsonify({
		'msg': f'Transaction will be added to Block {index}'
	}), 201


@app.route('/chain', methods=['GET'])
def full_chain():
	return jsonify({
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}), 200


@app.route('/identifier', methods=['GET'])
def get_identifier():
	return jsonify({
		'identifier': identifier
	})


@app.route('/nodes', methods=['GET'])
def get_nodes():
	return jsonify({
		'nodes': list(blockchain.nodes),
	}), 200


@app.route('/nodes/<identifier>/balance', methods=['GET'])
def get_balance(identifier):
	balance = blockchain.get_balance(identifier)
	if balance is None:
		return jsonify({
			'msg': 'Chain is not valid',
		}), 500

	return jsonify({
		'identifier': identifier,
		'balance': balance,
	}), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
	nodes = request.json.get('nodes')
	if None in (nodes,):
		return {'msg': 'No valid list of nodes'}, 400

	for node in nodes:
		blockchain.register_node(node)

	return jsonify({
		'msg': 'New nodes have been added',
		'total_nodes': list(blockchain.nodes),
	}), 201


@app.route('/nodes/resolve', methods=['POST'])
def consensus():
	replaced = blockchain.resolve_conflicts()

	if replaced:
		message = 'Our chain was replaced'
	else:
		message = 'Our chain is authoritative'

	return jsonify({
		'msg': message,
		'chain': blockchain.chain,
	}), 200
