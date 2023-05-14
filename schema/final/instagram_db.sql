CREATE SCHEMA `USER` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

CREATE SCHEMA `LOCATION` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;;

CREATE SCHEMA `MEDIA` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;;

CREATE SCHEMA `STATISTIC` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;;

CREATE TABLE `USER`.`user` (
  `user_id` integer PRIMARY KEY,
  `account_type_id` int DEFAULT null,
  `user_name` varchar(255) UNIQUE NOT NULL,
  `full_name` varchar(255) DEFAULT null,
  `is_verified` bool NOT NULL,
  `is_business` bool NOT NULL,
  `business_category_name` varchar(255) DEFAULT null,
  `category_name` varchar(255) DEFAULT null,
  `category` varchar(255) DEFAULT null,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `USER`.`user_profile_setting` (
  `user_id` integer PRIMARY KEY,
  `profile_pic_url` varchar(2000) UNIQUE NOT NULL,
  `profile_pic_url_hd` varchar(2000),
  `has_profile_pic` bool NOT NULL,
  `has_bio` bool NOT NULL,
  `bio` varchar(255) DEFAULT null,
  `is_private` bool NOT NULL,
  `external_url` varchar(2000) COMMENT 'External URL the Bio is linking to',
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `USER`.`user_contact_details` (
  `user_id` integer PRIMARY KEY,
  `contact_phone_number` varchar(255) DEFAULT null,
  `public_phone_number` varchar(255) DEFAULT null,
  `public_phone_country_code` varchar(255) DEFAULT null,
  `business_contact_method` varchar(255) DEFAULT null,
  `public_email` varchar(255) DEFAULT null,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `USER`.`user_adress` (
  `user_id` integer PRIMARY KEY,
  `location_id` integer,
  `longitude` decimal(9,6) DEFAULT null,
  `latitude` decimal(8,6) DEFAULT null,
  `street` varchar(255) DEFAULT null,
  `city` varchar(255) DEFAULT null,
  `zip` varchar(255) DEFAULT null,
  `country` varchar(255) DEFAULT null,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `USER`.`account_type` (
  `account_type_id` integer PRIMARY KEY,
  `account_type` varchar(255) NOT NULL
);

CREATE TABLE `USER`.`follower` (
  `user_id` integer NOT NULL,
  `follower_id` integer NOT NULL COMMENT 'User which is following the account',
  PRIMARY KEY (`user_id`, `follower_id`)
);

CREATE TABLE `LOCATION`.`location` (
  `location_id` integer PRIMARY KEY,
  `name` varchar(255) NOT NULL,
  `category` varchar(255) DEFAULT null,
  `longitude` decimal(9,6) DEFAULT null,
  `latitude` decimal(8,6) DEFAULT null,
  `street` varchar(255) DEFAULT null,
  `city` varchar(255) DEFAULT null,
  `zip` varchar(255) DEFAULT null,
  `country` varchar(255) DEFAULT null,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `LOCATION`.`location_contact_details` (
  `location_id` integer PRIMARY KEY,
  `phone_number` varchar(255) DEFAULT null,
  `opening_hours` varchar(255) DEFAULT null,
  `website_url` varchar(2000) DEFAULT null,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `MEDIA`.`story` (
  `story_id` integer PRIMARY KEY,
  `user_id` integer NOT NULL,
  `media_id` integer NOT NULL,
  `media_type_id` integer,
  `thumbnail_url` varchar(2000) DEFAULT null,
  `video_url` varchar(2000) DEFAULT null,
  `video_duration_seconds` decimal(9,6) DEFAULT null,
  `product_type` varchar(255) DEFAULT null,
  `publication_datetime` datetime NOT NULL,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `MEDIA`.`story_mention` (
  `story_id` integer NOT NULL,
  `user_id` integer NOT NULL,
  `is_sponsor` bool NOT NULL DEFAULT False,
  PRIMARY KEY (`story_id`, `user_id`)
);

CREATE TABLE `MEDIA`.`story_location` (
  `story_id` integer NOT NULL,
  `location_id` integer NOT NULL,
  PRIMARY KEY (`story_id`, `location_id`)
);

CREATE TABLE `MEDIA`.`story_hashtag` (
  `story_id` integer NOT NULL,
  `hashtag_id` integer NOT NULL,
  PRIMARY KEY (`story_id`, `hashtag_id`)
);

CREATE TABLE `MEDIA`.`story_media` (
  `story_id` integer NOT NULL,
  `media_id` integer NOT NULL,
  PRIMARY KEY (`story_id`, `media_id`)
);

CREATE TABLE `MEDIA`.`media` (
  `media_id` integer PRIMARY KEY,
  `user_id` integer NOT NULL,
  `location_id` integer,
  `media_type_id` integer,
  `title` varchar(255) DEFAULT null,
  `caption` varchar(255) DEFAULT null,
  `thumbnail_url` varchar(2000) DEFAULT null,
  `product_type` varchar(255) DEFAULT null,
  `video_url` varchar(2000) DEFAULT null,
  `video_duration_seconds` decimal(9,6) DEFAULT null,
  `has_comments_disabled` bool NOT NULL,
  `publication_datetime` datetime NOT NULL,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `MEDIA`.`media_usertag` (
  `media_id` integer NOT NULL,
  `user_id` integer NOT NULL,
  PRIMARY KEY (`media_id`, `user_id`)
);

CREATE TABLE `MEDIA`.`media_hashtag` (
  `media_id` integer NOT NULL,
  `hashtag_id` integer NOT NULL,
  PRIMARY KEY (`media_id`, `hashtag_id`)
);

CREATE TABLE `MEDIA`.`media_sponsor` (
  `media_id` integer NOT NULL,
  `user_id` integer NOT NULL,
  PRIMARY KEY (`media_id`, `user_id`)
);

CREATE TABLE `MEDIA`.`media_type` (
  `media_type_id` integer PRIMARY KEY,
  `type` varchar(255)
);

CREATE TABLE `MEDIA`.`hashtag` (
  `hashtag_id` integer PRIMARY KEY,
  `hashtag_name` varchar(255) UNIQUE NOT NULL,
  `profile_pic_url` varchar(2000),
  `has_profile_pic` bool NOT NULL
);

CREATE TABLE `MEDIA`.`related_hashtag` (
  `hashtag_id` integer NOT NULL,
  `related_hashtag_id` integer,
  PRIMARY KEY (`hashtag_id`, `related_hashtag_id`)
);

CREATE TABLE `STATISTIC`.`user_cumulated_statistic` (
  `user_id` integer NOT NULL,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_follower_count` integer NOT NULL COMMENT 'Number of accounts that are following this account',
  `cumulated_following_count` integer NOT NULL COMMENT 'Number of accounts the account is following',
  `cumulated_media_count` integer NOT NULL,
  PRIMARY KEY (`statistic_date`, `user_id`)
);

CREATE TABLE `STATISTIC`.`media_cumulated_statistic` (
  `media_id` integer NOT NULL,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_like_count` integer NOT NULL DEFAULT 0,
  `cumulated_comment_count` integer NOT NULL DEFAULT 0,
  `cumulated_play_count` integer NOT NULL DEFAULT 0,
  `cumulated_view_count` integer NOT NULL DEFAULT 0,
  `cumulated_mention_count` integer NOT NULL DEFAULT 0,
  PRIMARY KEY (`statistic_date`, `media_id`)
);

CREATE TABLE `STATISTIC`.`story_cumulated_statistic` (
  `story_id` integer NOT NULL,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_like_count` integer NOT NULL DEFAULT 0,
  `cumulated_comment_count` integer NOT NULL DEFAULT 0,
  `cumulated_play_count` integer NOT NULL DEFAULT 0,
  `cumulated_mention_count` integer NOT NULL DEFAULT 0,
  PRIMARY KEY (`statistic_date`, `story_id`)
);

CREATE TABLE `STATISTIC`.`location_cumulated_statistic` (
  `location_id` integer NOT NULL,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_like_count` integer NOT NULL DEFAULT 0,
  PRIMARY KEY (`statistic_date`, `location_id`)
);

CREATE TABLE `STATISTIC`.`hashtag_cumulated_statistic` (
  `hashtag_id` integer NOT NULL,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_media_count` integer NOT NULL DEFAULT 1,
  PRIMARY KEY (`statistic_date`, `hashtag_id`)
);

CREATE INDEX `user_name_index` ON `USER`.`user` (`user_name`);

CREATE INDEX `account_type_index` ON `USER`.`user` (`account_type_id`);

CREATE INDEX `full_name_index` ON `USER`.`user` (`full_name`);

CREATE INDEX `created_at_index` ON `USER`.`user` (`created_at`);

CREATE INDEX `updated_at_index` ON `USER`.`user` (`updated_at`);

CREATE INDEX `has_bio_bio_index` ON `USER`.`user_profile_setting` (`has_bio`, `bio`);

CREATE INDEX `is_privat_index` ON `USER`.`user_profile_setting` (`is_private`);

CREATE INDEX `created_at_index` ON `USER`.`user_profile_setting` (`created_at`);

CREATE INDEX `updated_at_index` ON `USER`.`user_profile_setting` (`updated_at`);

CREATE INDEX `created_at_index` ON `USER`.`user_contact_details` (`created_at`);

CREATE INDEX `updated_at_index` ON `USER`.`user_contact_details` (`updated_at`);

CREATE INDEX `location_id_index` ON `USER`.`user_adress` (`location_id`);

CREATE INDEX `country_city_index` ON `USER`.`user_adress` (`country`, `city`);

CREATE INDEX `created_at_index` ON `USER`.`user_adress` (`created_at`);

CREATE INDEX `updated_at_index` ON `USER`.`user_adress` (`updated_at`);

CREATE UNIQUE INDEX `account_type_index` ON `USER`.`account_type` (`account_type`);

CREATE INDEX `name_index` ON `LOCATION`.`location` (`name`);

CREATE INDEX `country_city_index` ON `LOCATION`.`location` (`country`, `city`);

CREATE INDEX `created_at_index` ON `LOCATION`.`location` (`created_at`);

CREATE INDEX `updated_at_index` ON `LOCATION`.`location` (`updated_at`);

CREATE INDEX `created_at_index` ON `LOCATION`.`location_contact_details` (`created_at`);

CREATE INDEX `updated_at_index` ON `LOCATION`.`location_contact_details` (`updated_at`);

CREATE INDEX `user_id_index` ON `MEDIA`.`story` (`user_id`);

CREATE INDEX `media_id_index` ON `MEDIA`.`story` (`media_id`);

CREATE INDEX `media_type_id_index` ON `MEDIA`.`story` (`media_type_id`);

CREATE INDEX `video_duration_seconds_index` ON `MEDIA`.`story` (`video_duration_seconds`);

CREATE INDEX `publication_datetime_index` ON `MEDIA`.`story` (`publication_datetime`);

CREATE INDEX `created_at_index` ON `MEDIA`.`story` (`created_at`);

CREATE INDEX `updated_at_index` ON `MEDIA`.`story` (`updated_at`);

CREATE INDEX `user_id_index` ON `MEDIA`.`media` (`user_id`);

CREATE INDEX `location_id_index` ON `MEDIA`.`media` (`location_id`);

CREATE INDEX `media_type_id_index` ON `MEDIA`.`media` (`media_type_id`);

CREATE INDEX `video_duration_seconds_index` ON `MEDIA`.`media` (`video_duration_seconds`);

CREATE INDEX `publication_datetime_index` ON `MEDIA`.`media` (`publication_datetime`);

CREATE INDEX `created_at_index` ON `MEDIA`.`media` (`created_at`);

CREATE INDEX `updated_at_index` ON `MEDIA`.`media` (`updated_at`);

CREATE UNIQUE INDEX `type_index` ON `MEDIA`.`media_type` (`type`);

CREATE INDEX `hashtag_name_index` ON `MEDIA`.`hashtag` (`hashtag_name`);

CREATE INDEX `has_profile_pic_index` ON `MEDIA`.`hashtag` (`has_profile_pic`);

ALTER TABLE `USER`.`user_adress` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `USER`.`user_profile_setting` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `USER`.`user_contact_details` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `USER`.`user` ADD FOREIGN KEY (`account_type_id`) REFERENCES `USER`.`account_type` (`account_type_id`) ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE `USER`.`follower` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `USER`.`user_adress` ADD FOREIGN KEY (`location_id`) REFERENCES `LOCATION`.`location` (`location_id`);

ALTER TABLE `STATISTIC`.`user_cumulated_statistic` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `LOCATION`.`location_contact_details` ADD FOREIGN KEY (`location_id`) REFERENCES `LOCATION`.`location` (`location_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `STATISTIC`.`location_cumulated_statistic` ADD FOREIGN KEY (`location_id`) REFERENCES `LOCATION`.`location` (`location_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`media` ADD FOREIGN KEY (`media_type_id`) REFERENCES `MEDIA`.`media_type` (`media_type_id`) ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`media_sponsor` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`media` (`media_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`media_hashtag` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`media` (`media_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`media_usertag` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`media` (`media_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`media_hashtag` ADD FOREIGN KEY (`hashtag_id`) REFERENCES `MEDIA`.`hashtag` (`hashtag_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`media_sponsor` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`media_usertag` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `STATISTIC`.`media_cumulated_statistic` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`media` (`media_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`story` ADD FOREIGN KEY (`media_type_id`) REFERENCES `MEDIA`.`media_type` (`media_type_id`) ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`story_mention` ADD FOREIGN KEY (`story_id`) REFERENCES `MEDIA`.`story` (`story_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`story_location` ADD FOREIGN KEY (`story_id`) REFERENCES `MEDIA`.`story` (`story_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`story_hashtag` ADD FOREIGN KEY (`story_id`) REFERENCES `MEDIA`.`story` (`story_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`story_mention` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`story_location` ADD FOREIGN KEY (`location_id`) REFERENCES `LOCATION`.`location` (`location_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`story_hashtag` ADD FOREIGN KEY (`hashtag_id`) REFERENCES `MEDIA`.`hashtag` (`hashtag_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `STATISTIC`.`story_cumulated_statistic` ADD FOREIGN KEY (`story_id`) REFERENCES `MEDIA`.`story` (`story_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `MEDIA`.`related_hashtag` ADD FOREIGN KEY (`hashtag_id`) REFERENCES `MEDIA`.`hashtag` (`hashtag_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `STATISTIC`.`hashtag_cumulated_statistic` ADD FOREIGN KEY (`hashtag_id`) REFERENCES `MEDIA`.`hashtag` (`hashtag_id`) ON DELETE CASCADE ON UPDATE CASCADE;
