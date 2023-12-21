CREATE TABLE Business.`restaurants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `review_count` int DEFAULT NULL,
  `rating` decimal(3,1) DEFAULT NULL,
  `transactions` varchar(50) DEFAULT NULL,
  `price` varchar(10) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `display_phone` varchar(15) DEFAULT NULL,
  `latitude` decimal(10,6) DEFAULT NULL,
  `longitude` decimal(10,6) DEFAULT NULL,
  `foodtype` varchar(80) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(2) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `audit_date` date DEFAULT (curdate()),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `prices` (
  `price_id` int NOT NULL,
  `price` varchar(5) DEFAULT NULL,
  `price_desc` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`price_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `food_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `food_type` varchar(80) DEFAULT NULL,
  `food_type_desc` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_food_type` (`food_type`)
) ENGINE=InnoDB AUTO_INCREMENT=255 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `transaction` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`transaction_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE EVENT Business.update_transactions_event
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
	UPDATE Business.restaurants
	SET transactions = (
		SELECT GROUP_CONCAT(DISTINCT transaction ORDER BY transaction SEPARATOR ', ')
		FROM (
			SELECT DISTINCT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(transactions, ',', n.digit + 1), ',', -1)) AS transaction
			, id
			FROM Business.restaurants
			JOIN (
				SELECT 0 AS digit
				UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
			) n ON CHAR_LENGTH(transactions) - CHAR_LENGTH(REPLACE(transactions, ',', '')) >= n.digit
		) sorted_transactions
		WHERE restaurants.id = sorted_transactions.id
);

ALTER EVENT Business.update_transactions_event ENABLE;

CREATE EVENT Business.update_food_types
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
	INSERT INTO Business.food_types (food_type)
	SELECT DISTINCT foodtype FROM Business.restaurants
	ON DUPLICATE KEY UPDATE food_type = foodtype
;

ALTER EVENT Business.update_food_types ENABLE;

CREATE EVENT Business.update_transactions
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
	INSERT INTO Business.transactions (transaction)
	SELECT DISTINCT transactions FROM Business.restaurants
	ON DUPLICATE KEY UPDATE transaction = transactions
;

ALTER EVENT Business.update_transactions ENABLE;






