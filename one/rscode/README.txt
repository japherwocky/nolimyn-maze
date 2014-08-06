depends on libmysql++-dev package

connects to mysql through a socket, looks like the mysq ldefault.

apt-get install mysql-server

mysql -u root
<pre>
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 9
Server version: 5.0.32-Debian_7etch8-log Debian etch distribution

Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

mysql> create user 'mud'@'localhost' identified by 'r1ftshadow';
Query OK, 0 rows affected (0.00 sec)

mysql> create database riftshadowdb;
Query OK, 1 row affected (0.00 sec)

mysql> grant all on riftshadowdb.* to 'mud'@'localhost';
Query OK, 0 rows affected (0.00 sec)

mysql> quit;
Bye
</pre>

Then run something like <code>mysql -u mud -p riftshadowdb &lt; rift_core.sql</code>

make, and set up directories to players, etc.

then import rift.sql too :P
