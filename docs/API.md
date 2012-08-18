# Tamari API

Tamari is a forum backend that uses a RESTful API, this will outline the proper use
of the interfaces to access the backend through your own third party application.
In tamari, there are three main models (currently).  They are the User, Thread,
and the Post.

## User

The User model is just a summary model for interactions with the backend per user.
It is required for all actions (PUT, POST, and DELETE) on the backend, as these
all track the performer and ensure permissions to perform the action.  The
interactions with the User model are:
   "/user/" POST -> Register the user, takes two parameters, the username (key is
      "username") and the password (key is "password").  Will return a 201 if it was
      successful and a 409 if the username is already taken.  (This is very much
      going to expand)
   "/user/" PUT -> Login the user, takes two parameters, the username and password.
      Will attempt to see if these match the entry in the database.  If so, a
      session will be attached to the client via cookie and the connection will be
      logged in as that user.
   "/user/" GET -> Get the information for the logged in user, just a simple way
      to reference the current status of the connection
   "/user/" DELETE -> Deletes the currently logged in user account and logs them
      out
   "/user/:id" GET -> Gets the account information for the specified user ID, this
      will just be a public set of information for that user.
   "/logout" GET -> Performs a logout of the currently logged in user account, just
      clears the session variable for the account

## Thread

The Thread model is the top level model of the forum, the system has a set of
Threads that represent various conversations collections with each having at least
one Post associated with it.  The threads currently act as a simple organization
system for the conversations, each being made up of various Posts.  The Thread
interactions are:
   "/thread/" POST -> Creates a thread, takes two arguments, the title, which is
      used to title the thread and summarize its purpose, and the content, which
      will be made into a Post as the initial Post under this thread.
   "/thread/" GET -> Returns a list of the threads
   "/thread/:id" PUT -> Modifies the thread specified by the id value, will only
      succeed if the logged in user is the same as the thread creator
   "/thread/:id" GET -> Returns the specified thread, which includes all of the
      Posts for that thread

## Post

The Post model is the bread and butter of the system.  A Post is merely a single
part of a Thread's conversation.  It is attached to a Thread and holds the content
of the conversation.  Post interactions stem from some already created Thread and
are:
   "/thread/:id" POST -> Replies to the thread, this will create a Post that is
      attached to the specified Thread.  Just takes a single parameter, which is
      the content of the Post
   "/post/:id" PUT -> Modifies the specified Post based on the provided id value,
      will only succeed if the logged in user is the one who created this Post, just
      takes the "content" parameter and overrides the original with this one
   "/post/:id" GET -> Gets only the specified Post based on the provided id value
