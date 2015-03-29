drop table if exists videos;
create table videos (
  -- id integer primary key autoincrement,
  video_id text primary key not null,
  title text not null,
  description text not null,
  thumbnail_url text not null,
  play_count integer
);