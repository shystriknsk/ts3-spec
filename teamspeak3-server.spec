
# How to create a Teamspeak3 server *.rpm with the help of this .spec file
# on Fedora, CentOS 5, 6 or 7:

# 1. install packages for rpm build environment:
#    $ sudo yum install rpm-build rpmdevtools redhat-rpm-config
# 2. login as non-root user and call:
#    $ rpmdev-setuptree
# 3. save this *.spec file to ~/rpmbuild/SPECS
# 4. This *.spec file was created for version 3.0.13.8. If you want to package
#    a different version, change the "version: " number below.
# 5. download the original teamspeak3-server_linux-*.tar.gz from
#    http://www.teamspeak.com/?page=downloads and save it to ~/rpmbuild/SOURCES
#    You can also use spectool to download the correct file directly:
#    $ spectool -g -R teamspeak3-server.spec
# 6. build the rpm:
#    $ rpmbuild -bb teamspeak3-server.spec
# 7. On x86_64 architecture, the *.rpm is created as:
#    ~/rpmbuild/RPMS/x86_64/teamspeak3-server-3.0.13.8-1.el7.centos.x86_64.rpm
#    Two additional packages are created:
#      teamspeak3-server-mariadb-3.0.13.8-1.el7.centos.x86_64.rpm (mariadb support)
#      teamspeak3-server-backup-3.0.13.8-1.el7.centos.noarch.rpm  (daily backup)

# How to perform the server installation with this *.rpm:
# On Fedora 18+ or CentOS 7:
#   1. Install:
#      $ sudo yum install teamspeak3-server-3.0.13.8-1.el7.centos.x86_64.rpm
#   2. open firewall (assuming you are using firewalld):
#      $ sudo firewall-cmd --permanent --add-service=teamspeak3-server
#      $ sudo firewall-cmd --reload
#   3. set the server to autostart:
#      $ sudo systemctl enable teamspeak3-server
#   4. start the server:
#      $ sudo systemctl start teamspeak3-server

# On CentOS 5 or 6:
#   1. Install:
#      $ sudo yum install teamspeak3-server-3.0.13.8-1.el6.x86_64.rpm
#   2. add firewall rules to /etc/sysconfig/iptables (see README.install)
#   3. set the server to autostart:
#      $ sudo chkconfig teamspeak3 on
#   4. start the server:
#      $ sudo service start teamspeak3

# Please consult the documentation in /usr/share/doc/teamspeak3-server-3.0.13.8.
# See README.install with general information about configuring and running the
# server.

Name: teamspeak3-server
Version: 3.13.7
Release: 1
Summary: TeamSpeak 3 Server

Group: Applications/Internet
License: Teamspeak, see http://sales.teamspeakusa.com/licensing.php
URL: http://www.teamspeak.com/

%ifarch x86_64
  %define __tgzarch amd64
%else
  %define __tgzarch x86
%endif

# define variables that must exist
%{?!fedora:%define fedora 0}
%define use_systemd 0
%if 0%{?rhel} == 7
%define fedora 19
%endif

# sysv init or systemd
%if 0%{?fedora} >= 18
%define use_systemd 1
%endif

%define __data         %{_datadir}/%{name}
%define __dbdir        %{_localstatedir}/lib/teamspeak3
%define __etc          %{_sysconfdir}/teamspeak3
%define __libdir       %{_libdir}/%{name}
%define __tsdnsbin     tsdnsserver
%define __ts3serverbin ts3server
%define __user         teamspeak3
%define _firewallddir  %{_usr}/lib/firewalld/services

Source: https://files.teamspeak-services.com/releases/server/%{version}/%{name}.tar.bz2

Requires: logrotate
%if %{use_systemd}
%systemd_requires
BuildRequires: systemd
%else
Requires(post): /sbin/service /sbin/chkconfig
Requires(preun): /sbin/service /sbin/chkconfig
Requires(postun): /sbin/service
%endif

Requires(pre): shadow-utils

%description
TeamSpeak enables people to speak with one another over the Internet.
TeamSpeak is flexible, powerful, scalable client-server software which
results in an Internet based conferencing solution which facilitates
communication between users. This package contains the server.

%package mariadb
Summary: MariaDB support for the Teamspeak 3 server
Group: Applications/Internet
Requires: teamspeak3-server
%description mariadb
MariaDB support for the Teamspeak 3 server.

%package backup
Summary: Scripts for backing up the Teamspeak 3 server
Group: Applications/Internet
License: Public Domain
BuildArch: noarch
Requires: teamspeak3-server, nc
Requires: sqlite >= 3.0
%description backup
Contributed scripts and a cron job to backup the Teamspeak server database and
create snapshots of all virtual server instances on a daily basis.

# no debug package for precompiled binaries
%global debug_package %{nil}

%prep
# extract *.tar.gz
%setup -n %{name}_%{_target_os}_%{__tgzarch} -q

# change documentation encoding to UTF8 and preserve timestamp
#for i in doc/*.txt LICENSE CHANGELOG; do
#  iconv -f CP1250 -t UTF8 "$i" -o "$i.new"
#  touch -r "$i" "$i.new"
#  mv -f "$i.new" "$i"
#done

%install

# create directories
%if %{use_systemd}
%{__install} -d -m 0755 %{buildroot}%{_unitdir}
%{__install} -d -m 0755 %{buildroot}%{_firewallddir}
%else
%{__install} -d -m 0755 %{buildroot}%{_initrddir}
%{__install} -d -m 0755 %{buildroot}%{_localstatedir}/run/teamspeak3
%endif
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/cron.d
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/ld.so.conf.d
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -d -m 0755 %{buildroot}%{_localstatedir}/log/teamspeak3
%{__install} -d -m 0755 %{buildroot}%{__libdir}
%{__install} -d -m 0755 %{buildroot}%{__etc}
%{__install} -d -m 0755 %{buildroot}%{__data}
%{__install} -d -m 0750 %{buildroot}%{__dbdir}
%{__install} -d -m 0750 %{buildroot}%{__dbdir}/backups
%{__install} -d -m 0750 %{buildroot}%{__dbdir}/snapshots

# install files
%{__cp} -a serverquerydocs/ sql/ %{buildroot}%{__data}
%{__cp} -a tsdns/tsdns_settings.ini.sample %{buildroot}%{__etc}/tsdns_settings.ini
%{__install} -m 0755 -p tsdns/%{__tsdnsbin} %{buildroot}%{_bindir}
%{__install} -m 0755 -p %{__ts3serverbin} %{buildroot}%{_bindir}
%{__install} -m 0755 -p libts3db_mariadb.so %{buildroot}%{__libdir}
%{__install} -m 0755 -p libts3db_sqlite3.so %{buildroot}%{__libdir}
%{__install} -m 0755 -p libts3_ssh.so %{buildroot}%{__libdir}
%{__install} -m 0755 -p redist/libmariadb.so* %{buildroot}%{__libdir}
%{__ln_s} %{__data}/serverquerydocs %{buildroot}%{__dbdir}/serverquerydocs
%{__rm} -f tsdns/%{__tsdnsbin}


# create ldconfig configuration for the TS3 libraries
cat <<"EOF" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
%{__libdir}
EOF

