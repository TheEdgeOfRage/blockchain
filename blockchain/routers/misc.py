#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

from decimal import Decimal

from fastapi import APIRouter

from .. import blockchain, identifier
from ..schemas import Transaction

router = APIRouter()


@router.post('/mine', status_code=200)
async def mine():
	last_block = blockchain.last_block
	proof = blockchain.proof_of_work(last_block)
	blockchain.new_transaction(
		sender='0',
		recipient=identifier,
		amount=Decimal(1),
		timestamp=None,
		mine=True,
	)

	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, previous_hash)

	return {
		'msg': 'New Block Forged',
		'index': block['index'],
		'transactions': block['transactions'],
		'proof': block['proof'],
		'previous_hash': block['previous_hash'],
	}


@router.post('/transactions', status_code=202)
async def create_transaction(request: Transaction):
	blockchain.new_transaction(
		request.sender,
		request.recipient,
		request.amount,
		request.timestamp,
	)

	return {
		'msg': f'Transaction sent'
	}


@router.get('/chain', status_code=200)
async def full_chain():
	return {
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}


@router.get('/identifier', status_code=200)
async def get_identifier():
	return {
		'identifier': identifier
	}
