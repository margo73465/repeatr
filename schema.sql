drop table if exists videos;
create table videos (
  -- id integer primary key autoincrement,
  title text not null,
  video_id text primary key not null,
  -- image_link text not null,
  -- description text not null,
  play_count integer
);