# create default ts3server.ini
cat <<"EOF" > %{buildroot}%{__etc}/ts3server.ini
default_voice_port=9987
filetransfer_port=30033
query_port=10011
dbplugin=ts3db_sqlite3
dbpluginparameter=
dbsqlpath=%{__data}/sql/
dbsqlcreatepath=create_sqlite/
query_ip_whitelist=%{__etc}/query_ip_whitelist.txt
query_ip_blacklist=%{__etc}/query_ip_blacklist.txt
logpath=%{_localstatedir}/log/teamspeak3
logquerycommands=1
logappend=1
dbclientkeepdays=365
dblogkeepdays=365
EOF


# create default ts3server.ini.mariadb, in case you want to use mariadb
cat <<"EOF" > %{buildroot}%{__etc}/ts3server.ini.mariadb
default_voice_port=9987
filetransfer_port=30033
query_port=10011
dbplugin=ts3db_mariadb
dbpluginparameter=%{__etc}/ts3db_mariadb.ini
dbsqlpath=%{__data}/sql/
dbsqlcreatepath=create_mariadb/
query_ip_whitelist=%{__etc}/query_ip_whitelist.txt
query_ip_blacklist=%{__etc}/query_ip_blacklist.txt
logpath=%{_localstatedir}/log/teamspeak3
logquerycommands=1
logappend=1
dbclientkeepdays=365
dblogkeepdays=365
EOF

# create default ts3db_mariadb.ini, in case you want to use mariadb
cat <<"EOF" > %{buildroot}%{__etc}/ts3db_mariadb.ini
[config]
host=localhost
port=3306
username=teamspeak
password=__PASSWORD__
database=ts3db
socket=
EOF

# create default whitelist with local addresses
cat <<"EOF" > %{buildroot}%{__etc}/query_ip_whitelist.txt
127.0.0.1
EOF

# create default blacklist (empty)
cat <<"EOF" > %{buildroot}%{__etc}/query_ip_blacklist.txt

EOF

# create default snapshot logon data
cat <<"EOF" > %{buildroot}%{__etc}/snapshot
#user="__QUERYADMIN__"
#pass="__PASSWORD__"
file="%{__dbdir}/snapshots/%%i/ts3-snapshot-%%i-`date +%%Y%%m%%d-%%H%%M%%S`.txt"
EOF

# create logrotate configuration
cat <<"EOF" > %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{_localstatedir}/log/teamspeak3/ts3server_*.log {
    monthly
    rotate 6
    copytruncate
    compress
    notifempty
    missingok
}
EOF

# create README.install
cat <<"EOF" > README.install
===============================================================================
Teamspeak 3 server rpm installation

Written by Alex Woick <alex@wombaz.de> 2012-02-22
Last updated: 2016-03-15

Contents:

1. OVERVIEW
2. OPEN FIREWALL PORTS
3. INSTALL TEAMSPEAK LICENSE
4. DIRECTORIES AND FILES
5. BACKUP YOUR SERVER
6. TSDNSSERVER
7. SRV DNS RECORDS
8. QUERY ADMIN PASSWORD RESET

===============================================================================
1. OVERVIEW

This rpm install of the Teamspeak server distributes the files from the
original *.tar.gz distribution into fhs-conformant destination directories.
It also comes with an enhanced startup file for SYSV init systems or systemd
unit files for Fedora 18+/RHEL 7+/CentOS 7+. It creates directories for the
database, for logfiles and for the ts3server.ini including blacklist and
whitelist files. It contains a working ts3server.ini, which can be customized
according to your needs.

The user %{__user} is created, which is used to run the Teamspeak server.

After installation, the server is ready to be started right away. It will run
out of the box with the default sqlite database.

To activate autostart and start the Teamspeak server, call:

%if %{use_systemd}
  $ sudo systemctl --now enable teamspeak3-server
%else
  $ sudo chkconfig teamspeak3 on
  $ sudo service teamspeak3 start
%endif

If you want that your server is reachable from remote, it is required to open
some ports in the firewall of the Teamspeak server machine. See Chapter 2 on
how to do this.

If you want that your server uses MariaDB as database, install the package
teamspeak3-server-mariadb and use the supplied ts3server.ini.mariadb instead
of ts3server.ini. Note that the default Sqlite database is sufficient for
standalone machines of any size. Only ATHPs will benefit from MariaDB.

IMPORTANT:
%if %{use_systemd}
After starting the Teamspeak server for the first time, call this command to
extract the query admin password and the server admin token from the journal:

  $ journalctl -u teamspeak3-server.service

Store the information in a safe place for later use. If you also installed the
package teamspeak3-server-backup, call get-query-admin.sh to extract the query
admin password and add it to the snapshot configuration in %{__etc}/snapshot.
%else
Check the file %{__dbdir}/query-admin-password.txt after server start.
It contains the query admin password and the server admin token after the
server has been started successfully for the first time. Get the file and store
it in a safe place for later use. Don't leave it openly on the server!
%endif

To get administrator access to the new server, use the token with your
Teamspeak client when you connect to the server for the first time. The
Teamspeak client will ask for it when you connect to a new server for the first
time.

===============================================================================
2. OPEN FIREWALL PORTS

2.1. Allow incoming connections

2.1.1. iptables

The iptables firewall configuration is in the file /etc/sysconfig/iptables.
Find the appropriate location for adding new port openings, for example where
port 22 for ssh or port 80 for http traffic is opened. Right after those
existing rules, but before any global REJECT rule or the closing COMMIT rule,
add the following rules for the Teamspeak server:

-A INPUT -m state --state NEW -m tcp -p tcp --dport 10011 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 30033 -j ACCEPT
-A INPUT -m state --state NEW -m udp -p udp -m multiport --dports 9987:9988 -j ACCEPT

In case you add more virtual servers, for example you create 10 virtual servers
which use the ports 9987..9997, modify the last rule accordingly:

-A INPUT -m state --state NEW -m udp -p udp -m multiport --dports 9987:9997 -j ACCEPT

This is an example for a complete firewall configuration that only allows ssh
and Teamspeak access:

*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
-A INPUT -p icmp -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 22 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 10011 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 30033 -j ACCEPT
-A INPUT -m state --state NEW -m udp -p udp -m multiport --dports 9987:9988 -j ACCEPT
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
COMMIT

%if %{use_systemd}
2.1.2. firewalld

This package comes with service definitions for the Teamspeak and tsdns server.
Enable Teamspeak service:

  $ sudo firewall-cmd --permanent --add-service=teamspeak3-server
  $ sudo firewall-cmd --reload

%endif

2.2. Outgoing connections

If you run a restrictive firewall that also filters outgoing traffic, it is
required to allow outgoing TCP connections to accounting.teamspeak.com:2008.
If you want weblist support, additionally allow outgoing UDP traffic on port
2010.


2.3. Port forwarding

If you run your server at home behind a router and want access from the
internet, it is required that you forward the Teamspeak ports on your router to
the Teamspeak server in your local network. Forward these ports on your router
to the local IP address of your Teamspeak server machine:

TCP 10011  # query port [only required for query admin access]
TCP 30033  # file transfer port
UDP 9987   # voice port (in case of more virtual servers: add every voice port)

===============================================================================
3. INSTALL TEAMSPEAK LICENSE

Please note that Teamspeak kindly allows operating a server without a license
for noncommercial use. Simply use the server without licence file, if you fit
Teamspeak's definition for noncommercial use and if you don't need more than 32
slots.

