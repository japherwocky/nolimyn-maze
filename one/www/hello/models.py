from django.db import models

# Create your models here.

"""
CREATE TABLE `helpfiles` (
  `id` int(11) NOT NULL auto_increment,
  `title` tinytext,
  `skill` tinytext,
  `minlevel` tinyint(3) unsigned default '0',
  `helpdata` text,
  `author` varchar(50) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=692 DEFAULT CHARSET=latin1;
"""

class Helpfile(models.Model):
	# id is autoint by default, iirc
	title = models.CharField(max_length=53, unique=True )
	legacy = models.CharField(max_length=53, db_column='skill' )
	minlevel = models.PositiveIntegerField()
	helpdata = models.TextField()
	author = models.ForeignKey('User')

