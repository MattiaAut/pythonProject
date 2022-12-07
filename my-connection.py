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
    QuestionTime    date    NOT NULL,
    Difficulty      varchar(15) NOT NULL,
    UserEmail       varchar(50) NOT NULL,
    CONSTRAINT Question_pk PRIMARY KEY (QuestionId),
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
    TimeSpent   date    NOT NULL,
    CONSTRAINT Game_pk PRIMARY KEY (DatePlayed),
    CONSTRAINT Game_fk1 FOREIGN KEY (QuestionId) REFERENCES QUESTION(QuestionId),
    CONSTRAINT Game_fk2 FOREIGN KEY (UserEmail) REFERENCES USER(UserEmail)
);
"""
insert_users="""
INSERT INTO USER VALUES("admin@gmail.com","admin","2");
INSERT INTO USER VALUES("mattiaautiero@gmail.com","mattia","2");
INSERT INTO USER VALUES("flavioruggiero@gmail.com","flavio","2");
"""

insert_questions="""
INSERT INTO QUESTION VALUES("1","Return the maximum","int a=10, b=11, max=0;","11","2022-12-07 10:04:03","easy","admin@gmail.com");
INSERT INTO QUESTION VALUES("2","Return the minimum","int a=10, b=11, min=0;","10","2022-12-07 10:03:03","amateur","admin@gmail.com");
INSERT INTO QUESTION VALUES("3","Sort the array","int a[10]={10,2,3,9,19};","2,3,9,10,19","2022-12-07 10:02:03","hard","admin@gmail.com")
"""

#SELECT ADDTIME(CURTIME(), '0:5') serve ad aggiungere tempo all ora corrente da ricordare
insert_games="""
INSERT INTO GAME VALUES("mattiaautiero@gmail.com","1","100","")
"""
connection_server= create_server_connection ("localhost", "root","")
create_db_query="CREATE DATABASE IF NOT EXISTS frontlinecode"
create_database(connection_server,create_db_query)
connection_database = create_db_connection("localhost", "root", "","frontlinecode")
execute_query(connection_database, create_table_user)
execute_query(connection_database, create_table_question)
execute_query(connection_database, create_table_game)