But if you require a license and have one, copy your Teamspeak license file
licensekey.dat into %{__dbdir} and adjust ownership and permissions:

  $ sudo -i
  $ cd %{__dbdir}
  $ cp -p /original-path-to-your-licensekey/licensekey.dat .
  $ chown %{__user}:%{__user} licensekey.dat
  $ chmod 640 licensekey.dat
%if %{use_systemd}
  $ systemctl restart teamspeak3-server
%else
  $ service teamspeak3 restart
%endif
  $ exit

It is very important to chown the license file to the Teamspeak user, so the
server is able to update the file to renew the license before it expires. If
the server is not able to update the license file, the license will expire and
you will have to contact Teamspeak to get a new one.

===============================================================================
4. DIRECTORIES AND FILES

Documentation:
%{_docdir}/%{name}-%{version}

Server Configuration:
%{__etc}/ts3server.ini
%{__etc}/query_ip_blacklist.txt
%{__etc}/query_ip_whitelist.txt

# stored query admin username and password for snapshot backup operations
%{__etc}/snapshot

Startup options, optionally to be created manually:
%{_sysconfdir}/sysconfig/teamspeak3

%if %{use_systemd}
Unit files:
%{_unitdir}/teamspeak3-server.service
%{_unitdir}/tsdns-server.service
%else
Startup script:
%{_initrddir}/teamspeak3
%{_initrddir}/tsdnsserver
%endif

Teamspeak database directory:
%{__dbdir}

Log file directory:
%{_localstatedir}/log/teamspeak3

%if %{use_systemd} == 0
Pid file (used by the startup script):
%{_localstatedir}/run/teamspeak3/ts3server.pid
%endif
SQL scripts and query admin help files:
%{__data}

Server and tools binary:
%{_bindir}/%{__ts3serverbin}
%{_bindir}/%{__tsdnsbin}
%{_bindir}/ts3snapshot     (create and deploy virtual server snapshots)
%{_bindir}/ts3backup_cron  (cron job for snapshots and database backup)

Database plugins and libraries:
%{__libdir}/libts3db_mariadb.so
%{__libdir}/libts3db_sqlite3.so

===============================================================================
5. BACKUP YOUR SERVER

The optional package teamspeak3-server-backup installs a cron job that creates
snaphots for every virtual server instance once a day. It's highly recommended,
if you don't do your own instance backup.
Snapshot and backup files older than 60 days are removed automatically.

The snapshot creation script uses the query admin login credentials from
%{__etc}/snapshot.
%if %{use_systemd}
After the first start of the Teamspeak server, call:

  $ get-query-admin.sh

This will extract the query admin password from the journal and store it in
%{__etc}/snapshot.
%endif
If the credentials have not been entered automatically, edit the file manually.

Snapshots are stored here with a subdirectory for each server instance:
%{__dbdir}/snapshots

If you want to restore or deploy a virtual server with one of the snaphot
files, call:

  $ ts3snapshot deploy -i <instance> -f %{__dbdir}/snapshots/<instance>/ts3-snapshot-<instance>-<date>.txt

The backup files are stored in this location:
%{__dbdir}/backups

Additionally, you should backup the following files regularly to be able to
restore your server:

