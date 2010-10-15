#!/bin/bash
# Install scripts
cd
wget http://backpack.invisibleroads.com/scripts.tar.gz
tar xzvf scripts.tar.gz
cd scripts
./setup
cd ..
rm -Rf scripts.tar.gz scripts
export SVN_EDITOR=vim
# Install packages
yum install -y svn vim lush python-setuptools-devel python-pylons python-sqlalchemy gdal-python geos python-imaging numpy scipy python-matplotlib ipython pylint screen gcc
yum update -y
easy_install Shapely
# Install Pycluster
cd
wget http://bonsai.ims.u-tokyo.ac.jp/~mdehoon/software/cluster/Pycluster-1.49.tar.gz
tar xzvf Pycluster-1.49.tar.gz
cd Pycluster-1.49
python setup.py install
cd ..
rm -Rf Pycluster-1.49 Pycluster-1.49.tar.gz
# Install code
cd
svn co http://further-perception.invisibleroads.com/sources fp
cd fp/trunk
./install
cd ../branches/fp

mkdir images
cd images
sftp september.mech.columbia.edu:/home/rhh/Downloads/fp/branches/fp/images
