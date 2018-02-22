drop table if exists materials;
create table materials (
  id integer primary key autoincrement,
  name text not null,
  k real not null,
  cp real not null,
  rho real not null,
  T real not null
);