%{__dbdir}/files/*
%{__dbdir}/licensekey.dat (in case you have a license installed)
%{__dbdir}/serverkey.dat
%{__dbdir}/ts3server.sqlitedb
%{__etc}/snapshot
%{__etc}/ts3server.ini
%{__etc}/query_ip_blacklist.txt
%{__etc}/query_ip_whitelist.txt
%{_sysconfdir}/sysconfig/teamspeak3

If you need to restore the Teamspeak server database, stop the Teamspeak server
and copy one of the datase backup files over the existing database:

%if %{use_systemd}
  $ systemctl stop teamspeak3-server
  $ cd %{__dbdir}
  $ cp backups/ts3server.sqlitedb.YYYYMMDD-HHMMDD ts3server.sqlitedb
  $ systemctl start teamspeak3-server
%else
  $ service teamspeak3 stop
  $ cd %{__dbdir}
  $ cp backups/ts3server.sqlitedb.YYYYMMDD-HHMMDD ts3server.sqlitedb
  $ service teamspeak3 start
%endif

There is an important difference between database backups and snapshots:

A snapshot always contains one single virtual server instance. If you need to
move one virtual server instance from one host to another, or if you need to
copy one virtual server to another instance or host, create and deploy a
snapshot.
There is one caveat with using snapshots: the connection between uploaded
channel files and the actual channel is lost. It is lost even if you restore
a virtual server on the same host, since all server objects (channels, groups
and users) get new id numbers.

A database backup always contains the whole server with every virtual server
instance. Restoring a database backup always restores every virtual server. It
is not possible to restore a single server instance by using a database backup.
In contrast to snapshots, the connection between uploaded channel files and the
channels is not lost. If you restore a server, uploaded files remain
accessible.

===============================================================================
6. TSDNSSERVER

A start script for tsdnsserver is installed as well. To activate autostart and
start tsdnsserver, call:

%if %{use_systemd}
  $ sudo systemctl --now enable tsdns-server
%else
  $ sudo chkconfig tsdnsserver on
  $ sudo service tsdnsserver start
%endif

The configuration is in %{__etc}/tsdns_settings.ini. After you change the
configuration, restart the server:

%if %{use_systemd}
  $ sudo systemctl reload tsdns-server
%else
  $ sudo service tsdnsserver restart
%endif

It you use tsdnsserver, you need to open port 41144 in your firewall:

%if %{use_systemd}
  $ sudo firewall-cmd --permanent --add-service=tsdns-server
  $ sudo firewall-cmd --reload
else
-A INPUT -m state --state NEW -m tcp -p tcp --dport 41144 -j ACCEPT
%endif

Usually, you will not want to use tsdnsserver but use SRV dns records instead.

===============================================================================
7. SRV DNS RECORDS

If you want that your users connect to your server by using a simple hostname,
you may want to create SRV records for your virtual Teamspeak instances if
you have control over your domains' DNS. No more cryptic IP address or port
number for your users.

In this example, you want to support 4 clans called clanalpha, clanbeta,
clangamma and clandelta and give them individual Teamspeak hostnames like
clanalpha.example.org.

You collect these prerequisites:
- your server machine has an IP address of 1.2.3.4
- your server machine has the hostname www.example.org
- Teamspeak server is installed on this server machine
- you configured 4 Teamspeak server instances on ports 9987, 9988, 9989, 9990
- you can already connect successfully to the instances by using 1.2.3.4:9987
  or www.example.org:9987 as connection data.
- you are able to configure SRV records in your domain example.org

You plan these assignments:

IP-address=hostname      port  Teamspeak-hostname
1.2.3.4=www.example.org  9987  clanalpha.example.org
1.2.3.4=www.example.org  9988  clanbeta.example.org
1.2.3.4=www.example.org  9989  clangamma.example.org
1.2.3.4=www.example.org  9990  clandelta.example.org

Now you create the following SRV records into your dns zone for example.org:

$ORIGIN example.org.
_ts3._udp.clanalpha 3600  SRV  10 5 9987 www.example.org.
_ts3._udp.clanbeta  3600  SRV  10 5 9988 www.example.org.
_ts3._udp.clangamma 3600  SRV  10 5 9989 www.example.org.
_ts3._udp.clandelta 3600  SRV  10 5 9990 www.example.org.

To verify that these entries are active in the dns, enter these commands:

For clanalpha:

  $ dig srv _ts3._udp.clanalpha.example.org +short

Expected output:
10 5 9987 www.example.org.

For clanbeta:

  $ dig srv _ts3._udp.clanbeta.example.org +short

Expected output:
10 5 9988 www.example.org.

etc.

If there is no output, the entries are not active.

From now on, your clanalpha users can connect to your Teamspeak servers by
simply connecting to clanalpha.example.org without port number. Your clanbeta
users use clanbeta.example.org, and so on.

If you move your Teamspeak server away from your web server, for example to
ts.example.org on 1.2.3.5, you only need to change your SRV records:

$ORIGIN example.org.
_ts3._udp.clanalpha 3600  SRV  10 5 9987 ts.example.org.
_ts3._udp.clanbeta  3600  SRV  10 5 9988 ts.example.org.
_ts3._udp.clangamma 3600  SRV  10 5 9989 ts.example.org.
_ts3._udp.clandelta 3600  SRV  10 5 9990 ts.example.org.

Your users don't need to change anything.

Even if you run your Teamspeak server at home and use a dynamic hostname for
it, for example "mytsathome.dyndns.org", it is possible to hide the dynamic
hostname for your Teamspeak users. The only thing you need is control over your
domain example.org. This scenario applies if you only have rented webspace
with your own domain, but without the possibility of installing the Teamspeak
server on the webspace.

$ORIGIN example.org.
_ts3._udp.clanalpha 3600  SRV  10 5 9987 mytsathome.dyndns.org.
_ts3._udp.clanbeta  3600  SRV  10 5 9988 mytsathome.dyndns.org.
_ts3._udp.clangamma 3600  SRV  10 5 9989 mytsathome.dyndns.org.
_ts3._udp.clandelta 3600  SRV  10 5 9990 mytsathome.dyndns.org.

Your users still use clanalpha.example.org, clanbeta.example.org, etc. to
connect to your Teamspeak server.

===============================================================================
8. QUERY ADMIN PASSWORD RESET

To reset the query admin password without restarting the Teamspeak server,
simply call the contributed script /usr/bin/ts3-reset-query-admin.sh.
It creates a new random serveradmin password, sets this password in the
Teamspeak database, and prints it to stdout.

If you want to do this manually to have control over the process, use these
commands:

$ echo -n 'the!New1Password2' | openssl dgst -binary -sha1 | openssl base64
kUOY5N1LFgSOVsKq689XHdYtJnQ=

$ sqlite3 ts3server.sqlitedb
sqlite> UPDATE clients SET client_login_password='kUOY5N1LFgSOVsKq689XHdYtJnQ=' WHERE
        client_login_name='serveradmin';

This is not an officially supported way to reset the password, but it works
nonetheless.
EOF

%if %{use_systemd}
# create teamspeak3-server unit file for systemd
cat <<"EOF" > %{buildroot}%{_unitdir}/teamspeak3-server.service
[Unit]
Description=TeamSpeak 3 Server
Documentation=file:/%{_docdir}/%{name}-%{version}/README.install
After=nss-lookup.target network.target

[Service]
User=%{__user}
UMask=0027
WorkingDirectory=%{__dbdir}
ExecStart=%{_bindir}/%{__ts3serverbin} inifile=%{__etc}/ts3server.ini
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# create tsdns-server unit file for systemd
cat <<"EOF" > %{buildroot}%{_unitdir}/tsdns-server.service
[Unit]
Description=TeamSpeak 3 TSDNS Server
Documentation=file:/%{_docdir}/%{name}-%{version}/README.install
After=network.target

[Service]
User=%{__user}
WorkingDirectory=%{__etc}
ExecStart=%{_bindir}/%{__tsdnsbin}
ExecReload=%{_bindir}/%{__tsdnsbin} --update
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# create teamspeak server service file for firewalld
cat <<"EOF" > %{buildroot}%{_firewallddir}/teamspeak3-server.xml
<?xml version="1.0" encoding="utf-8"?>
<service>
  <short>Teamspeak 3 Server</short>
  <description>TeamSpeak enables people to speak with one another over the Internet.</description>
  <port protocol="udp" port="9987-9999"/>
  <port protocol="tcp" port="10011"/>
  <port protocol="tcp" port="30033"/>
</service>
EOF

# create tsdns server service file for firewalld
cat <<"EOF" > %{buildroot}%{_firewallddir}/tsdns-server.xml
<?xml version="1.0" encoding="utf-8"?>
<service>
  <short>Teamspeak 3 TSDNS Server</short>
  <description>TSDNS for Teamspeak enables Teamspeak-specific name resolution services.</description>
  <port protocol="tcp" port="41144"/>
</service>
EOF

cat <<"EOF" > %{buildroot}%{_bindir}/get-query-admin.sh
#!/bin/sh
# Read the Teamspeak 3 query admin password from the journal and write it to
# %{__etc}/snapshot, which is used by the database backup
# utility script.

test -f %{__etc}/snapshot || exit 0
grep -q "#user=\"__QUERYADMIN__\"" %{__etc}/snapshot || exit 0

journalctl -u teamspeak3-server.service | grep -o "loginname= .*" |
while read -r kwuser queryadmin kwpass password; do
  sed -i "s/#\?user=\".*\"/user=${queryadmin%,}/g" %{__etc}/snapshot
  sed -i "s/#\?pass=\".*\"/pass=$password/g" %{__etc}/snapshot
done
EOF

%else

# create server startup script
cat <<"EOF" > %{buildroot}%{_initrddir}/teamspeak3
#!/bin/sh

# teamspeak3 Startup script written by Alex Woick <alex@wombaz.de> 2012-02-22

# chkconfig: - 95 5
# description: TeamSpeak 3 Server
# processname: %{__ts3serverbin}
# config: %{_sysconfdir}/sysconfig/teamspeak3
# pidfile: %{_localstatedir}/run/teamspeak3/ts3server.pid

# TeamSpeak 3
# Copyright TeamSpeak Systems GmbH
# http://www.teamspeak.com

# Source function library.
. /etc/rc.d/init.d/functions

exec=%{_bindir}/%{__ts3serverbin}
prog=$(basename $exec)
config=%{__etc}/ts3server.ini
snapconf=%{__etc}/snapshot
dbdir=%{__dbdir}
pidfile=%{_localstatedir}/run/teamspeak3/ts3server.pid
ts3user=%{__user}

[ -e %{_sysconfdir}/sysconfig/teamspeak3 ] && . %{_sysconfdir}/sysconfig/teamspeak3

lockfile=%{_localstatedir}/lock/subsys/teamspeak3

start() {

  [ -x $exec ] || exit 5
  [ -f $config ] || exit 6
  [ -f "$pidfile" ] && checkpid `cat $pidfile` && return 0

  # check if tmpfs is mounted, add entry to fstab if necessary
  if ! mount|grep -q "/dev/shm"; then
    mount -t tmpfs tmpfs /dev/shm
    grep -q "/dev/shm" /etc/fstab || echo "tmpfs /dev/shm tmpfs rw 0 0" >> /etc/fstab
  fi

  echo -n $"Starting Teamspeak 3 server $prog: "

  errout=$dbdir/query-admin-password.txt
  if grep -q "^dbplugin=ts3db_sqlite3" $config; then
    if [ -s $dbdir/ts3server.sqlitedb ]; then
      errout="/dev/null"
    else
      echo
      echo 1>&2 "This is the first start of a new Teamspeak 3 server."
      echo 1>&2 "Check $errout for the query admin password"
      echo 1>&2 "and the server admin token if the database was created successfully."
      echo -n $"Starting"
    fi
  fi

  if [ "$errout" != "/dev/null" ]; then
    echo "Teamspeak server started on `date`" >> $errout
    chown $ts3user:root $errout
    chmod 0640 $errout
  fi

  cd $dbdir
  runuser -s /bin/bash $ts3user -c "
    umask 0027
    $exec inifile=$config 1>/dev/null 2>>$errout &
    umask 0022
    echo -n \$! > $pidfile
  "
  sleep 3
  [ -f "$pidfile" ] && checkpid `cat $pidfile`
  retval=$?
  if [ "$retval" -eq 0 ]; then
    success
    touch $lockfile
    if [ "$errout" != "/dev/null" -a -f $snapconf ]; then
      # copy query admin name and password to snapshot login data
      if grep -q "#user=\"__QUERYADMIN__\"" $snapconf; then
        grep "loginname= " $errout |
        while read -r kwuser queryadmin kwpass password; do
          sed -i "s/#\?user=\".*\"/user=${queryadmin%,}/g" $snapconf
          sed -i "s/#\?pass=\".*\"/pass=$password/g" $snapconf
        done
      fi
    fi
  else
    failure
    rm -f $pidfile $lockfile
  fi
  echo
  return $retval
}

stop() {
  echo -n $"Stopping Teamspeak 3 server $prog: "
  killproc -p $pidfile $exec
  retval=$?
  echo
  [ $retval -eq 0 ] && rm -f $pidfile $lockfile
  return $retval
}

restart() {
  stop
  start
}


case "$1" in
  start|stop|restart)
      $1
      ;;
  reload|force-reload)
      restart
      ;;
  try-restart|condrestart)
      [ -f $lockfile ] && restart || :
      ;;
  status)
      status -p $pidfile $exec
      ;;
  *)
      echo $"Usage: $0 {start|stop|status|restart|condrestart|try-restart|reload|force-reload}"
      exit 2
esac
EOF

# create tsdns startup script
cat <<"EOF" > %{buildroot}%{_initrddir}/tsdnsserver
#!/bin/sh

# tsdnsserver Startup script written by Alex Woick <alex@wombaz.de> 2012-02-22

# chkconfig: - 95 5
# description: tsdnsserver for TeamSpeak 3 Server
# processname: %{__tsdnsbin}
# config: %{_sysconfdir}/sysconfig/teamspeak3
# pidfile: %{_localstatedir}/run/teamspeak3/tsdnsserver.pid

# TeamSpeak 3
# Copyright TeamSpeak Systems GmbH
# http://www.teamspeak.com

# Source function library.
. /etc/init.d/functions

exec=%{_bindir}/%{__tsdnsbin}
prog=$(basename $exec)
configdir=%{__etc}
pidfile=%{_localstatedir}/run/teamspeak3/tsdnsserver.pid
ts3user=%{__user}

[ -e %{_sysconfdir}/sysconfig/teamspeak3 ] && . %{_sysconfdir}/sysconfig/teamspeak3

lockfile=%{_localstatedir}/lock/subsys/tsdnsserver

start() {

  [ -f "$pidfile" ] && checkpid `cat $pidfile` && return 0

  # check if tmpfs is mounted, add entry to fstab if necessary
  if ! mount|grep -q "/dev/shm"; then
    mount -t tmpfs tmpfs /dev/shm
    grep -q "/dev/shm" /etc/fstab || echo "tmpfs /dev/shm tmpfs rw 0 0" >> /etc/fstab
  fi

  echo -n $"Starting tsdnsserver $prog: "
  cd $configdir
  runuser -s /bin/bash $ts3user -c \
    "$exec 1>/dev/null 2>/dev/null & echo -n \$! > $pidfile"
  sleep 3
  [ -f "$pidfile" ] && checkpid `cat $pidfile`
  retval=$?
  [ "$retval" -eq 0 ] && success || failure
  [ "$retval" -eq 0 ] && touch $lockfile || rm -f $pidfile
  echo
  return $retval
}

stop() {
  echo -n $"Stopping tsdnsserver $prog: "
  killproc -p $pidfile $exec -TERM
  retval=$?
  echo
  [ $retval -eq 0 ] && rm -f $pidfile $lockfile
  return $retval
}

restart() {
  stop
  start
}


case "$1" in
  start|stop|restart)
      $1
      ;;
  force-reload)
      restart
      ;;
  try-restart|condrestart)
      [ -f $lockfile ] && restart || :
      ;;
  reload)
      echo -n $"Reloading tsdnsserver $prog: "
      cd $configdir
      runuser -m -s /bin/bash - $ts3user -c "$exec --update"
      success
      echo
      exit 0
      ;;
  status)
      status -p $pidfile $exec
      ;;
  *)
      echo $"Usage: $0 {start|stop|status|restart|condrestart|try-restart|reload|force-reload}"
      exit 2
esac
EOF
%endif

# create script for creating virtual server snapshots
cat <<"EOF" > %{buildroot}%{_bindir}/ts3snapshot
#!/bin/sh

usage="\
$0 - create or deploy a snapshot of a virtual Teamspeak 3 server instance

Usage:
$0 [-h host] [-p <port>] [-i <instance>] [-f <file>] [-u <user>] [-P <password>] [cmd]

Commands:
  create        create snapshot (read from server and save to file)
  deploy        deploy snapshot (read from file and write to server)
  clientlist    list clients that are currently online

Options:
  -h <hostname> server hostname   (default: localhost)
  -p <port>     server query port (default: 10011)
  -i <instance> virtual server    (default: only on create: all instances)
  -f <file>     snapshot file     (default: ts3-snapshot-%%i.txt
  -u <user>     admin query user name
  -P <password> admin query user password

Notes:
- if you provide an instance number, only this virtual server is processed.
- if you provide a file name with -f, %%i is replaced with the instance number
- settings from %{__etc}/snapshot are used as defaults"


# read server response from input, return 0 on success
# return 1 and print message, if server returns error
check_ts3_response() {
  local prefix=$1 kw=$2

  read -r kw id msg
  if [ "$kw" != "error" ]; then
    echo $prefix
    echo "Unexpected server response \"$kw $id $msg\""
    return 2
  fi
  [ "$id" = "id=0" ] && return 0
  echo $prefix
  msg=${msg#msg=}
  echo "Server message: \"${msg//\\s/ }\""
  return 1
}

# perform signon to Teamspeak server, return 0 on success
# return 1 and print message, if server returns error
check_ts3_signon() {
  local line line1

  if ! read -r line; then
    echo "Unable to connect to the Teamspeak Server"
    echo "host=\"$1\""
    echo "port=\"$2\""
    return 1
  fi
  if [ "$line" != "TS3" ]; then
    echo "Invalid greeting line(1), expected \"TS3\", got \"$line\""
    return 1
  fi

  read -r line line1
  if [ "$line" != "Welcome" ]; then
    echo "Invalid greeting line(2), expected \"Welcome to the TeamSpeak 3 ServerQuery interface[...]\", got \"$line $line1\""
    return 1
  fi
  return 0
}

# output list of online clients
clientlist() {
  local dir line _host=$1 _port=$2 _instance=$3 _user=$4 _pass=$5

  echo "client list for instance $_instance:"
  echo -e "use $_instance\nlogin $_user $_pass\nclientlist -ip\nquit" | \
  nc $_host $_port | tr -d "\r" | {
    check_ts3_signon $_host $_port || return 1
    check_ts3_response "Unable to select server instance \"$_instance\"" || return 1
    check_ts3_response "Unable to login to the Teamspeak server" || return 1
    read -r line
    for cl in `echo "$line"|xargs -n 1 -d "|"`; do
      echo "$cl"|grep -E "^client_nickname"
    done

    check_ts3_response "Unable to get clientlist" || return 1
  } || return 1
  return 0
}

# get a list of all virtual servers and get the list of online clients for all of them
clientlist_all() {
  local line _host=$1 _port=$2 _user=$3 _pass=$4

  echo -e "login $_user $_pass\nserverlist -short\nquit" | \
  nc $_host $_port | tr -d "\r" | {
    check_ts3_signon $_host $_port || return 1
    check_ts3_response "Unable to login to the Teamspeak server" || return 1
    read -r line
    check_ts3_response "Unable to get server instance list" || return 1

    for i in `echo "$line"|xargs -n 1 -d "|"|grep "virtualserver_status=online"|sed -re 's/virtualserver_id=([0-9]+).*/\1/g'`; do
      if ! clientlist "$_host" "$_port" "$i" "$_user" "$_pass"; then
        echo "clientlist for server instance $i failed."
      fi
    done
  } || return 1
  return 0
}


