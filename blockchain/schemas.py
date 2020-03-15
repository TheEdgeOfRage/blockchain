#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 <pavle.portic@tilda.center>
#
# Distributed under terms of the BSD 3-Clause license.

from decimal import Decimal
from typing import List

from pydantic import BaseModel


class NodeList(BaseModel):
	nodes: List[str]


class Transaction(BaseModel):
	sender: str
	recipient: str
	amount: Decimal
	timestamp: float = None
