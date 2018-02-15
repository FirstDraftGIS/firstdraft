su postgres -c "psql -c 'CREATE DATABASE dbfd'";
su postgres -c "psql -c 'CREATE ROLE $(whoami) SUPERUSER LOGIN CREATEDB'";
su postgres -c "psql -c 'ALTER DATABASE dbfd OWNER TO $(whoami)'";

git clone https://github.com/DanielJDufour/safecast ~/safecast;
cd ~/safecast && make install && make installcheck;

cd ~/;
psql -c "$(awk 'NR>=3 { printf "CREATE EXTENSION " $2 "; " }' ~/firstdraft/postgresql_extensions.md)" dbfd; 


