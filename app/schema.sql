CREATE TABLE if not EXISTS share_contents (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    preview TEXT NOT NULL,
    contents BLOB NOT NULL,
    modified INTEGER NOT NULL
);