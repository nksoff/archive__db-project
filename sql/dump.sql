/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Дамп таблицы Followers
# ------------------------------------------------------------

DROP TABLE IF EXISTS `Followers`;

CREATE TABLE `Followers` (
  `followee` varchar(45) NOT NULL,
  `follower` varchar(45) NOT NULL,
  UNIQUE KEY `both` (`followee`,`follower`),
  KEY `followee` (`followee`),
  KEY `follower` (`follower`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Дамп таблицы Forums
# ------------------------------------------------------------

DROP TABLE IF EXISTS `Forums`;

CREATE TABLE `Forums` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL DEFAULT '',
  `short_name` varchar(45) NOT NULL DEFAULT '',
  `user` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `short_name` (`short_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Дамп таблицы Posts
# ------------------------------------------------------------

DROP TABLE IF EXISTS `Posts`;

CREATE TABLE `Posts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message` text,
  `date` timestamp NULL DEFAULT NULL,
  `likes` int(11) NOT NULL DEFAULT '0',
  `dislikes` int(11) NOT NULL DEFAULT '0',
  `isApproved` tinyint(4) NOT NULL DEFAULT '1',
  `isHighlighted` tinyint(4) NOT NULL DEFAULT '0',
  `isEdited` tinyint(4) NOT NULL DEFAULT '0',
  `isSpam` tinyint(4) NOT NULL DEFAULT '0',
  `isDeleted` tinyint(4) NOT NULL DEFAULT '0',
  `parent` int(11) DEFAULT NULL,
  `user` varchar(45) NOT NULL,
  `thread` int(11) NOT NULL,
  `forum` varchar(45) NOT NULL,
  `sorter_date` varchar(80) NOT NULL DEFAULT '',
  `sorter` varchar(20) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `forum` (`forum`,`date`),
  KEY `thread` (`thread`,`date`),
  KEY `user` (`user`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Дамп таблицы Subscriptions
# ------------------------------------------------------------

DROP TABLE IF EXISTS `Subscriptions`;

CREATE TABLE `Subscriptions` (
  `thread` int(11) NOT NULL,
  `user` varchar(45) NOT NULL,
  UNIQUE KEY `both` (`thread`,`user`),
  KEY `thread` (`thread`),
  KEY `user` (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Дамп таблицы Threads
# ------------------------------------------------------------

DROP TABLE IF EXISTS `Threads`;

CREATE TABLE `Threads` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(45) NOT NULL DEFAULT '',
  `slug` varchar(45) NOT NULL DEFAULT '',
  `message` text,
  `date` timestamp NULL DEFAULT NULL,
  `likes` int(11) NOT NULL DEFAULT '0',
  `dislikes` int(11) NOT NULL DEFAULT '0',
  `isClosed` tinyint(4) NOT NULL DEFAULT '0',
  `isDeleted` tinyint(4) NOT NULL DEFAULT '0',
  `posts` int(11) NOT NULL DEFAULT '0',
  `forum` varchar(45) NOT NULL,
  `user` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user` (`user`,`date`),
  KEY `forum` (`forum`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Дамп таблицы Users
# ------------------------------------------------------------

DROP TABLE IF EXISTS `Users`;

CREATE TABLE `Users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(45) DEFAULT NULL,
  `about` text,
  `name` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `isAnonymous` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `email_2` (`email`,`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
