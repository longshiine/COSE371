drop table post_comment;
drop table user_post;
drop table comment;
drop table post;
drop table board;
drop table users;
drop table auth;

create table auth(
	auth_code numeric(3,0),
	type varchar(30) not null, 
	primary key(auth_code)
);

create table users(
	user_id varchar(20), 
	password varchar(20),
	name varchar(20) not null,
	auth_code numeric(3,0),
	primary key(user_id),
	foreign key(auth_code) references auth(auth_code)
);

create table board(
	board_id varchar(20),
	access numeric(3,0),
	primary key(board_id),
	foreign key (access) references auth(auth_code)
);

create table post(
	post_id int,
	board_id varchar(20),
	user_id varchar(20),
	date timestamp,
	title varchar(100),
	content text,
	likes int,
	primary key (post_id),
	foreign key (board_id) references board(board_id),
	foreign key (user_id) references users(user_id)
);

create table comment(
	comment_id int,
	post_id int,
	user_id varchar(20),
	date timestamp,
	content varchar(200),
	primary key (comment_id),
	foreign key (post_id) references post(post_id),
	foreign key (user_id) references users(user_id)
); 

create table user_post(
	user_id varchar(20),
	post_id int,
	primary key	(user_id, post_id),
	foreign key (user_id) references users(user_id),
	foreign key (post_id) references post(post_id)
);

create table post_comment(
	post_id int,
	comment_id int,
	primary key	(post_id, comment_id),
	foreign key (post_id) references post(post_id),
	foreign key (comment_id) references comment(comment_id)
);

-- insert auth options
insert into auth values (001, '학생');
insert into auth values (002, '조교');
insert into auth values (003, '교수');
-- insert default boards
insert into board values ('자유질문', 001); -- id=1
insert into board values ('조교게시판', 002); -- id=2
-- insert admin user
insert into users values ('prof', '1234', '교수님', 003);
insert into users values ('assist', '1234', '조교', 002);
insert into users values ('stu', '1234', '학생', 001);
-- insert initial post
insert into post values (1, '자유질문', 'prof', now(), '기말고사 공지 + 강의 일정 안내', 
'- 6/10 목요일 10:30-12:00 기말고사 실시
- 학교 강의실에서 대면 시험을 실시합니다. 
  (시험 강의실 추후 공지합니다. 학번 기준으로 여러 강의실에서 시험이 치뤄집니다.)
- 시험 범위는 중간고사 이후 강의 분량입니다. 4, 6, 11장 강의 내용
- 대면시험이 불가한 학생은 6/8 강의 시간 이전까지 저에게 이메일로 연락바랍니다.
  (ydchung@korea.ac.kr)

- 향후 일정
6/3    휴강
6/8    질의 응답
6/10  기말고사
6/15  관계형데이터베이스 설계 (정규화) 강의
6/18  관계형데이터베이스 설계 (정규화) 강의 (계속)'
, 0);
insert into user_post values ('prof', 1);

insert into post values (2, '자유질문', 'assist', now(), '중간고사 성적 공지', 
'총원: 145명
응시 인원: 142명
결시 인원: 3명

만점: 96점
최고점: 83점
평균: 47.16점'
, 0);
insert into user_post values ('assist', 2);

insert into post values (3, '자유질문', 'stu', now(), 'OLAP 실습관련 질문드립니다!', 
'질문드립니다!'
, 0);
insert into user_post values ('stu', 3);

-- insert initial comment
insert into comment values (1, 1, 'prof', now(), '교수님 테스트 댓글');
insert into post_comment values (1, 1);
insert into comment values (2, 1, 'assist', now(), '조교 테스트 댓글');
insert into post_comment values (1, 2);
insert into comment values (3, 1, 'stu', now(), '학생 테스트 댓글');
insert into post_comment values (1, 3);
