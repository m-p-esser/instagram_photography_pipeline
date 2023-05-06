CREATE SCHEMA `USER`;

CREATE SCHEMA `LOCATION`;

CREATE SCHEMA `MEDIA`;

CREATE SCHEMA `STATISTIC`;

CREATE TABLE `USER`.`user` (
  `user_id` integer PRIMARY KEY,
  `user_name` varchar(255) UNIQUE NOT NULL,
  `full_name` varchar(255) DEFAULT null,
  `is_verified` bool NOT NULL,
  `account_type` int DEFAULT null,
  `is_business` bool NOT NULL,
  `business_category_name` varchar(255) DEFAULT null,
  `category_name` varchar(255) DEFAULT null,
  `category` varchar(255) DEFAULT null,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `USER`.`user_profile_setting` (
  `user_id` integer PRIMARY KEY,
  `profile_pic_url` varchar(255) UNIQUE NOT NULL,
  `profile_pic_url_hd` varchar(255),
  `has_profile_pic` bool NOT NULL,
  `bio` varchar(255) DEFAULT null,
  `has_bio` bool NOT NULL,
  `is_private` bool NOT NULL,
  `external_url` varchar(255) COMMENT 'External URL the Bio is linking to',
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

CREATE TABLE `USER`.`user_type` (
  `user_id` integer PRIMARY KEY,
  `user_type` varchar(255)
);

CREATE TABLE `USER`.`follower` (
  `user_id` integer NOT NULL,
  `follower_id` integer NOT NULL COMMENT 'User which is following the account'
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
  `website_url` varchar(255) DEFAULT null,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `MEDIA`.`story` (
  `story_id` integer PRIMARY KEY,
  `user_id` integer,
  `media_id` integer,
  `thumbnail_url` varchar(255) DEFAULT null,
  `video_url` varchar(255) DEFAULT null,
  `video_duration_seconds` decimal(9,6) DEFAULT null,
  `product_type` varchar(255) DEFAULT null,
  `publication_datetime` datetime NOT NULL,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `MEDIA`.`story_mention` (
  `story_id` integer NOT NULL,
  `user_id` integer NOT NULL,
  `is_sponsor` bool NOT NULL DEFAULT False
);

CREATE TABLE `MEDIA`.`story_location` (
  `story_id` integer NOT NULL,
  `location_id` integer NOT NULL
);

CREATE TABLE `MEDIA`.`story_hashtag` (
  `story_id` integer NOT NULL,
  `hashtag_id` integer NOT NULL
);

CREATE TABLE `MEDIA`.`story_media` (
  `story_id` integer NOT NULL,
  `media_id` integer NOT NULL
);

CREATE TABLE `MEDIA`.`media` (
  `media_id` integer PRIMARY KEY,
  `user_id` integer,
  `location_id` integer,
  `title` varchar(255) DEFAULT null,
  `caption` varchar(255) DEFAULT null,
  `thumbnail_url` varchar(255) DEFAULT null,
  `product_type` varchar(255) DEFAULT null,
  `video_url` varchar(255) DEFAULT null,
  `video_duration_seconds` decimal(9,6) DEFAULT null,
  `has_comments_disabled` bool NOT NULL,
  `publication_datetime` datetime NOT NULL,
  `created_at` timestamp default CURRENT_TIMESTAMP NOT NULL COMMENT 'create time',
  `updated_at` datetime default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL COMMENT 'update time'
);

CREATE TABLE `MEDIA`.`media_usertag` (
  `media_id` integer NOT NULL,
  `user_id` integer NOT NULL
);

CREATE TABLE `MEDIA`.`media_hashtag` (
  `media_id` integer NOT NULL,
  `hashtag_id` integer NOT NULL
);

CREATE TABLE `MEDIA`.`media_sponsor` (
  `media_id` integer NOT NULL,
  `user_id` integer NOT NULL
);

CREATE TABLE `MEDIA`.`media_type` (
  `media_id` integer PRIMARY KEY,
  `media_name` varchar(255)
);

CREATE TABLE `MEDIA`.`hashtag` (
  `hashtag_id` integer PRIMARY KEY,
  `hashtag_name` varchar(255) UNIQUE NOT NULL,
  `profile_pic_url` varchar(255)
);

CREATE TABLE `MEDIA`.`related_hashtag` (
  `id` integer PRIMARY KEY,
  `hashtag_id` integer,
  `related_hashtag_id` integer
);

CREATE TABLE `STATISTIC`.`user_cumulated_statistic` (
  `user_id` integer NOT NULL,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_follower_count` integer NOT NULL COMMENT 'Number of accounts that are following this account',
  `cumulated_following_count` integer NOT NULL COMMENT 'Number of accounts the account is following',
  `cumulated_media_count` integer NOT NULL
);

CREATE TABLE `STATISTIC`.`media_cumulated_statistic` (
  `media_id` integer NOT NULL,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_like_count` integer NOT NULL DEFAULT 0,
  `cumulated_comment_count` integer NOT NULL DEFAULT 0,
  `cumulated_play_count` integer NOT NULL DEFAULT 0,
  `cumulated_view_count` integer NOT NULL DEFAULT 0,
  `cumulated_mention_count` integer NOT NULL DEFAULT 0
);

CREATE TABLE `STATISTIC`.`story_cumulated_statistic` (
  `story_id` integer NOT NULL,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_like_count` integer NOT NULL DEFAULT 0,
  `cumulated_comment_count` integer NOT NULL DEFAULT 0,
  `cumulated_play_count` integer NOT NULL DEFAULT 0,
  `cumulated_mention_count` integer NOT NULL DEFAULT 0
);

CREATE TABLE `STATISTIC`.`location_cumulated_statistic` (
  `location_id` integer NOT NULL,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_like_count` integer NOT NULL DEFAULT 0
);

CREATE TABLE `STATISTIC`.`hashtag_cumulated_statistic` (
  `hashtag_id` integer PRIMARY KEY,
  `statistic_date` date NOT NULL COMMENT 'Date the Statistics are referring to',
  `cumulated_media_count` integer NOT NULL DEFAULT 1
);

ALTER TABLE `USER`.`user_adress` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`);

ALTER TABLE `USER`.`user_profile_setting` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`);

ALTER TABLE `USER`.`user_contact_details` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`);

ALTER TABLE `USER`.`user_type` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`);

ALTER TABLE `USER`.`follower` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`);

ALTER TABLE `LOCATION`.`location` ADD FOREIGN KEY (`location_id`) REFERENCES `USER`.`user_adress` (`location_id`);

ALTER TABLE `STATISTIC`.`user_cumulated_statistic` ADD FOREIGN KEY (`user_id`) REFERENCES `USER`.`user` (`user_id`);

ALTER TABLE `LOCATION`.`location_contact_details` ADD FOREIGN KEY (`location_id`) REFERENCES `LOCATION`.`location` (`location_id`);

ALTER TABLE `STATISTIC`.`location_cumulated_statistic` ADD FOREIGN KEY (`location_id`) REFERENCES `LOCATION`.`location` (`location_id`);

ALTER TABLE `MEDIA`.`media_type` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`media` (`media_id`);

ALTER TABLE `MEDIA`.`media_sponsor` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`media` (`media_id`);

ALTER TABLE `MEDIA`.`media_hashtag` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`media` (`media_id`);

ALTER TABLE `MEDIA`.`media_usertag` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`media` (`media_id`);

ALTER TABLE `MEDIA`.`hashtag` ADD FOREIGN KEY (`hashtag_id`) REFERENCES `MEDIA`.`media_hashtag` (`hashtag_id`);

ALTER TABLE `USER`.`user` ADD FOREIGN KEY (`user_id`) REFERENCES `MEDIA`.`media_sponsor` (`user_id`);

ALTER TABLE `USER`.`user` ADD FOREIGN KEY (`user_id`) REFERENCES `MEDIA`.`media_usertag` (`user_id`);

ALTER TABLE `STATISTIC`.`media_cumulated_statistic` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`media` (`media_id`);

ALTER TABLE `MEDIA`.`media_type` ADD FOREIGN KEY (`media_id`) REFERENCES `MEDIA`.`story` (`media_id`);

ALTER TABLE `MEDIA`.`story_mention` ADD FOREIGN KEY (`story_id`) REFERENCES `MEDIA`.`story` (`story_id`);

ALTER TABLE `MEDIA`.`story_location` ADD FOREIGN KEY (`story_id`) REFERENCES `MEDIA`.`story` (`story_id`);

ALTER TABLE `MEDIA`.`story_hashtag` ADD FOREIGN KEY (`story_id`) REFERENCES `MEDIA`.`story` (`story_id`);

ALTER TABLE `USER`.`user` ADD FOREIGN KEY (`user_id`) REFERENCES `MEDIA`.`story_mention` (`user_id`);

ALTER TABLE `LOCATION`.`location` ADD FOREIGN KEY (`location_id`) REFERENCES `MEDIA`.`story_location` (`location_id`);

ALTER TABLE `MEDIA`.`hashtag` ADD FOREIGN KEY (`hashtag_id`) REFERENCES `MEDIA`.`story_hashtag` (`hashtag_id`);

ALTER TABLE `STATISTIC`.`story_cumulated_statistic` ADD FOREIGN KEY (`story_id`) REFERENCES `MEDIA`.`story` (`story_id`);

ALTER TABLE `MEDIA`.`related_hashtag` ADD FOREIGN KEY (`hashtag_id`) REFERENCES `MEDIA`.`hashtag` (`hashtag_id`);

ALTER TABLE `STATISTIC`.`hashtag_cumulated_statistic` ADD FOREIGN KEY (`hashtag_id`) REFERENCES `MEDIA`.`hashtag` (`hashtag_id`);
