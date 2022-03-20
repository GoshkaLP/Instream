CREATE TABLE Channels (
    id VARCHAR (30) NOT NULL,
    username VARCHAR (32) NOT NULL,
    name VARCHAR (128) NOT NULL,
    photo BYTEA,
    subscribers INT NOT NULL,

    PRIMARY KEY (id)
);


CREATE TABLE AnnouncedStreams (
    id VARCHAR (30) NOT NULL,
    channel_id VARCHAR (32) NOT NULL,
    scheduled_date TIMESTAMP NOT NULL,

    PRIMARY KEY (id),
    FOREIGN KEY (channel_id) REFERENCES Channels (id)

);


CREATE TABLE CurrentStreams (
    id VARCHAR (30) NOT NULL,
    channel_id VARCHAR (32) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    scheduled BOOLEAN DEFAULT FALSE,

    PRIMARY KEY (id),
    FOREIGN KEY (channel_id) REFERENCES Channels (id)
);


CREATE TABLE FinishedStreams (
    id VARCHAR (30) NOT NULL,
    channel_id VARCHAR (32) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    viewers_count INT NOT NULL,
    duration INT NOT NULL,
    scheduled BOOLEAN DEFAULT FALSE,

    PRIMARY KEY (id),
    FOREIGN KEY (channel_id) REFERENCES Channels (id)
);
