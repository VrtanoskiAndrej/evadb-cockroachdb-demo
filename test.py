import evadb
import csv
import time
import random

insert_range = 100
table_name = 'customers'

class UnitTest:
  def __init__(self, name, cursor):
    self.name = name
    self.cursor = cursor
  
  def fail(self):
    print(f'FAILED TEST {self.name}')
    exit()

  def passed(self):
    print(f'PASSED TEST {self.name}\n')

  def call(self, *args):
    print(f'[{time.ctime()}] TEST {self.name}')

    ## measurment region for test
    start_time = time.time()

    try:
      test_return = self.run(args)

    except Exception as e:
        print(e)
        self.fail()  

    end_time = time.time()
    print("Time: ", end_time - start_time)

    self.passed()

    return test_return

  def run(self, *args):
    print("test not implemented")
    return False
  
class ConnectTest(UnitTest):
  def run(self, *args):
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

    return cursor

class TableTest(UnitTest):
  def run(self, *args):
    print('creating table with name ', table_name)

    # initialize the url_table
    self.cursor.query(f"""
      USE cockroachdb_data {{
        DROP TABLE IF EXISTS {table_name}
      }};
    """).execute()

    self.cursor.query(f"""
      USE cockroachdb_data {{
        CREATE TABLE IF NOT EXISTS {table_name} (id INT, name VARCHAR(64), number INT)
      }};
    """).execute()


class InsertionTest(UnitTest):
  def run(self, *args):
    print('inserting values into table')
    
    for i in range(1, insert_range):
      id = i
      name = str(i*11)
      number = int(i/2)
      self.cursor.query(f""" USE cockroachdb_data {{ \
        UPSERT INTO {table_name}(id, name, number) \
        VALUES ({id}, '{name}', {number}) 
      }};""" ).execute()


class SelectAllTest(UnitTest):
  def run(self, *args):
    print('selecting all values from table')
    print (self.cursor.query(f""" USE cockroachdb_data {{ \
      SELECT * FROM {table_name}
    }};""" ).execute())

class UpdateTest(UnitTest):
  def run(self, *args):
    print('updating entry in table')
    self.cursor.query(f""" USE cockroachdb_data {{ \
      UPDATE {table_name} SET name = 'XXX' WHERE id = 0
    }};""" )
    
class JoinTest(UnitTest):
  def run(self, *args):
    print('complex join of two tables')

    # create new table
    self.cursor.query(f"""
      USE cockroachdb_data {{
        DROP TABLE IF EXISTS cointoss
      }};
    """).execute()

    self.cursor.query(f"""
      USE cockroachdb_data {{
        CREATE TABLE IF NOT EXISTS cointoss (id INT, coin VARCHAR(64))
      }};
    """).execute()

      
    for i in range(1, insert_range - 2):
      id = i
      toss = 'heads' if random.randint(0, 1) == 0 else 'tails'

      self.cursor.query(f""" USE cockroachdb_data {{ \
        UPSERT INTO cointoss(id, coin) \
        VALUES ({id}, '{toss}') 
      }};""" ).execute()

    print (self.cursor.query(f""" USE cockroachdb_data {{ \
      SELECT * FROM {table_name}
      INNER JOIN cointoss
      ON {table_name}.id = cointoss.id
    }};""" ).execute())


def main():

  cursor = ConnectTest('ConnectTest', None).call()
  TableTest('CreateTable', cursor).call()
  InsertionTest('InsertValues', cursor).call()
  SelectAllTest('SelectAll', cursor).call()
  UpdateTest('UpdateTest', cursor).call()
  JoinTest('JoinTest', cursor).call()

if __name__ == "__main__":
  main()