# deploy a snapshot to given virtual server instance
snapshot_deploy() {
  local _host=$1 _port=$2 _instance=$3 _user=$4 _pass=$5 _file=$6

  if [ ! -f $_file ]; then
    echo "Unable to find input file '$_file', aborting"
    exit 1
  fi
  echo -e "use $_instance\nlogin $_user $_pass\n serversnapshotdeploy `cat $_file`\nquit" | \
  nc -4 $_host $_port | tr -d "\r" | {
    check_ts3_signon $_host $_port || return 1
    check_ts3_response "Unable to select server instance \"$_instance\"" || return 1
    check_ts3_response "Unable to login to the Teamspeak server" || return 1
    check_ts3_response "Unable to deploy snapshot" || return 1
  } || return 1
  return 0
}

# create a snapshot from given vitual server instance and write to file
snapshot_create() {
  local dir line _host=$1 _port=$2 _instance=$3 _user=$4 _pass=$5 _file=$6

  dir=`dirname "$_file"`
  echo -e "use $_instance\nlogin $_user $_pass\nserversnapshotcreate\nquit" | \
  nc -4 $_host $_port | tr -d "\r" | {
    check_ts3_signon $_host $_port || return 1
    check_ts3_response "Unable to select server instance \"$_instance\"" || return 1
    check_ts3_response "Unable to login to the Teamspeak server" || return 1
    read -r line
    [ -z "$dir" -o -d "$dir" ] || mkdir -p "$dir"
    echo -n "$line" > "$_file"
    check_ts3_response "Unable to get snapshot" || { rm -f "$_file"; return 1; }
  } || return 1
  return 0
}

