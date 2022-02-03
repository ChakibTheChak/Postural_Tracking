create database postulartracker;
use postulartracker;

CREATE TABLE author (
  Name VARCHAR(20),
  Version VARCHAR(8),
  Date DATETIME DEFAULT CURRENT_TIMESTAMP
  );

INSERT INTO test_table
  (name, Version)
VALUES
  ('Chakib', '0.1');
 