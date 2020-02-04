#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from flask import Flask


def init_blueprints(app):
	from .app import app as app_bp
	app.register_blueprint(app_bp, url_prefix='/')


def create_app(package_name=__name__):
	app = Flask(package_name)

	init_blueprints(app)

	return app
