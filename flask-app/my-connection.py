import mysql.connector
from mysql.connector import Error
#FUNCTION--------------------------------------------------------------------------
def create_server_connection(host_name, user_name, user_password):
  connection_server = None
  try:
    connection_server = mysql.connector.connect(
      host=host_name,
      user=user_name,
      passwd=user_password
    )
    print("MySQL Database server connection successful")
  except Error as err:
    print(f"Error: '{err}'")

  return connection_server
#-----------------------------------------------
def execute_query(connection_database, query):
  cursor = connection_database.cursor()
  try:
    cursor.execute(query)
    connection_database.commit()
    print("Query successful")
  except Error as err:
    print(f"Error: '{err}'")
#-----------------------------------------------
def create_database(connection_server, query):
  cursor = connection_server.cursor()
  try:
    cursor.execute(query)
    print("Database created successfully")
  except Error as err:
    print(f"Error: '{err}'")
#-----------------------------------------------
def create_db_connection(host_name, user_name, user_password, db_name):
  connection_database = None
  try:
    connection_database = mysql.connector.connect(
      host=host_name,
      user=user_name,
      passwd=user_password,
      database=db_name
    )
    print("MySQL Database connection successful")
  except Error as err:
    print(f"Error: '{err}'")
  return connection_database
#END OF FUNCTION--------------------------------------------------------------------------
create_table_user="""
CREATE TABLE IF NOT EXISTS USER
(   
    UserEmail   varchar(50)     NOT NULL,
    Username    varchar(20)     NOT NULL,
    UserRole    int     NOT NULL,   
    CONSTRAINT User_pk PRIMARY KEY (UserEmail)
);
"""
create_table_question="""
CREATE TABLE IF NOT EXISTS QUESTION
(   
    QuestionId      int     NOT NULL AUTO_INCREMENT,
    QuestionText    varchar(250)     NOT NULL,
    QuestionCode    varchar(50000)    NOT NULL,
    CorrectOutput   varchar(50)     NOT NULL,
    QuestionDate    date    NOT NULL,
    Difficulty      varchar(15) NOT NULL,
    UserEmail       varchar(50) NOT NULL,
    CONSTRAINT Question_pk PRIMARY KEY (QuestionId,UserEmail),
    CONSTRAINT Question_fk  FOREIGN KEY (UserEmail) REFERENCES USER(UserEmail)
);
"""
create_table_game="""
CREATE TABLE IF NOT EXISTS GAME
(
    UserEmail   varchar(50)     NOT NULL,
    QuestionId  int     NOT NULL,
    GameScore     int     NOT NULL,
    DatePlayed  date    NOT NULL,
    UserInput   varchar(1000)   NOT NULL,
    CONSTRAINT Game_pk PRIMARY KEY (DatePlayed,QuestionId,UserEmail),
    CONSTRAINT Game_fk1 FOREIGN KEY (QuestionId) REFERENCES QUESTION(QuestionId),
    CONSTRAINT Game_fk2 FOREIGN KEY (UserEmail) REFERENCES USER(UserEmail)
);
"""
insert_user1="""
INSERT INTO USER VALUES("admin@gmail.com","admin","2");
"""
insert_user2="""
INSERT INTO USER VALUES("mattiaautiero@gmail.com","mattia","2");
"""
insert_user3="""
INSERT INTO USER VALUES("flavioruggiero@gmail.com","flavio","2");
"""

insert_question1="""
INSERT INTO QUESTION VALUES("1","Return the maximum","int a=10, b=11, max=0;","11","2022-12-07 10:04:03","easy","admin@gmail.com");
"""
insert_question2="""
INSERT INTO QUESTION VALUES("2","Return the minimum","int a=10, b=11, min=0;","10","2022-12-07 10:03:03","amateur","admin@gmail.com");
"""
insert_question3="""
INSERT INTO QUESTION VALUES("3","Sort the array","int a[10]={10,2,3,9,19};","2,3,9,10,19","2022-12-07 10:02:03","hard","admin@gmail.com");
"""
#SELECT ADDTIME(CURTIME(), '0:5') serve ad aggiungere tempo all ora corrente da ricordare

insert_game1="""
INSERT INTO GAME VALUES("mattiaautiero@gmail.com","1","100","2022-12-07 12:04:03","if(a>b) max=a; else max=b; return max;");
"""
insert_game2="""
INSERT INTO GAME VALUES("flavioruggiero@gmail.com","2","100","2022-12-07 12:04:03","if(a<b) min=a; else min=b; return min;");
"""
insert_game3="""
INSERT INTO GAME VALUES("admin@gmail.com","3","0","2022-12-07 14:04:03","if(a[0]>a[1]) a[0]=a[1]");
"""
connection_server= create_server_connection ("localhost", "root","")
create_db_query="CREATE DATABASE IF NOT EXISTS frontlinecode"
create_database(connection_server,create_db_query)
connection_database = create_db_connection("localhost", "root", "","frontlinecode")
execute_query(connection_database, create_table_user)
execute_query(connection_database, create_table_question)
execute_query(connection_database, create_table_game)
execute_query(connection_database, insert_user1)
execute_query(connection_database, insert_user2)
execute_query(connection_database, insert_user3)
execute_query(connection_database, insert_question1)
execute_query(connection_database, insert_question2)
execute_query(connection_database, insert_question3)
execute_query(connection_database, insert_game1)
execute_query(connection_database, insert_game2)
execute_query(connection_database, insert_game3)
