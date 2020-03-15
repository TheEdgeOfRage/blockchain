#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from uuid import uuid4

from fastapi import FastAPI

from .blockchain import Blockchain

blockchain = Blockchain()
identifier = str(uuid4()).replace('-', '')


def init_routers(app):
	from .routers import misc
	app.include_router(
		misc.router,
		prefix='',
		tags=['misc'],
	)

	from .routers import nodes
	app.include_router(
		nodes.router,
		prefix='/nodes',
		tags=['nodes'],
	)


def create_app():
	app = FastAPI()
	init_routers(app)

	return app
