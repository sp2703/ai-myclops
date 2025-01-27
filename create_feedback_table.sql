CREATE TABLE query_feedback (
    auto_id BIGINT AUTO_INCREMENT,
    question TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    feedback BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (auto_id)
);