# get a list of all virtual servers and create snapshots for each of them
# Put a %%i into the filename to avoid that the snaphots overwrite each other
snapshot_create_all() {
  local line _host=$1 _port=$2 _user=$3 _pass=$4 _file=$5

  echo -e "login $_user $_pass\nserverlist -short\nquit" | \
  nc -4 $_host $_port | tr -d "\r" | {
    check_ts3_signon $_host $_port || return 1
    check_ts3_response "Unable to login to the Teamspeak server" || return 1
    read -r line
    check_ts3_response "Unable to get server instance list" || return 1

    for i in `echo "$line"|xargs -n 1 -d "|"|grep "virtualserver_status=online"|sed -re 's/virtualserver_id=([0-9]+).*/\1/g'`; do
      if ! snapshot_create "$_host" "$_port" "$i" "$_user" "$_pass" "${_file//\%%i/$i}"; then
        echo "Snapshot for server instance $i failed."
      fi
    done
  } || return 1
  return 0
}

if [ ! -x /usr/bin/nc ]; then
  echo "/usr/bin/nc not found - please install NetCat!"
  exit 1
fi

[ -f %{__etc}/snapshot ] && . %{__etc}/snapshot

while getopts "f:h:i:p:u:P:" key ; do
  case "$key" in
    f) file="$OPTARG" ;;
    h) host="$OPTARG" ;;
    i) instance="$OPTARG" ;;
    p) port="$OPTARG" ;;
    u) user="$OPTARG" ;;
    P) pass="$OPTARG" ;;
    *) exec echo "$usage" ;;
  esac
done
shift $(( $OPTIND -1 ))
cmd=${1:-}
host=${host:-localhost}
port=${port:-10011}
file=${file:-ts3-snapshot-%%i.txt}

if [ -z "$user" -o -z "$pass" ]; then
  echo -e "error: no username or password given!\n"
  exec echo "$usage"
fi

case "$cmd" in
  deploy)
    if [ -z "$instance" ]; then
      echo -e "deploy requires an instance number\n"
      exec echo "$usage"
    fi
    snapshot_deploy "$host" "$port" "$instance" "$user" "$pass" "${file//\%%i/$instance}"
    ;;
  create)
    if [ -z "$instance" ]; then
      snapshot_create_all "$host" "$port" "$user" "$pass" "$file"
    else
      snapshot_create "$host" "$port" "$instance" "$user" "$pass" "${file//\%%i/$instance}"
    fi
    ;;
  clientlist)
    if [ -z "$instance" ]; then
      clientlist_all  "$host" "$port" "$user" "$pass"
    else
      clientlist "$host" "$port" "$instance" "$user" "$pass"
    fi
    ;;
  *)
    echo -e "Unknown command \"$cmd\"\n"
    exec echo "$usage"
    ;;
esac
EOF


# create cron script for snapshot and backup
cat <<"EOF" > %{buildroot}%{_bindir}/ts3backup_cron
#!/bin/sh

umask 0027

# remove snapshots older than 60 days
find %{__dbdir}/snapshots -type f -mtime +60 -exec rm -f {} \;

# create new snapshots of all virtual servers
ts3snapshot create

# stop here, if sqlite database not in use
[ -f %{__dbdir}/ts3server.sqlitedb ] || exit 0

# remove database backups older than 60 days
find %{__dbdir}/backups -type f -mtime +60 -exec rm -f {} \;

# perform a clean copy of the sqlite database
sqlite3 %{__dbdir}/ts3server.sqlitedb ".backup \
  %{__dbdir}/backups/ts3server.sqlitedb.`date +%%Y%%m%%d-%%H%%M%%S`"
EOF


# create crontab file for snapshot and backup
cat <<"EOF" > %{buildroot}%{_sysconfdir}/cron.d/%{name}
MAILTO=root
# scheduled backups of the Teamspeak 3 server database
#
45 3 * * * %{__user} %{_bindir}/ts3backup_cron
EOF


# create script for resetting the query admin password
cat <<"EOF" > %{buildroot}%{_bindir}/ts3-reset-query-admin.sh
#!/bin/sh

username='serveradmin'
db="%{__dbdir}/ts3server.sqlitedb"

if [ ! -x /usr/bin/openssl ]; then
  echo "/usr/bin/openssl not found - please install openssl!"
  exit 1
