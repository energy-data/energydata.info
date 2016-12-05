#!/bin/bash

datacats reload
datacats paster -d celeryd
cd ckanext-harvest
datacats paster -d harvester gather_consumer
datacats paster -d harvester fetch_consumer
