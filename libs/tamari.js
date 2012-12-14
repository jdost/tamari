/***
 * Tamari javascript library
 * Author: Jeff (jdost)
 *
 * This is a simple javascript wrapping library that handles the request/response
 * structure of the API for the Tamari forum.  It is meant to serve as both an
 * example in how to work with the API as well as an introductory aid in building
 * a webapp around the backend API.
 ***/
window.tamari = (function (lib) {
  if (typeof lib !== 'Object') {
    lib = {};
  }

  var prefix = lib.prefix || '',
    jQuery = window.jQuery || false,

    ready = false,
    loggedIn = false,
    routes,
    queue = []; // Queues up requests while waiting for the initial route request

  var ajax = function (args) {
    if (!args) { return false; }

    if (jQuery) { // If jQuery is available, use it to perform the ajax request
      return jQuery.ajax(args);
    }

    // Manually create and send the XHR
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
      if (xhr.readyState !== xhr.DONE) { return; }
      if (xhr.status >= 300) {  // Only error on status codes > 2xx
        if (!args.statusCode || !args.statusCode[xhr.status]) {
          if (args.error) {
            return args.error(xhr.responseText);
          }

          return;
        } else {
          return args.statusCode[xhr.status](xhr.responseText);
        }
      }

      try {
        var data = JSON.parse(xhr.responseText);
      } catch (e) {
        var data = xhr.responseText;
      }

      if (xhr.getResponseHeader('Link') && typeof data === 'object') {
        data.links = parseLinks(xhr.getResponseHeader('Link'));
      }

      if (args.success) {
        return args.success(data);
      }
    };
    xhr.open(args.type ? args.type : 'GET', prefix + args.url, true);
    xhr.setRequestHeader("Accept", "application/json");
    if (args.data) {
      var data = "";

      if (args.contentType && args.contentType === 'application/json') {
        xhr.setRequestHeader("Content-Type", args.contentType);
        data = JSON.stringify(args.data);
      } else {
        xhr.setRequestHeader("Content-Type", 'application/x-www-form-urlencoded');
        for (var key in args.data) {
          if (args.data.hasOwnProperty(key)) {
            data += encodeURI(key + '=' + args.data[key] + '&');
          }
        }
        data = data.substr(0, data.length-1);
      }

      xhr.send(data);
    } else {
      xhr.send(null);
    }
  };

  var parseLinks = function (links) {
    var regex = /<([a-zA-Z0-9_\-;&=/?]+)>; rel=\"(\w+)\"/;
    var output = {};
    if (links.length === 0) { return output; }

    links = links.split(",");
    for (var i = 0, l = links.length; i < l; i++) {
      var res = links[i].match(regex);
      if (!res) { continue; }
      output[res[2]] = res[1];
    }

    return output;
  };

  var callbacks = {},
  /**
  Events that this library will 'trigger' and the user can 'bind' to.  Mostly useful
  for the async callbacks.
   **/
    events = { };

  // bind: pseudo event binding, just stores the callback function in an array
  lib.bind = function (evt, callback) {
    if (!callbacks[evt]) { return; } // Not a valid event
    callbacks[evt].push(callback);
  };
  // trigger: pseudo event triggering, just calls all of the stored callbacks
  lib.trigger = function (evt, args) {
    if (!callbacks[evt]) { return; } // Not a valid event
    for (var i = 0, l = callbacks[evt].length; i < l; i++) {
      callbacks[evt][i](args);
    }
  };
  // User management {{{
  lib.user = {};
  /** user.register
      args: credentials object:
        username - (string) username to register
        password - (string) password for this username to authenticate with

    Tries to register the user with the application, will trigger a REGISTER event
    if the request succeeds, otherwise will trigger a REGISTRATION_FAILED event.
   **/
  events.REGISTER = "userRegistered";
  events.REGISTRATION_FAILED = "userRegistrationProblem";
  lib.user.register = function (credentials, cb) {
    if (!credentials.username || !credentials.password) {
      return;
    }

    if (!ready) { return queue.push(function () { lib.user.register(credentials); }); }
    cb = cb || {};

    ajax({
      url: routes.user.url,
      data: credentials,
      type: 'POST',
      success: function (data) {
        loggedIn = true;
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.REGISTER, data);
      },
      statusCode: {
        409: function (msg) {
          if (typeof cb.error === 'function') { cb.error(msg); }
          lib.trigger(events.REGISTRATION_FAILED, msg);
        }
      }
    });
  };

  /** user.login
      args: credentials object:
        username - (string) username to authenticate with
        password - (string) password to authenticate with

    Tries to login with the provided credentials, will trigger a LOGIN if the
    attempt succeeds and a LOGIN_FAILED if it does not.
   **/
  events.LOGIN = "userLoggedIn";
  events.LOGIN_FAILED = "loginFailed";
  lib.user.login = function (credentials, cb) {
    if (!credentials.username || !credentials.password) {
      return;
    }

    if (!ready) { return queue.push(function () { lib.user.login(credentials); }); }
    cb = cb || {};

    ajax({
      url: routes.login.url,
      data: credentials,
      type: 'POST',
      success: function (data) {
        loggedIn = true;
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.LOGIN, data);
      }, error: function (msg) {
        if (typeof cb.error === 'function') { cb.error(msg); }
        lib.trigger(events.LOGIN_FAILED, data);
      }
    });
  };

  /** user.logout

    Informs the application to void the currently logged in session.
   **/
  events.LOGOUT = "userLoggedOut";
  lib.user.logout = function (cb) {
    if (!ready) { return queue.push(function () { lib.user.logout(); }); }
    cb = cb || {};

    ajax({
      url: routes.logout.url,
      type: 'GET',
      success: function (data) {
        loggedIn = false;
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.LOGOUT, data);
      }
    });
  };
  // }}}

  // Forum interaction {{{
  lib.forum = {};
  /** forum.get
      args: forum - (string) 'url' property for a forum object
                    (object) forum object retrieved from a forum list

    Retrieves the basic information for a forum, this includes routes to retrieve
    its list of threads and list of subforums.  Will trigger a FORUM_INFO event when
    successfully retrieves a forum, otherwise will trigger a FORUM_FAILURE event.
   **/
  events.FORUM_INFO = 'forumInfoRetrieved';
  events.FORUM_FAILURE = 'forumFailure';
  lib.forum.get = function (forum, cb) {
    if (typeof forum === 'object' && forum.url) {
      forum = forum.url;
    } else if (typeof forum === 'string') {
      forum = forum;
    } else {
      if (typeof forum === 'object' && typeof cb === 'undefined') {
        cb = forum;
      }
      forum = routes.root.url;
    }

    cb = cb || {};

    ajax({
      url: forum,
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.FORUM_INFO, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.FORUM_FAILURE, data);
      }
    });
  };
  /** forum.threads
      args: thread_set - (string) url property of the thread set to request
                         (object) forum object from `forum.get`

    Retrieves the thread list for the forum.  This list is paginated, so the object
    returned *should* have a property called 'links' that has an object with the
    relative pages to the response set.  If the request succeeds, a THREAD_LIST
    is triggered, otherwise FORUM_FAILURE.
   **/
  events.THREAD_LIST = 'forumThreadList';
  lib.forum.threads = function (thread_set, cb) {
    if (typeof thread_set === 'object') {
      if (typeof thread_set.threads === 'undefined') { return; }
      thread_set = thread_set.threads;
    }

    cb = cb || {};

    ajax({
      url: thread_set,
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.THREAD_LIST, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.FORUM_FAILURE, data);
      }
    });
  };
  /** forum.forums
      args: forum_set - (string) url property of the forum set to request
                        (object) forum object from `forum.get`

    Retrieves the list of subforums for a specified forum.
   **/
  events.FORUM_LIST = 'forumForumList';
  lib.forum.forums = function (forum_set, cb) {
    if (typeof forum_set === 'object') {
      if (typeof forum_set.forums === 'undefined') { return; }
      forum_set = forum_set.forums;
    }

    cb = cb || {};

    ajax({
      url: forum_set,
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.FORUM_LIST, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.FORUM_FAILURE, data);
      }
    });
  };
  /** forum.create
      args: parent - (string) url property for the forum to create under
                     (object) forum object for the forum to create under
            forum - (object) information to use in creating the forum

    Attempts to create a forum under the specified `parent` forum using the
    information provided.
   **/
  events.FORUM_CREATED = 'forumCreationSuccessful';
  lib.forum.create = function (parent, forum, cb) {
    if (typeof parent === 'object') {
      if (typeof parent.forums === 'undefined') { return; }
      parent = parent.forums;
    }

    cb = cb || {};

    ajax({
      url: parent,
      data: forum,
      type: 'POST',
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.FORUM_CREATED, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.FORUM_FAILURE, data);
      }
    });
  };
  // }}}

  // Thread interaction {{{
  lib.thread = {};
  /** thread.get
      args: thread - (string) url property for a thread from the forum.threads call
                     (object) thread object returned from the forum.threads call

    Retrieves the thread information for the provided thread.  The result is paged,
    so the object will have a links property that has relative links to the other
    pages.  If the request fails, a THREAD_FAILURE is triggered, if successful, a
    THREAD_INFO event is triggered.
   **/
  events.THREAD_INFO = 'threadInfoRetrieved';
  events.THREAD_FAILURE = 'threadFailureOccurred';
  lib.thread.get = function (thread, cb) {
    if (typeof thread === 'object') {
      if (typeof thread.url === 'undefined') { return; }
      thread = thread.url;
    }

    cb = cb || {};

    ajax({
      url: thread,
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.THREAD_INFO, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.THREAD_FAILURE, data);
      }
    });
  };
  /** thread.create
      args: forum - (string) url property for the threads list of a forum
                    (object) forum object retrieved from forum.get
            thread - (object) definition of the thread being created

    Attempts to create a thread for the specified forum
   **/
  events.THREAD_CREATED = 'threadCreated';
  lib.thread.create = function (forum, thread, cb) {
    if (typeof forum === 'object') {
      if (typeof forum.threads === 'undefined') { return; }
      forum = forum.threads;
    }

    cb = cb || {};

    ajax({
      url: forum,
      data: thread,
      type: 'POST',
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.THREAD_CREATED, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.THREAD_FAILURE, data);
      }
    });
  };
  // }}}

  // Post interaction {{{
  lib.post = {};
  /** post.get
      args: post - (string) url property of a post object returned for a thread
                   (object) post object returned with a post list in a thread

    Retrieves the full post information for the post specified in the arguments.  If
    the retrieval fails, a POST_FAILURE is returned, otherwise a POST_INFO will be
    returned with the post data in it.
   **/
  events.POST_INFO = 'postInfoRetrieved';
  events.POST_FAILURE = 'postActionFailed';
  lib.post.get = function (post, cb) {
    if (typeof post === 'object') {
      if (typeof post.url === 'undefined') { return; }
      post = post.url;
    }

    cb = cb || {};

    ajax({
      url: post,
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.POST_INFO, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.POST_FAILURE, data);
      }
    });
  };
  /** post.edit
      args: post - (string) url property of a post object returned for a thread
                   (object) post object returned with a post list in a thread
            info - (object) new post information to apply to the exiting post

    Attempts to apply the provided information as a new version of the specified
    post object on the application.  If the edit of the post succeeds a
    POST_MODIFIED will be triggered, otherwise a POST_FAILURE will be sent.
   **/
  events.POST_MODIFIED = 'postModificationSuccessful';
  lib.post.edit = function (post, info, cb) {
    if (typeof post === 'object') {
      if (typeof post.url === 'undefined') { return; }
      post = post.url;
    }
    if (typeof info !== 'object') { return; }

    cb = cb || {};

    ajax({
      url: post,
      data: info,
      type: 'PUT',
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.POST_MODIFIED, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.POST_FAILURE, data);
      }
    });
  };
  /** post.create
      args: thread - (string) url property of a thread object
                     (object) a thread object
            post - (object) information on the post to create for the thread

    Creates a post in reply to the conversation thread specified.  The information
    provided must have at least the content set, this will be the content of the
    post being made.  If the creation of the reply works, a POST_CREATED will be
    triggered, otherwise a POST_FAILURE will be sent.
   **/
  events.POST_CREATED = 'postCreated';
  lib.post.create = function (thread, post, cb) {
    if (typeof thread === 'object') {
      if (typeof thread.url === 'undefined') { return; }
      thread = thread.url;
    }
    if (typeof post !== 'object') { return; }

    cb = cb || {};

    ajax({
      url: thread,
      data: post,
      type: 'POST',
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.POST_CREATED, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.POST_FAILURE, data);
      }
    });
  };
  // }}}

  // API settings {{{
  lib.api = {};
  /** api.get

    Requests the current settings for the API session, these settings dictate
    various properties for requests and actions made.  Upon successfully receiving
    the settings, a SETTINGS_RETRIEVED will be triggered, if it fails a
    SETTINGS_FAILURE will be used.
   **/
  events.SETTINGS_RETRIEVED = 'settingsRetrieved';
  events.SETTINGS_FAILURE = 'settingsActionFailure';
  lib.api.get = function (cb) {
    cb = cb || {};

    ajax({
      url: routes.settings.url,
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.SETTINGS_RETRIEVED, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.SETTINGS_FAILURE, data);
      }
    });
  };
  /** api.set
      args: settings - (object) definition of new settings to apply

    Applies new settings to the API session, these settings can dictate various
    properties to the actions, such as date format, time offset, page size, etc.
    If the application of settings succeeds, a SETTINGS_CHANGED is triggered, if
    it fails a SETTINGS_FAILURE.
   **/
  events.SETTINGS_CHANGED = 'settingsModified';
  lib.api.set = function (settings, cb) {
    if (typeof settings !== 'object') { return; }

    cb = cb || {};

    ajax({
      url: routes.settings.url,
      data: settings,
      type: 'PUT',
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.SETTINGS_CHANGED, data);
      },
      error: function (data) {
        if (typeof cb.error === 'function') { cb.error(data); }
        lib.trigger(events.SETTINGS_FAILURE, data);
      }
    });
  };
  /** api.version

    Retrieves the version of the application backend currently communicating with.
    Will return it with a VERSION event.
   **/
  events.VERSION = 'versionRetrieved';
  lib.api.version = function (cb) {
    cb = cb || {};

    ajax({
      url: routes.version.url,
      success: function (data) {
        if (typeof cb.success === 'function') { cb.success(data); }
        lib.trigger(events.VERSION, data);
      }
    });
  };
  // }}}


  if (jQuery) {
    // If jQuery is available, it will be used in ajax requests, setup a prefilter
    jQuery.ajaxPrefilter(function (options) {
      options.url = prefix + options.url;
      options.dataType = 'json';
      var errorFunc = options.error;
      //options.error = function (
    });
  }


  lib.EVENTS = events;
  for (e in events) { // makes the events externally visible and initializes the
      // callback array
    if (events.hasOwnProperty(e)) {
      callbacks[events[e]] = [];
      lib.EVENTS[e] = events[e];
    }
  }

  ajax({ // Has to request the endpoints from the API server
    url: '/',
    success: function (data) {
      routes = data;
      ready = true;
      if (queue.length) { // If there are any requests queued up, make them now
        for (var i = queue.length; i > 0; i--) {
          (queue.pop())();
        }
      }
    }
  });

  return lib;
}({}));
