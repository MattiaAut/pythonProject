CREATE DATABASE IF NOT EXISTS FRONTLINECODE;

CREATE TABLE IF NOT EXISTS USER
(
    UserEmail   varchar(50)     NOT NULL,
    Username    varchar(20)     NOT NULL,
    UserRole    int     NOT NULL,
    PRIMARY KEY (UserEmail)
);

CREATE TABLE IF NOT EXISTS QUESTION
(
    QuestionId      int     NOT NULL AUTO_INCREMENT,
    QuestionText    varchar(250)     NOT NULL,
    QuestionCode    varchar(50000)    NOT NULL,
    CorrectOutput   varchar(50)     NOT NULL,
    QuestionDate    date    NOT NULL,
    Difficulty      varchar(15) NOT NULL,
    UserEmail       varchar(50) NOT NULL,
    PRIMARY KEY (QuestionId,UserEmail),
    FOREIGN KEY (UserEmail) REFERENCES USER(UserEmail)
);
CREATE TABLE IF NOT EXISTS GAME
(
    UserEmail   varchar(50)     NOT NULL,
    QuestionId  int     NOT NULL,
    GameScore     int     NOT NULL,
    DatePlayed  date    NOT NULL,
    UserInput   varchar(1000)   NOT NULL,
    PRIMARY KEY (DatePlayed,QuestionId,UserEmail),
    FOREIGN KEY (QuestionId) REFERENCES QUESTION(QuestionId),
    FOREIGN KEY (UserEmail) REFERENCES USER(UserEmail)
);
INSERT INTO USER VALUES("admin@gmail.com","admin","2");
INSERT INTO USER VALUES("mattiaautiero@gmail.com","mattia","2");
INSERT INTO USER VALUES("flavioruggiero@gmail.com","flavio","2");

INSERT INTO QUESTION VALUES("1","Return the maximum","int a=10, b=11, max=0;","11","2022-12-07 10:04:03","easy","admin@gmail.com");
INSERT INTO QUESTION VALUES("2","Return the minimum","int a=10, b=11, min=0;","10","2022-12-07 10:03:03","amateur","admin@gmail.com");
INSERT INTO QUESTION VALUES("3","Sort the array","int a[10]={10,2,3,9,19};","2,3,9,10,19","2022-12-07 10:02:03","hard","admin@gmail.com");

INSERT INTO GAME VALUES("mattiaautiero@gmail.com","1","100","2022-12-07 12:04:03","if(a>b) max=a; else max=b; return max;");
INSERT INTO GAME VALUES("flavioruggiero@gmail.com","2","100","2022-12-07 12:04:03","if(a<b) min=a; else min=b; return min;");
INSERT INTO GAME VALUES("admin@gmail.com","3","0","2022-12-07 14:04:03","if(a[0]>a[1]) a[0]=a[1]");