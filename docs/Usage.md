# Usage

Tamari is a simple forum backend, but it does not come with a built in frontend (I
am writing a sample however) which means that you can write your own customized
frontend to interact with it (it also means that various frontends can all use the
same backend).  This is just a simple usage tutorial for how to interact with the
backend.

So first off, before you can really do anything, you need to create a user.  This
is required as all modification operations (Creating, modifying, and deleting)
require that the session performing the action have a user account attached to it.
To create a user account, you will need to perform a POST operation on the url
'/user/' with two HTTP parameters, "username" and "password".  This operation
**should** succeed unless one of those parameters is missing or the username has
already been taken.  Once the action is successful, the session is automatically
logged in.  On subsequent visits where the session has expired, you can log back in
by using the PUT operation on the same url with the same username and password and
this will reattach the account to the session.

Once you are logged in, you can now create a thread.  This is done by making a POST
call to '/thread/' with two parameters, "title" for the title of the thread and
"content" for the content of the first post on the thread.  After this call, the
thread will be created.  You can get a list of the available threads by making a
GET call to '/thread/'.  If you want to modify a thread that you have created, you
will just make a PUT call to '/thread/:id' where ':id' is the thread's id (it will
be available in the thread list).

If you want to dig into a thread, you just make a GET call to '/thread/:id' where
':id' is the thread's ID.  This will return the thread information as well as all
of the posts attached to this thread.  If you want to reply to the thread, just
make a POST call to '/thread/:id' with a "content" parameter and the post will be
created and added to the thread.