fi

# create random password with 12 characters
pw=$(tr -dc "A-Za-z0-9_!%=+" < /dev/urandom | head -c 12)
echo "Resetting Teamspeak 'serveradmin' password..."

encoded=$(echo -n "$pw" | openssl dgst -binary -sha1 | openssl base64)

if sqlite3 "$db" "UPDATE clients SET client_login_password='$encoded' WHERE client_login_name='$username'"; then
  s=$(sqlite3 "$db" "SELECT client_login_password from clients WHERE client_login_name='$username'")
  if [ "$encoded" = "$s" ]; then
    echo "Success! Write down the new password for $username:"
    echo "$pw"
  else
    echo "Database update failed. The update command seems to have succeeded, but the new password was not saved!"
    echo "tried to set encoded password='$encoded'"
    echo "encoded password in database='$s'"
  fi
else
  echo "Database update failed!"
fi
EOF


# don't strip/recompress the binaries. Leave them untouched.
%define __os_install_post %{nil}


%pre
getent passwd %{__user} >/dev/null || \
  useradd -r -d %{__dbdir} -s /sbin/nologin -c "Teamspeak Server" %{__user}

if [ "$1" -ge "1" ]; then
  # Package upgrade, not install
  # stop server and save state information to restart it after upgrade
  # it's required to stop the server before the new files get copied, because
  # the server needs the original *.sql files on shutdown.
  %{__rm} -f %{_tmppath}/teamspeak3-running %{_tmppath}/tsdnsserver-running

%if %{use_systemd}
  /usr/bin/systemctl -q is-active teamspeak3-server.service && touch %{_tmppath}/teamspeak3-running
  /usr/bin/systemctl stop teamspeak3-server.service >/dev/null 2>&1

  /usr/bin/systemctl -q is-active tsdns-server.service && touch %{_tmppath}/tsdnsserver-running
  /usr/bin/systemctl stop tsdns-server.service >/dev/null 2>&1 || :
%else
  /sbin/service teamspeak3 status >/dev/null 2>&1 && touch %{_tmppath}/teamspeak3-running
  /sbin/service teamspeak3 stop >/dev/null 2>&1

  /sbin/service tsdnsserver status >/dev/null 2>&1 && touch %{_tmppath}/tsdnsserver-running
  /sbin/service tsdnsserver stop >/dev/null 2>&1 || :
%endif
fi

%post
ldconfig
%if %{use_systemd}
%systemd_post teamspeak3-server.service tsdns-server.service
%else
if [ "$1" -eq "1" ]; then
  # Initial installation
  /sbin/chkconfig --add teamspeak3
  /sbin/chkconfig --add tsdnsserver || :
fi
%endif

%post mariadb
ldconfig
if [ "$1" -eq "1" ]; then
  # Initial installation
  # generate a random default database password for mariadb configuration.
  # We don't want to have the same default password for every user in the world.
  pw=`tr -dc A-Za-z0-9_ < /dev/urandom | head -c 8`
  sed -i "s/__PASSWORD__/$pw/g" %{__etc}/ts3db_mariadb.ini || :
fi

%preun
%if %{use_systemd}
%systemd_preun teamspeak3-server.service tsdns-server.service
%else
if [ "$1" -eq "0" ] ; then
  # Package removal, not upgrade
  /sbin/service tsdnsserver stop >/dev/null 2>&1
  /sbin/service teamspeak3 stop >/dev/null 2>&1
  /sbin/chkconfig --del teamspeak3
  /sbin/chkconfig --del tsdnsserver || :
fi
%endif

%postun
%if %{use_systemd}
# we cannot use this, see comment in %%pre:
# %%systemd_postun_with_restart teamspeak3-server.service tsdns-server.service
# So for a clean restart, we must stop the old server in %%pre and start the
# updated server here.
%systemd_postun
if [ "$1" -ge "1" ]; then
  # Package upgrade, not uninstall
  test -e %{_tmppath}/teamspeak3-running && \
    /usr/bin/systemctl start teamspeak3-server.service >/dev/null 2>&1

  test -e %{_tmppath}/tsdnsserver-running && \
    /usr/bin/systemctl start tsdns-server.service >/dev/null 2>&1
fi
%else
if [ "$1" -ge "1" ]; then
  # Package upgrade, not uninstall
  test -e %{_tmppath}/teamspeak3-running && \
    /sbin/service teamspeak3 start >/dev/null 2>&1

  test -e %{_tmppath}/tsdnsserver-running && \
    /sbin/service tsdnsserver start >/dev/null 2>&1
fi
%endif
%{__rm} -f %{_tmppath}/teamspeak3-running %{_tmppath}/tsdnsserver-running || :

%postun mariadb
ldconfig


%files
%defattr(-,root,root)
%doc doc/ tsdns/ CHANGELOG README.install
%if 0%{?_licensedir:1}
%license LICENSE
%else
%doc LICENSE
%endif

%{__data}
%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
%dir %{__libdir}
%{__libdir}/libts3db_sqlite3.so
%{__libdir}/libts3_ssh.so
%{_bindir}/%{__ts3serverbin}
%{_bindir}/%{__tsdnsbin}
%attr(0755,root,root) %{_bindir}/ts3-reset-query-admin.sh

%{__dbdir}/serverquerydocs

