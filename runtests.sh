#!/bin/sh
coverage erase
tox
coverage html --include=simple_history/* --omit=simple_history/tests/*
