#!/bin/bash

cp ./billmgr_mod_testpayment.xml /usr/local/mgr5/etc/xml/
/usr/local/mgr5/sbin/mgrctl -m billmgr -R