%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,root,root) %dir %{__etc}
%attr(0644,root,root) %config(noreplace) %{__etc}/*.txt
%attr(0644,root,root) %config(noreplace) %{__etc}/ts3server.ini
%attr(0644,root,root) %config(noreplace) %{__etc}/tsdns_settings.ini
%if %{use_systemd}
%{_unitdir}/*
%{_firewallddir}/*
%attr(0755,root,root) %{_bindir}/get-query-admin.sh
%else
%attr(0755,root,root) %{_initrddir}/*
%attr(0755,%{__user},%{__user}) %dir %{_localstatedir}/run/teamspeak3
%endif
%attr(0750,%{__user},%{__user}) %dir %{__dbdir}
%attr(0755,%{__user},%{__user}) %dir %{_localstatedir}/log/teamspeak3

%files mariadb
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{__etc}/ts3server.ini.mariadb
%attr(0640,root,%{__user}) %config(noreplace) %{__etc}/ts3db_mariadb.ini
%{__libdir}/libts3db_mariadb.so
%{__libdir}/libmariadb.so*

%files backup
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/ts3backup_cron
%attr(0755,root,root) %{_bindir}/ts3snapshot
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/cron.d/%{name}
%attr(0640,root,%{__user}) %config(noreplace) %{__etc}/snapshot
%attr(0750,%{__user},%{__user}) %dir %{__dbdir}/backups
%attr(0750,%{__user},%{__user}) %dir %{__dbdir}/snapshots


%changelog
* Fri Aug 31 2018 Izenn <none@nothing.com> - 3.3.1-1
- updated to server 3.3.1
- added libts3-ssh

* Thu May 17 2018 Izenn <none@nothing.com> - 3.2.0-1
- updated to server 3.2.0

* Fri Mar 2 2018 Izenn <none@nothing.com> - 3.1.1-1
- updated to server 3.1.1

* Wed Jul 19 2017 Alex Woick <alex@wombaz.de> - 3.0.13.8-1
- updated to server 3.0.13.8

* Tue Jun 27 2017 Alex Woick <alex@wombaz.de> - 3.0.13.7-1
- updated to server 3.0.13.7

* Wed Nov 09 2016 Alex Woick <alex@wombaz.de> - 3.0.13.6-1
- updated to server 3.0.13.6

* Tue Oct 25 2016 Alex Woick <alex@wombaz.de> - 3.0.13.5-1
- updated documentation about MariaDB usage
- updated to server 3.0.13.5

* Wed Sep 07 2016 Alex Woick <alex@wombaz.de> - 3.0.13.4-1
- updated to server 3.0.13.4

* Mon Aug 22 2016 Alex Woick <alex@wombaz.de> - 3.0.13.3-1
- updated to server 3.0.13.3

* Mon Aug 15 2016 Alex Woick <alex@wombaz.de> - 3.0.13.2-1
- updated to server 3.0.13.2

* Sun Aug 14 2016 Alex Woick <alex@wombaz.de> - 3.0.13.1-1
- updated to server 3.0.13.1

* Wed Jul 20 2016 Alex Woick <alex@wombaz.de> - 3.0.13-1
- updated to server 3.0.13
- added ts3-reset-query-admin.sh

* Wed May 18 2016 Alex Woick <alex@wombaz.de> - 3.0.12.4-2
- updated teamspeak3-server.service: removed network-online.target from After=
  and added dependency to network.target and nss-lookup.target
- added redist/libmariadb.so* to mariadb package
- added ExecReload= to tsdns-server.service

* Fri Mar 25 2016 Alex Woick <alex@wombaz.de> - 3.0.12.4-1
- updated to server 3.0.12.4
- moved LICENSE from %doc to %license if available
- removed trigger for sysv -> systemd autostart migration
- improved comments and documentation
- made some %requires sysv-only
- simplified user creation
- added dependency to logrotate for rotating the logfiles

* Fri Mar 04 2016 Alex Woick <alex@wombaz.de> - 3.0.12.3-1
- updated to server 3.0.12.3

* Sun Feb 21 2016 Alex Woick <alex@wombaz.de> - 3.0.12.2-3
- changed After= to After=network-online.target in teamspeak3-server.service
  to provide name resolution for resolving the licensing server.
- updated documentation with systemd commands

* Tue Feb 16 2016 Alex Woick <alex@wombaz.de> - 3.0.12.2-2
- added clientlist parameter to /usr/bin/ts3snapshot

* Tue Feb 16 2016 Alex Woick <alex@wombaz.de> - 3.0.12.2-1
- updated to server 3.0.12.2

* Wed Feb 10 2016 Alex Woick <alex@wombaz.de> - 3.0.12.1-1
- updated to server 3.0.12.1

* Sat Dec 19 2015 Alex Woick <alex@wombaz.de> - 3.0.12-1
- updated to server 3.0.12, which included renaming *.tar.gz -> *.tar.bz2 and ts3server/tsdns binaries

* Fri Aug 21 2015 Alex Woick <alex@wombaz.de> - 3.0.11.4-1
- updated to server 3.0.11.4

* Mon May 11 2015 Alex Woick <alex@wombaz.de> - 3.0.11.3-1
- updated to server 3.0.11.3

* Sat May 02 2015 Alex Woick <alex@wombaz.de> - 3.0.11.2-3
- added -4 to nc call to force ipv4

* Fri May 01 2015 Alex Woick <alex@wombaz.de> - 3.0.11.2-2
- fixed inclusion of get-query-admin.sh for systemd systems

* Thu Dec 18 2014 Alex Woick <alex@wombaz.de> - 3.0.11.2-1
- updated to server 3.0.11.2

* Thu Oct 16 2014 Alex Woick <alex@wombaz.de> - 3.0.11.1-1
- updated to server 3.0.11.1

* Tue Sep 02 2014 Alex Woick <alex@wombaz.de> - 3.0.11-2
- use systemd units instead of sysv init files on systemd systems

* Sun Aug 10 2014 Alex Woick <alex@wombaz.de> - 3.0.11-1
- updated to server 3.0.11
- removed libdir from server startscript
- removed contributed scripts and documentation for mysql/mariadb
- changed architecture of backup package to noarch

* Fri Jul 04 2014 Alex Woick <alex@wombaz.de> - 3.0.10.3-3.aw
- added /etc/ld.so.conf.d/teamspeak3-server-%{_arch}.conf and call
  ldconfig at install time

* Mon Mar 31 2014 Alex Woick <alex@wombaz.de> - 3.0.10.3-2.aw
- changed tmpwatch to find for backup maintenance

* Wed Jan 08 2014 Alex Woick <alex@wombaz.de> - 3.0.10.3-1.aw
- updated to server 3.0.10.3
- removed private IP ranges from query_ip_whitelist.txt

* Mon Dec 02 2013 Alex Woick <alex@wombaz.de> - 3.0.10.2-1.aw
- updated to server 3.0.10.2

* Tue Nov 12 2013 Alex Woick <alex@wombaz.de> - 3.0.10.1-1.aw
- updated to server 3.0.10.1

* Wed Oct 02 2013 Alex Woick <alex@wombaz.de> - 3.0.10-2.aw
- no debug package (fixes "*** ERROR: No build ID note found")
- fixed portrange in README.install

* Tue Oct 01 2013 Alex Woick <alex@wombaz.de> - 3.0.10-1.aw
- updated to server 3.0.10

* Thu Sep 12 2013 Alex Woick <alex@wombaz.de> - 3.0.9-1.aw
- updated to server 3.0.9
- added logrotate configuration

* Fri Aug 23 2013 Alex Woick <alex@wombaz.de> - 3.0.8-1.aw
- updated to server 3.0.8
- extended documentation; added SRV dns record explanation
- moved libraries to %%{_libdir}/%%{name} and added appropriate LD_LIBRARY_PATH
  to the start script
- added scripts and cron job for daily database backup
- added mount check for /dev/shm to start scripts
- split into 3 packages for clean dependencies

* Mon Jul 01 2013 Alex Woick <alex@wombaz.de> - 3.0.7.2-1.aw
- updated to server 3.0.7.2

* Tue Mar 26 2013 Alex Woick <alex@wombaz.de> - 3.0.7.1-1.aw
- updated to server 3.0.7.1
- updated minor details in the documentation

* Wed Mar 06 2013 Alex Woick <alex@wombaz.de> - 3.0.7-1.aw
- updated to server 3.0.7

* Fri Jul 13 2012 Alex Woick <alex@wombaz.de> - 3.0.6.1-1.aw
- updated to server 3.0.6.1

* Sun Jun 24 2012 Alex Woick <alex@wombaz.de> - 3.0.6-1.aw
- updated to server 3.0.6

* Tue Jun 12 2012 Alex Woick <alex@wombaz.de> - 3.0.5-2
- added filter for automated dependency on libmysqlclient.so.15
  (mysql client library 5.0 is not available on newer distributions)
- new init script from template

* Sat May 05 2012 Alex Woick <alex@wombaz.de> - 3.0.5
- Updated to server 3.0.5
- confirmed proper operation on 64-bit CentOS 5.8.

* Mon Apr 16 2012 Alex Woick <alex@wombaz.de> - 3.0.3
- Updated to server 3.0.3

* Thu Mar 01 2012 Alex Woick <alex@wombaz.de> - 3.0.2
- Updated to server 3.0.2

* Tue Feb 21 2012 Alex Woick <alex@wombaz.de> - 3.0.1
- Initial package.
