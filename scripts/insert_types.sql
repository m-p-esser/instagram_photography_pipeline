# Insert Account Types
INSERT INTO USER.account_type 
VALUES 
   (1, 'Personal Account'),
   (2, 'Business Account'),
   (3, 'Creator Account');

# Insert Media Types
INSERT INTO MEDIA.media_type
VALUES
   (1, 'Photo'),
   (2, 'Video'),
   (8, 'Album');

# Video - When media_type=2 and product_type=feed
# IGTV - When media_type=2 and product_type=igtv
# Reel - When media_type=2 and product_type=clips
