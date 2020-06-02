# Hoply (DM564 Exam project)
---

### Phase 1 - The Local Database (here)
In this first phase, you are to design, implement, and make accessible to your
application a local database storing information on users of the application,
on posts, and on comments to posts. If you are developing an Android
application, using Android Room could be a good choice.

### Phase 2 - Basic Features
Based on the local database from Phase 1, you are to design, implement, and
test the 3 basic features:
 - Creating a user.  
 - Creating a post.  
 - Commenting on a post.  

You are free regarding the design of your user interface. You can both pro-
gram the interface or specify it declaritively, e.g., using XML files.
For more details on the basic features, see the slides regarding the project
under Course Materials on Blackboard.

### Phase 3 - Synchronization with the remote database
Once the basic features have been implemented, you are to synchronize the
data in your local database with the remote database. In other words, users,
posts, and comments created or changed in your application should be up-
loaded to the remote database, while newly created or changed objects from
the remote databases should be downloaded to your local databases.  

The remote database is implemented as a REST webservice called Post-
GREST, which is backed by a PostgreSQL database having at least the
following three schemata:
 - users(id text, name text, stamp timestamp)
 - posts(id integer, user text, content text, stamp timestamp)
 - comments(user text, post integer, content text, stamp timestamp)

For details on the remote database see the PostGREST documentation
as well as the slides regarding the project available under Course Materials
on Blackboard,

### Phase 4 - Advanced and/or fun features
In this last phase, advanced or fun features are to be selected, designed,
implemented, and tested. There are 3 advanced features:
 - Share your location in a post.
 - Sharing a picture in a post.
 - Top fan badges.

You may think of your own fun features. Remember to get approval for
them in good time, though.
Note that this phase is optional for groups of size 1. Groups of size 1

### Phase 5 - Have fun
This last phase is optional for all group sizes but nevertheless highly recom-
mended. Use the Hoply social media platform through your applications and
have a lot of fun!















can, of course, strengthen their project by including advanced and/or fun
features.
