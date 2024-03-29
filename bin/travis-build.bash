cd
sudo apt-get install python-dev postgresql libpq-dev python-pip python-virtualenv git-core solr-jetty openjdk-8-jdk redis-server python-logilab-common
sudo mkdir -p /usr/lib/ckan/default
sudo chown `whoami` /usr/lib/ckan/default
virtualenv --no-site-packages /usr/lib/ckan/default
. /usr/lib/ckan/default/bin/activate
pip install setuptools==36.1
pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.8.1#egg=ckan'
pip install -r /usr/lib/ckan/default/src/ckan/requirements.txt
cd /usr/lib/ckan/default/src/ckan/
python setup.py develop
deactivate 
. /usr/lib/ckan/default/bin/activate
sudo service postgresql start
psql -c 'create database ckan_default;' -U postgres
sudo mkdir -p /etc/ckan/default
sudo chown -R `whoami` /etc/ckan/
paster make-config ckan /etc/ckan/default/development.ini
sed -i 's/sqlalchemy.url = postgresql:\/\/ckan_default:pass@localhost\/ckan_default/sqlalchemy.url = postgresql:\/\/postgres@localhost\/ckan_default/g' /etc/ckan/default/development.ini
sed -i 's/ckan.site_url =/ckan.site_url = http:\/\/data.laastutabloo.ee/g' /etc/ckan/default/development.ini
sudo sed -i 's/#JETTY_HOST=127.0.0.1/JETTY_HOST=127.0.0.1/g' /etc/default/jetty8
sudo sed -i 's/JETTY_PORT=8080/JETTY_PORT=8983/g' /etc/default/jetty8
sudo service jetty8 restart
sudo mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.bak
sudo ln -s /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
sed -i 's/#solr_url=http:\/\/127.0.0.1:8983\/solr/solr_url=http:\/\/127.0.0.1:8983\/solr/g' /etc/ckan/default/development.ini
ln -s /usr/lib/ckan/default/src/ckan/who.ini /etc/ckan/default/who.ini
cd /usr/lib/ckan/default/src/ckan
paster db init -c /etc/ckan/default/development.ini
cd /usr/lib/ckan/default/src/ckan
paster serve /etc/ckan/default/development.ini &
cd $TRAVIS_BUILD_DIR/ckanext-archiver
pip install -e git+https://github.com/datagovuk/ckanext-report.git#egg=ckanext-report
python setup.py develop
pip install -r requirements.txt
pip install -r dev-requirements.txt
cd $TRAVIS_BUILD_DIR/ckanext-harvest
pip install -r pip-requirements.txt
pip install -r dev-requirements.txt
python setup.py develop
cd $TRAVIS_BUILD_DIR/ckanext-datastorer
pip install -e git+git://github.com/ckan/ckanext-datastorer.git#egg=ckanext-datastorer
pip install -r pip-requirements.txt
pip install nose
pip install mock
pip install factory
python setup.py develop
cd $TRAVIS_BUILD_DIR
pip install pytest
