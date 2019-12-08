CREATE TABLE stats(
   playerid int,
   hero text,
   eliminations numeric(8, 6),
   deaths numeric(8, 6),
   damage numeric(10, 6),
   healing numeric(10, 6),
   ultimates numeric(8, 6),
   final_blows numeric(8, 6),
   time_played numeric(12, 6),
   PRIMARY KEY (playerid, hero)
);

CREATE TABLE tempmapstats(
   name text,
   matchid int,
   map_number int,
   teamid int,
   playerid int,
   hero text,
   damage numeric(11, 6),
   deaths int,
   eliminations int,
   healing numeric(11, 6),
   PRIMARY KEY (matchid, map_number, playerid, hero)
);

CREATE TABLE matches(
   matchid int PRIMARY KEY,
   home int,
   away int,
   homescore int,
   awayscore int,
   startdate bigint,
   matchtime bigint,
   tournament text
);

CREATE TABLE maps(
   matchid int,
   map_number int,
   name text,
   type text,
   homescore int,
   awayscore int,
   gametime bigint,
   PRIMARY KEY (matchid, map_number)
);

CREATE TABLE teams(
   teamid int PRIMARY KEY,
   name text,
   city text,
   country varchar(3),
   abbreviation varchar(3),
   division varchar(8),
   divabbrev varchar(3),
   primary_color varchar(6),
   secondary_color varchar(6)
);

CREATE TABLE records(
   teamid int PRIMARY KEY,
   ranking int,
   matches_won int,
   matches_lost int,
   maps_won int,
   maps_lost int,
   maps_tied int
);