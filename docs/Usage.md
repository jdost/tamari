# Usage

Tamari is a forum backend with a packaged API consuming frontend.  The application
is only meant to be consumed via the API, meaning that the functionality and control
achieved through it will be uniform across media (as they all will have access to
the same actions on the same data).  The interaction with the application will be
done either anonymously as just a consumer of the information (not being logged in)
or logged into the system, giving the ability to modify and add to the dataset.

The main function of the application (as a forum system) is creating and
participating in thread discussions among the members.  The threads are placed under
various forums (organized in a tree of subforums nested within each other) based on
whatever criteria and organization used.  They are created with a title and an
initial post (the head post of the thread) to start discussion.  Then other users
may participate in the dialog via adding their own posts.

The system handles permissions on whether a user (in this context the client API
consumer) has the rights to perform the action.  This means that when trying to
edit a post, only specific people have permission to make that edit.

The HTTP requests/responses with the appliction will utilize the HTTP spec, so when
an action is attempted by a user without adequate permissions, an UNAUTHORIZED code
will be returned along with some body text giving an error message.  Other codes are
used throughout the application where appropriate (for exampe, CONFLICT is used when
trying to create another user with the same username).

Included in this is a folder '/libs' that has some basic libraries that wrap up the
packaging and handling of the API calls.  They will probably be updated and modified
as I learn to write a better standalone library.
