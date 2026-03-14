CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS action_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  description TEXT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS note_tags (
  note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  tag_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (note_id, tag_id)
);

INSERT INTO notes (title, content) VALUES
  ('Welcome', 'This is a starter note. TODO: explore the app! #onboarding'),
  ('Demo', 'Click around and add a note. Ship feature! #demo');

INSERT INTO action_items (description, completed) VALUES
  ('Try pre-commit', 0),
  ('Run tests', 0);

INSERT INTO tags (name) VALUES
  ('onboarding'),
  ('demo');

INSERT INTO note_tags (note_id, tag_id) VALUES
  (1, 1),
  (2, 2);
