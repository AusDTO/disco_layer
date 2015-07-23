var express = require('express')
    , passport = require('passport')
    , util = require('util')
    , GitHubStrategy = require('passport-github2').Strategy,
    CONF = require('config');

// Passport session setup.
//   To support persistent login sessions, Passport needs to be able to
//   serialize users into and deserialize users out of the session.  Typically,
//   this will be as simple as storing the user ID when serializing, and finding
//   the user by ID when deserializing.  However, since this example does not
//   have a database of user records, the complete GitHub profile is serialized
//   and deserialized.
passport.serializeUser(function (user, done) {
    done(null, user);
});

passport.deserializeUser(function (obj, done) {
    done(null, obj);
});

// Use the GitHubStrategy within Passport.
//   Strategies in Passport require a `verify` function, which accept
//   credentials (in this case, an accessToken, refreshToken, and GitHub
//   profile), and invoke a callback with a user object.
passport.use(new GitHubStrategy({
        clientID: CONF.app.github_client_id,
        clientSecret: process.env.GITHUB_CLIENT_SECRET,
        callbackURL: CONF.app.server_url + "/auth/github/callback"
    },
    function (accessToken, refreshToken, profile, done) {
        // asynchronous verification, for effect...
        process.nextTick(function () {

            // To keep the example simple, the user's GitHub profile is returned to
            // represent the logged-in user.  In a typical application, you would want
            // to associate the GitHub account with a user record in your database,
            // and return that user instead.
            profile.accessToken = accessToken;

            return done(null, profile);
        });
    }
));


var server = require('nodebootstrap-server');

server.setup(function (runningApp) {

    // authentication and session setup
    runningApp.use(require('cookie-parser')());
    runningApp.use(require('express-session')({secret: CONF.app.cookie_secret, resave: false, saveUninitialized: false}));

    // Initialize Passport!  Also use passport.session() middleware, to support
    // persistent login sessions (recommended).
    runningApp.use(passport.initialize());
    runningApp.use(passport.session());

    // Choose your favorite view engine(s)
    runningApp.set('view engine', 'handlebars');
    runningApp.engine('handlebars', require('hbs').__express);

    //// you could use two view engines in parallel (if you are brave):
    // runningApp.set('view engine', 'j2');
    // runningApp.engine('j2', require('swig').renderFile);


    //---- Mounting well-encapsulated application modules
    //---- See: http://vimeo.com/56166857

    runningApp.use('/viewer', require('viewer')); // attach to sub-route
    runningApp.use('/editor', require('editor')); // attach to sub-route
    runningApp.use(require('routes')); // attach to root route
    runningApp.get('/', function (req, res) {

        var template = __dirname + '/views/home';
        var context = { layout: false };

        res.render(template, context);
    });
    runningApp.get('/about', function (req, res) {

        var template = __dirname + '/views/about';
        var context = { };

        res.render(template, context);
    });
    // If you need websockets:
    // var socketio = require('socket.io')(runningApp.http);
    // require('fauxchatapp')(socketio);


    /** Authentication **/


// GET /auth/github
//   Use passport.authenticate() as route middleware to authenticate the
//   request.  The first step in GitHub authentication will involve redirecting
//   the user to github.com.  After authorization, GitHubwill redirect the user
//   back to this application at /auth/github/callback
    runningApp.get('/auth/github',
        passport.authenticate('github', {scope: [
            'user:email', // Grants read access to a user’s email addresses. https://developer.github.com/v3/oauth/#scopes
            'repo' // Grants read/write access to code, commit statuses, collaborators, and deployment statuses for public and private repositories and organizations. https://developer.github.com/v3/oauth/#scopes
        ]}),
        function (req, res) {
            // The request will be redirected to GitHub for authentication, so this
            // function will not be called.
        });

// GET /auth/github/callback
//   Use passport.authenticate() as route middleware to authenticate the
//   request.  If authentication fails, the user will be redirected back to the
//   login page.  Otherwise, the primary route function function will be called,
//   which, in this example, will redirect the user to the home page.
    runningApp.get('/auth/github/callback',
        passport.authenticate('github', {failureRedirect: '/login'}),
        function (req, res) {
            res.redirect('/editor');
        });

    runningApp.get('/logout', function (req, res) {
        req.logout();
        res.redirect('/');
    });

});

