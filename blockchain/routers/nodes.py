#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

from fastapi import APIRouter

from .. import blockchain
from ..schemas import NodeList

router = APIRouter()


@router.get('/', status_code=200)
async def get_nodes():
	return {
		'nodes': list(blockchain.peers),
	}


@router.get('/{identifier}/balance', status_code=200)
async def get_balance(identifier: str):
	balance = blockchain.get_balance(identifier)
	if balance is None:
		return {
			'msg': 'Chain is not valid',
		}, 500

	return {
		'identifier': identifier,
		'balance': balance,
	}


@router.post('/register', status_code=201)
async def register_nodes(request: NodeList):
	if None in (request.nodes,):
		return {'msg': 'No valid list of nodes'}, 400

	for node in request.nodes:
		blockchain.register_node(node)

	return {
		'msg': 'New peers have been added',
		'peers': list(blockchain.peers),
	}


@router.post('/resolve', status_code=200)
async def consensus():
	replaced = blockchain.resolve_conflicts()

	if replaced:
		message = 'Our chain was replaced'
	else:
		message = 'Our chain is authoritative'

	return {
		'msg': message,
		'chain': blockchain.chain,
	}
