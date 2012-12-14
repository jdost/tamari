# Tamari API

Tamari is a forum backend that uses a RESTful API, this will outline the proper use
of the interfaces to access the backend through your own third party application.
The Tamari API is designed to be discovery based, so **you should not have any
hardcoded routes in the application**.

## Discovery

The first call when using the API should be a request to the index of the
application.  This will provide a key/value pairing of the different accessible
endpoints of the application.

## User

To interact with the application in a writing manner (i.e. creating posts, threads,
and forums) you are required to have your session attached to an existing User
record).  The system to create a user is through the register endpoint (via the
discovery packet).  This endpoint takes a POST to create a user.  Upon creation, the
session is logged in.  The credentials given to register with can be reused to
log back in as the created User in subsequent visits (the login endpoint is also
included in the discovery packet).  When the user is finished with their session,
they can remove the authentication on their session with the logout endpoint.  This
will remove the credentials and permissions on their interactions with the server.

## Forum

Forums are the concept of collections of categorized conversation threads.  The
application will always have a root forum (this is automatically created and
returned as a discovered endpoint).  Forums can exist within forums (the term used
is 'subforum').  From the root forum endpoint, you will discovery routes to get the
threads (read below) and subforums of the forum.  These subforums will give routes
to retrieve similar information for each subforum and so on.  To create subforums or
modify them, the logged in user needs permissions to act on the forum and they can
either PUT changes to a forum (changing the name, etc.) or POST a new forum to the
forums route to create a new subforum.

## Thread

Threads are collections of conversation posts (see below) that are placed under
specified forums.  The posts are in reply to an initial topic and post made when
creating the thread.  Creating a thread requires the user be logged in.  It is a
POST to the threads route of a forum and will create both a title for a conversation
thread and the initial Post of the conversation.  Users with permission can modify
the title of Threads with PUT.

## Post

Posts are the individual inputs into a conversation Thread.  They are made in reply
to the initial or subsequent Posts in the conversation.
