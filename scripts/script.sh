#!/bin/sh

export PGUSER="postgres"

psql -c "CREATE DATABASE products"

psql products -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"