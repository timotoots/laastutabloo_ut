# Laastutabloo
[![Build Status](https://travis-ci.com/timotoots/laastutabloo.svg?branch=master)](https://travis-ci.com/timotoots/laastutabloo)

This is a joint project between Timo Toots and the Univerity of Tartu.
The project is an art project aiming to show local information about Estonian villages, towns and cities on a wooden display at the Estonian National Museum in Tartu.

Currently the open data of Estonia is scattered around the web in many different servers and data formats which makes it difficult to use many data sources in a single project.
The goal of the team is to use and extend the Comprehensive Knowledge Archive Network (CKAN) to collect, organise and store Estonian open data and make it accessible from one place in a consistent and reliable matter.<br/>
CKAN is a web-based open source management system for the storage and distribution of open data. Its codebase is maintained by Open Knowledge International and it's widely used by governments throughout the world to manage open data.

## Documentation
All the necessary information can be found on the [wiki of this repository.](https://github.com/timotoots/laastutabloo/wiki)

## Project plan
Overview of the project is available [here](https://github.com/timotoots/laastutabloo/wiki/Project-Plan)

## Project structure
Here you can see the approximate structure of the software: ![Laastutabloo structure](https://i.imgur.com/xs6x8BM.jpg)

## Installation Process
Install:

https://docs.ckan.org/en/2.8/maintaining/installing/install-from-package.html

sudo apt-get update

sudo apt-get install -y nginx apache2 libapache2-mod-wsgi libpq5 redis-server git-core

wget http://packaging.ckan.org/python-ckan_2.8-xenial_amd64.deb

sudo dpkg -i python-ckan_2.8-xenial_amd64.deb

sudo apt-get install -y postgresql

sudo -u postgres psql -l

sudo -u postgres createuser -S -D -R -P ckan_default

sudo -u postgres createdb -O ckan_default ckan_default -E utf-8

sudo apt-get install -y solr-jetty

Edit the Jetty configuration file (/etc/default/jetty8 or /etc/default/jetty) and change the following variables:

NO_START=0            # (line 4)

JETTY_HOST=127.0.0.1  # (line 16)

JETTY_PORT=8983       # (line 19)

(?)

sudo service jetty8 restart


sudo apt-get install nodejs

sudo apt-get install npm

If you use the package on the default Ubuntu repositories (eg sudo apt-get install nodejs), the node binary will be called nodejs. This will prevent the CKAN less script to work properly, so you will need to create a link to make it work:

ln -s /usr/bin/nodejs /usr/bin/node

cd into the CKAN source folder (eg /usr/lib/ckan/default/src/ckan ) and run:

$ npm install less@1.7.5 nodewatch

## URL
http://data.laastutabloo.ee
