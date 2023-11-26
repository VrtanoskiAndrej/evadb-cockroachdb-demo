
# CockroachDB extention for EvaDB

## Installation

First we need to install a local instance of cockroachDB, which can be done by following the installation guide for linux in the following link: https://www.cockroachlabs.com/docs/stable/install-cockroachdb-linux

```bash
wget https://binaries.cockroachdb.com/cockroach-v23.2.0-alpha.3.linux-amd64.tgz
```

```bash
tar -xf cockroach-v23.2.0-alpha.3.linux-amd64.tgz
```

CockroachDB relies on specific libgeos libraries that are not installed on linux distros, so these will need to be extracted from the folder that we downloaded and placed with the rest of the linux standard libraries. 

```bash
mkdir -p /usr/local/lib/cockroach
```

```bash
cp -i cockroach-v23.1.11.linux-{ARCHITECTURE}/lib/libgeos.so /usr/local/lib/cockroach/
```

```bash
cp -i cockroach-v23.1.11.linux-{ARCHITECTURE}/lib/libgeos_c.so /usr/local/lib/cockroach/
```

Lastly we need to place the actual executable command somewhere in our path directory, and thus we will move it to /usr/local

```bash
mv cockroach-v23.1.11.linux-{ARCHITECTURE}/cockroack /usr/local/bin/
```

As a simple verification of our steps, we can check the version of the binary file:

```bash
cockroach --version
```

## Running EvaDB with Cockroach

### CockroackDB Secure Mode

This is the suggested way of booting the cockroach db servers in a secrure fashion, which will initalize a set of certificates for interfacing with the server in a safe manor. This will setup a default user for the database called `eva` with password `password` that will be used in the transactions though eva db.

```bash
./setup.sh start-single-node
```

Using this approach allows us to interface with eva db using the params that we pass in, otherwise if we ran cockroack db in an insecure mode we would need to interface with it through the url as psycopg2 api is different. 

Use the code below in python files to create an instance of the database in the eva enviroment and interface with it using the USE SQL paradigm.

```python
cursor = evadb.connect().cursor()

params = {
    "user": "eva",
    "password": "password",
    "host": "localhost",
    "port": "26257",
    "database": "evadb",
}

cursor.query(f"""
    CREATE DATABASE IF NOT EXISTS cockroachdb_data WITH ENGINE = 'cockroachdb', PARAMETERS = {params};
""").execute()

self.cursor.query(f"""
  USE cockroachdb_data {{
    CREATE TABLE IF NOT EXISTS {table_name} (id INT, name VARCHAR(64), number INT)
  }};
""").execute()
```
### CockroackDB Insecure Mode (depricated)

In another terminal, we instantitate a single server node for our cockroachDB and attach it to our local host at port 26257.

```bash
cockroach start-single-node --listen-addr=localhost:26257 --insecure
```

When this command runs, it will output a log similar to the following: 

```
CockroachDB node starting at 2023-10-18 (took 1.2s)
build:               CCL v23.2.0-alpha.3 @ 2023/10/10 00:07:20 (go1.20.8 X:nocoverageredesign)
webui:               http://localhost:8080
sql:                 postgresql://root@localhost:26257/defaultdb?sslmode=disable
sql (JDBC):          jdbc:postgresql://localhost:26257/defaultdb?sslmode=disable&user=root
RPC client flags:    cockroach <client cmd> --host=localhost:26257 --insecure
logs:                /home/root/cockroach-data/logs
temp dir:            /home/root/cockroach-data/cockroach-temp1987976066
external I/O path:   /home/root/cockroach-data/extern
store[0]:            path=/home/root/cockroach-data
storage engine:      pebble
clusterID:           a97cdc0f-4a29-4469-ba75-1230
status:              initialized new cluster
nodeID:              1
```

Make a note of the sql URI as this will be important when connecting our database with evadb. `postgresql://root@localhost:26257/defaultdb?sslmode=disable`

On another terminal, we run the python test command, and we can verify that cockroach db and evadb have proper intergration with one another:

```bash
$ python3 cockroach_test.py


[Tue Oct 17 22:45:41 2023] TEST ConnectTest
Time:  2.6738364696502686
PASSED TEST ConnectTest

[Tue Oct 17 22:45:44 2023] TEST CreateTable
creating table with name  customers
Time:  0.019145965576171875
PASSED TEST CreateTable

[Tue Oct 17 22:45:44 2023] TEST InsertValues
inserting values into table
Time:  0.9618363380432129
PASSED TEST InsertValues

[Tue Oct 17 22:45:45 2023] TEST SelectAll
selecting all values from table
    id  name  number
0    1    11       0
1    2    22       1
2    3    33       1
3    4    44       2
4    5    55       2
..  ..   ...     ...
94  95  1045      47
95  96  1056      48
96  97  1067      48
97  98  1078      49
98  99  1089      49

[99 rows x 3 columns]
Time:  0.012323141098022461
PASSED TEST SelectAll

[Tue Oct 17 22:45:45 2023] TEST UpdateTest
updating entry in table
Time:  0.00023698806762695312
PASSED TEST UpdateTest

[Tue Oct 17 22:45:45 2023] TEST JoinTest
complex join of two tables
    id  name  number  id   coin
0    1    11       0   1  tails
1    2    22       1   2  tails
2    3    33       1   3  heads
3    4    44       2   4  tails
4    5    55       2   5  heads
..  ..   ...     ...  ..    ...
92  93  1023      46  93  heads
93  94  1034      47  94  heads
94  95  1045      47  95  heads
95  96  1056      48  96  heads
96  97  1067      48  97  heads

[97 rows x 5 columns]
Time:  0.7697305679321289
PASSED TEST JoinTest
```

### Implementation Details

The implementation of the project relies heavily on the abstract database DBHandler method defined in `evadb/third_party/databases/types.py`. Various methods were implemented, most notabliy the `execute_native_query` command and the `connect` command which were vital to the entire project. Since cockroachDB's python interface relies on postgres, the code was implemented with respect to the DBHandler code for the postgres file, which a few changes relating to the data representation and the sql output that the database provides. This was important when conaverting sql commands to pandas dataframes to be used throughout the libary.

To validate the implementation, I wrote a suite of testcases to stress test vital SQL components of the database, such as the SELECT, INSERT, CREATE and JOIN methods. These are showcaed above and show the correctness of the methodology. 

### Reference

* https://github.com/cockroachlabs/hello-world-python-psycopg2/blob/master/example.py
* https://pypi.org/project/psycopg2/
