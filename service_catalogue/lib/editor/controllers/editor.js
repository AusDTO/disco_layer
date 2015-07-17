var exports = module.exports;
var GitHubApi = require("github");
var fs = require('fs');
var path = require('path');
var mkdirp = require('mkdirp');
var CONF = require('config');
var S = require('string');
var jf = require('jsonfile');
var NodeGit = require("nodegit");
var moment = require("moment");
jf.spaces = 4;


var github = new GitHubApi({
    // required
    version: "3.0.0",
    // optional
    debug: true,
    protocol: "https",
    host: "api.github.com", // should be api.github.com for GitHub
    pathPrefix: "", // for some GHEs; none for GitHub
    timeout: 5000,
    headers: {
        "user-agent": "passport-github" // GitHub is happy with a unique user agent
    }
});


exports.home = function (req, res) {
    if (!req.hasOwnProperty('user')) {
        var context = {
            siteTitle: "Service Catalogue",
            pageTitle: "Editor",
            breadcrumbs: [{href: "/", title: "Service Catalogue"}]
        };
        var template = __dirname + '/../views/home';
        res.render(template, context);
    } else {

        // OAuth2
        github.authenticate({
            type: "oauth",
            token: req.user.accessToken
        });

        github.repos.getAll({per_page: 100}, function (err, list) {

            var context = {
                siteTitle: "Service Catalogue",
                user: req.user,
                repos: list,
                pageTitle: "Editor",
                breadcrumbs: [{href: "/", title: "Service Catalogue"}]

            };

            var template = __dirname + '/../views/home';
            res.render(template, context);
        });
    }
}

exports.showOrganisation = function (req, res) {

    var repoAccount = req.params[0];

    var repoName = req.params[1];
    var orgPath = req.params[2];
    var alertDanger = [];

// authentication check
    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }
    var tmppath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/' + orgPath + "/";
    var model;
    try {
        model = jf.readFileSync(tmppath + "model.json");
    } catch (e) {
        alertDanger.push(e);
    }
    var definition;
    try {
        definition = jf.readFileSync(tmppath + "definition.json");
    } catch (e) {
        alertDanger.push(e);
    }
    var services = []
    fs.readdir(tmppath, function (err, files) {
        if (err) {
            alertDanger.push(err);
        } else {
            // load each service from service file
            files.forEach(function (file) {
                if (file != 'model.json' && file != 'definition.json') {
                    try {
                        var service = jf.readFileSync(tmppath + file);
                        services.push(service);
                    } catch (e) {
                        console.log(file);
                        alertDanger.push("Cannot parse JSON in " + file);
                    }
                }
            });
        }
        var context = {
            siteTitle: "Service Catalogue",
            repoAccount: repoAccount,
            repoName: repoName,
            orgPath: orgPath,
            model: model,
            definition: definition,
            services: services,
            alertDanger: alertDanger,
            pageTitle: orgPath,
            breadcrumbs: [{href: "/", title: "Service Catalogue"}, {href: "/editor/", title: "Editor"},
                {
                    href: "/editor/repo/" + repoAccount + "/" + repoName,
                    title: "Repository " + repoAccount + "/" + repoName
                }]
        };


        var template = __dirname + '/../views/organisation';
        res.render(template, context);


    });
}
exports.showServiceEditor = function (req, res) {
    var repoAccount = req.params[0];

    var repoName = req.params[1];
    var orgPath = req.params[2];
    var serviceID = req.params[3];
    var alertDanger = [];
var alertSuccess = [];
    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }
    var tmppath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/' + orgPath + "/";
    if (req.body.output) {
        var output = JSON.parse(req.body.output);
        serviceID = output.id;
        output.documentType = "ServiceInformation"
        var definition;
        try {
            definition = jf.readFileSync(tmppath + "definition.json");

            var targets = {};
            if (definition.serviceDimensions)
                definition.serviceDimensions.forEach(function (item) {
                    targets[item['id']] = item
                });
            if (definition.channels)
                definition.channels.forEach(function (item) {
                    targets[item['id']] = item
                });
            if (definition.components)
                definition.components.forEach(function (item) {
                    targets[item['id']] = item
                });
            output['Dimension'] = output['Dimension'].map(function (link) {
                if (targets[link.target]) {
                    delete targets[link.target].links;
                    return targets[link.target];
                } else {
                    return link;
                }
            });
        } catch (e) {
            alertDanger.push(e);
        }

        jf.writeFileSync(tmppath + serviceID + ".json", output);
        alertSuccess.push(serviceID + ".json saved successfully");
    }
    fs.readFile(tmppath + serviceID + ".json", function (err, latestFile) {
        var content = '""';
        if (!err) {
            content = latestFile.toString();
        }
        var context = {
            siteTitle: "Service Catalogue"
            , repoAccount: repoAccount,
            repoName: repoName,
            orgPath: orgPath,
            content: content,
            pageTitle: "Service: " + serviceID,
            alertDanger: alertDanger,
            breadcrumbs: [{href: "/", title: "Service Catalogue"}, {href: "/editor/", title: "Editor"},
                {
                    href: "/editor/repo/" + repoAccount + "/" + repoName,
                    title: "Repository " + repoAccount + "/" + repoName
                },
                {href: "/editor/edit/organisation/" + repoAccount + "/" + repoName + "/" + orgPath, title: orgPath}],
            schema: '{ $ref: "/schemas/service.json" }'

        };

        var template = __dirname + '/../views/editor';
        res.render(template, context);
    });
}

exports.autocomplete = function (req, res) {
    // if a user types foo, a GET request would be made to http://example.com?term=foo
    var repoAccount = req.params[0];

    var repoName = req.params[1];
    var orgPath = req.params[2];
    var autocompleteType = req.params[3];
    var suggestions = [];
    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }
    var tmppath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/' + orgPath + "/";

    if (autocompleteType == "link-target") {
        var definition;
        try {
            definition = jf.readFileSync(tmppath + "definition.json");
            var targets = [];
            if (definition.serviceDimensions)
                targets = targets.concat(definition.serviceDimensions);
            if (definition.channels)
                targets = targets.concat(definition.channels);
            if (definition.components)
                targets = targets.concat(definition.components);
            targets.forEach(function (item) {
                if (S(item.id + " " + item.name).toLowerCase().contains(req.query.term.toLowerCase())) {
                    suggestions.push({
                        "label": item.id + " " + item.name,
                        "value": item.id,
                        "name": item.name,
                        "type": item.type,
                        "id": item.id
                    });
                }
            });
        } catch (e) {

        }

        res.status(200).send(JSON.stringify(suggestions));
    }
}
exports.showDimensionEditor = function (req, res) {
    var repoAccount = req.params[0];

    var repoName = req.params[1];
    var orgPath = req.params[2];
    var dimID = req.params[3];

    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }
    var tmppath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/' + orgPath + "/";
    if (req.body.output) {
        var definition;
        try {
            definition = jf.readFileSync(tmppath + "definition.json");
            if (!definition.serviceDimensions) definition.serviceDimensions = []
        } catch (e) {
            definition = {"serviceDimensions": []}
        }
        var output = JSON.parse(req.body.output);
        dimID = output.id;
        definition.serviceDimensions = definition.serviceDimensions.filter(function (item) {
            if (dimID != item.id) return item;
        })
        definition.serviceDimensions.push(output);
        jf.writeFileSync(tmppath + "definition.json", definition)
    }
    var model;
    try {
        model = jf.readFileSync(tmppath + "model.json");
    } catch (e) {

    }
    jf.readFile(tmppath + "definition.json", function (err, definition) {
        var content = '""';
        if (!err) {
            if (definition && definition.serviceDimensions)

                definition.serviceDimensions.forEach(function (item) {
                    if (item.id == dimID) {
                        content = JSON.stringify(item);
                    }
                })

        }
        jf.readFile(__dirname + '/../../../public/schemas/service-dimension.json', function (err, fd) {
            if (!err) {
                if (model.serviceDimensionTypes) {
                    fd['properties']['type']['enum'] = model.serviceDimensionTypes.map(function (type) {
                        return type.id
                    });
                }
                var schema = JSON.stringify(fd);


                var context = {
                    siteTitle: "Service Catalogue"
                    , repoAccount: repoAccount,
                    repoName: repoName,
                    orgPath: orgPath,
                    editor: 'dimension',
                    content: content,
                    schema: schema,

                    pageTitle: "Dimension: " + dimID,
                    breadcrumbs: [{href: "/", title: "Service Catalogue"}, {href: "/editor/", title: "Editor"},
                        {
                            href: "/editor/repo/" + repoAccount + "/" + repoName,
                            title: "Repository " + repoAccount + "/" + repoName
                        },
                        {
                            href: "/editor/edit/organisation/" + repoAccount + "/" + repoName + "/" + orgPath,
                            title: orgPath
                        }]
                };

                var template = __dirname + '/../views/editor';
                res.render(template, context);
            } else {
                res.status(500).send('Error');
            }
        });
    });
}
exports.showComponentEditor = function (req, res) {
    var repoAccount = req.params[0];

    var repoName = req.params[1];
    var orgPath = req.params[2];
    var componentID = req.params[3];

    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }
    var tmppath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/' + orgPath + "/";
    if (req.body.output) {
        var definition;
        try {
            definition = jf.readFileSync(tmppath + "definition.json");
            if (!definition.components) definition.components = []
        } catch (e) {
            definition = {"components": []}
        }
        var output = JSON.parse(req.body.output);
        componentID = output.id
        definition.components = definition.components.filter(function (item) {
            if (componentID != item.id) return item;
        })
        definition.components.push(output);
        jf.writeFileSync(tmppath + "definition.json", definition)
    }
    var model;
    try {
        model = jf.readFileSync(tmppath + "model.json");
    } catch (e) {

    }
    jf.readFile(tmppath + "definition.json", function (err, definition) {
        jf.readFile(__dirname + '/../../../public/schemas/service-dimension.json', function (err, fd) {
            if (!err) {
                if (model.serviceComponentTypes) {
                    fd['properties']['type']['enum'] = model.serviceComponentTypes.map(function (type) {
                        return type.id
                    });
                }
                var schema = JSON.stringify(fd);

                var content = '""';
                if (!err) {
                    if (definition && definition.components)
                        definition.components.forEach(function (item) {
                            if (item.id == componentID) {
                                content = JSON.stringify(item);
                            }
                        })
                }
                var context = {
                    siteTitle: "Service Catalogue"
                    , repoAccount: repoAccount,
                    repoName: repoName,
                    orgPath: orgPath,
                    editor: 'dimension',
                    content: content,
                    schema: schema,

                    pageTitle: "Component: " + componentID,
                    breadcrumbs: [{href: "/", title: "Service Catalogue"}, {href: "/editor/", title: "Editor"},
                        {
                            href: "/editor/repo/" + repoAccount + "/" + repoName,
                            title: "Repository " + repoAccount + "/" + repoName
                        },
                        {
                            href: "/editor/edit/organisation/" + repoAccount + "/" + repoName + "/" + orgPath,
                            title: orgPath
                        }],
                };

                var template = __dirname + '/../views/editor';
                res.render(template, context);
            } else {
                res.status(500).send('Error');
            }
        });
    });
}
exports.showChannelEditor = function (req, res) {
    var repoAccount = req.params[0];

    var repoName = req.params[1];
    var orgPath = req.params[2];
    var channelID = req.params[3];

    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }
    var tmppath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/' + orgPath + "/";
    if (req.body.output) {
        var definition;
        try {
            definition = jf.readFileSync(tmppath + "definition.json");
            if (!definition.channels) definition.channels = []
        } catch (e) {
            definition = {"channels": []}
        }
        var output = JSON.parse(req.body.output);
        channelID = output.id
        definition.channels = definition.channels.filter(function (item) {
            if (channelID != item.id) return item;
        })
        definition.channels.push(output);
        jf.writeFileSync(tmppath + "definition.json", definition)
    }
    var model;
    try {
        model = jf.readFileSync(tmppath + "model.json");
    } catch (e) {

    }
    jf.readFile(tmppath + "definition.json", function (err, definition) {
        jf.readFile(__dirname + '/../../../public/schemas/service-dimension.json', function (err, fd) {
            if (!err) {
                if (model.serviceChannelTypes) {
                    fd['properties']['type']['enum'] = model.serviceChannelTypes.map(function (type) {
                        return type.id
                    });
                }
                var schema = JSON.stringify(fd);

                var content = '""';
                if (!err) {
                    if (definition && definition.channels)
                        definition.channels.forEach(function (item) {
                            if (item.id == channelID) {
                                content = JSON.stringify(item);
                            }
                        })
                }
                var context = {
                    siteTitle: "Service Catalogue",
                    repoAccount: repoAccount,
                    repoName: repoName,
                    orgPath: orgPath,
                    editor: 'dimension',
                    content: content,
                    schema: schema,

                    pageTitle: "Channel: " + channelID,
                    breadcrumbs: [{href: "/", title: "Service Catalogue"}, {href: "/editor/", title: "Editor"},
                        {
                            href: "/editor/repo/" + repoAccount + "/" + repoName,
                            title: "Repository " + repoAccount + "/" + repoName
                        },
                        {
                            href: "/editor/edit/organisation/" + repoAccount + "/" + repoName + "/" + orgPath,
                            title: orgPath
                        }],
                };

                var template = __dirname + '/../views/editor';
                res.render(template, context);
            } else {
                res.status(500).send('Error');
            }
        });
    });
}
exports.showOrgDefnEditor = function (req, res) {
    var repoAccount = req.params[0];

    var repoName = req.params[1];
    var orgPath = req.params[2];

    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }
    var tmppath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/' + orgPath + "/";
    if (req.body.output) {
        var definition;
        try {
            definition = jf.readFileSync(tmppath + "definition.json");
        } catch (e) {
            definition = {}
        }
        definition.serviceOrganisation = JSON.parse(req.body.output);
        jf.writeFileSync(tmppath + "definition.json", definition)
    }
    jf.readFile(tmppath + "definition.json", function (err, latestFile) {
        var content = '""';
        if (!err) {
            content = JSON.stringify(latestFile.serviceOrganisation);
        }
        var context = {
            siteTitle: "Service Catalogue"
            , repoAccount: repoAccount,
            repoName: repoName,
            orgPath: orgPath,
            content: content,
            schema: '{ $ref: "/schemas/organisation.json" }',

            pageTitle: "Org. Definition: " + orgPath,
            breadcrumbs: [{href: "/", title: "Service Catalogue"}, {href: "/editor/", title: "Editor"},
                {
                    href: "/editor/repo/" + repoAccount + "/" + repoName,
                    title: "Repository " + repoAccount + "/" + repoName
                },
                {href: "/editor/edit/organisation/" + repoAccount + "/" + repoName + "/" + orgPath, title: orgPath}],

        };

        var template = __dirname + '/../views/editor';
        res.render(template, context);
    });
}
exports.showOrgModelEditor = function (req, res) {
    var repoAccount = req.params[0];

    var repoName = req.params[1];
    var orgPath = req.params[2];

    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }
    var tmppath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/' + orgPath + "/";
    if (req.body.output) {
        fs.writeFileSync(tmppath + "model.json", req.body.output)
    }
    fs.readFile(tmppath + "model.json", function (err, latestFile) {
        var content = '""';
        if (!err) {
            content = latestFile.toString();
        }
        var context = {
            siteTitle: "Service Catalogue",
            repoAccount: repoAccount,
            repoName: repoName,
            orgPath: orgPath,
            content: content,
            schema: '{ $ref: "/schemas/organisation-model.json" }',
            pageTitle: "Org. Model: " + orgPath,
            breadcrumbs: [{href: "/", title: "Service Catalogue"}, {href: "/editor/", title: "Editor"},
                {
                    href: "/editor/repo/" + repoAccount + "/" + repoName,
                    title: "Repository " + repoAccount + "/" + repoName
                },
                {href: "/editor/edit/organisation/" + repoAccount + "/" + repoName + "/" + orgPath, title: orgPath}],
        };

        var template = __dirname + '/../views/editor';
        res.render(template, context);
    });
}

exports.submit = function (req, res) {
    var repoAccount = req.params[0];

    var repoName = req.params[1];

    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }

    var context = {
        siteTitle: "Service Catalogue",
        repoAccount: repoAccount,
        repoName: repoName,
        pageTitle: "Submit",
        breadcrumbs: [{href: "/", title: "Service Catalogue"}, {href: "/editor/", title: "Editor"},
            {
                href: "/editor/repo/" + repoAccount + "/" + repoName,
                title: "Repository " + repoAccount + "/" + repoName
            }]
    };
    var repo;
    var index;
    var remote;
    var oid;
    var branch, branch_short;
    var author = NodeGit.Signature.now(req.user.displayName,
        req.user.emails[0].value);
    var localPath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/';

    NodeGit.Repository.open(localPath)
        .then(function (repoResult) {
            repo = repoResult;
        })
        .then(function () {
            return repo.openIndex();
        })
        .then(function (indexResult) {
            index = indexResult;
            return index.read(1);
        }).then(function () {
            return index.addAll();
        })
        .then(function () {
            // this will write both files to the index
            return index.write();
        })
        .then(function () {
            return index.writeTree();
        })
        .then(function (oidResult) {
            oid = oidResult;
            return NodeGit.Reference.nameToId(repo, "HEAD");
        })
        .then(function (head) {
            return repo.getCommit(head);
        })
        .then(function (parent) {

            return repo.createCommit("HEAD", author, author, "saved", oid, [parent]);
        })
        .then(function () {
            return repo.getCurrentBranch()
        })
        .then(function (ref) {
            branch = ref.name();
            branch_short = branch.split('/').pop();
        })
        .then(function () {
            return NodeGit.Remote.lookup(repo, 'origin')
        })
        .then(function (remoteResult) {
            remote = remoteResult;
            remote.setCallbacks({
                credentials: function () {
                    return NodeGit.Cred.userpassPlaintextNew(req.user.accessToken, "x-oauth-basic");
                }
            });
            return remote.push([branch + ":" + branch], null, author, "Push to " + branch_short)
        })
        .done(function (push) {
            github.authenticate({
                type: "oauth",
                token: req.user.accessToken
            });

            github.pullRequests.getAll({
                user: repoAccount,
                repo: repoName,
                state: 'open',
                base: 'master',
                head: branch_short
            }, function (err, list) {
                // head: The name of the branch where your changes are implemented.
                // For cross-repository pull requests in the same network, namespace head with a user like this: username:branch.

                github.pullRequests.create({
                    user: repoAccount,
                    repo: repoName,
                    title: branch,
                    base: 'master',
                    head: branch_short
                }, function (err, list) {
                    var template = __dirname + '/../views/submit';
                    res.render(template, context);
                });
            });
        });
}

exports.showRepo = function (req, res) {
    var repoAccount = req.params[0];

    var repoName = req.params[1];

    if (req.hasOwnProperty('user')) {
        var userName = req.user.username;
    } else {
        res.redirect('/');
    }

    // Using the `clone` method from the `Git.Clone` module, bring down the NodeGit
    // test repository from GitHub.
    var cloneURL = "https://github.com/" + repoAccount + "/" + repoName;

    // Ensure that the `tmp` directory is local to this file and not the CWD.
    var localPath = CONF.app.tmp_dir + '/' + repoAccount + '/' + repoName + '/' + userName + '/';

    // Simple object to store clone options.
    var cloneOptions = {};

    // This is a required callback for OS X machines.  There is a known issue
    // with libgit2 being able to verify certificates from GitHub.
    cloneOptions.remoteCallbacks = {
        certificateCheck: function () {
            return 1;
        },
        credentials: function () {
            return NodeGit.Cred.userpassPlaintextNew(req.user.accessToken, "x-oauth-basic");
        }
    };

    // Invoke the clone operation and store the returned Promise.
    var cloneRepository = NodeGit.Clone(cloneURL, localPath, cloneOptions);

    // If the repository already exists, the clone above will fail.  You can simply
    // open the repository in this case to continue execution.
    var errorAndAttemptOpen = function () {
        return NodeGit.Repository.open(localPath);
    };

    // Once the repository has been cloned or opened, you can work with a returned
    // `Git.Repository` instance.

    cloneRepository.catch(errorAndAttemptOpen)
        .then(function (repository) {
            // Access any repository methods here.
            console.log("Is the repository bare? %s", Boolean(repository.isBare()));
            fs.readdir(localPath, function (err, files) {
                if (err) {
                    cb(null);
                } else {
                    files = files.filter(function (file) {
                        return fs.statSync(path.join(localPath, file)).isDirectory() && file != '.git';
                    });
                    var context = {
                        siteTitle: "Service Catalogue",
                        contents: files,
                        repoAccount: repoAccount,
                        repoName: repoName,
                        pageTitle: "Repository " + repoAccount + "/" + repoName,
                        breadcrumbs: [{href: "/", title: "Service Catalogue"}, {href: "/editor/", title: "Editor"}]
                    };
                    var template = __dirname + '/../views/repo';
                    repository.getCurrentBranch().then(function (ref) {
                        // Use ref
                        if (ref.name() == "refs/heads/master") {
                            repository.getHeadCommit()
                                .then(function (commit) {
                                    // create branch for changes to be recorded in
                                    repository.createBranch(
                                        "changes-"+userName+"-"+moment().format('YYYYMMDD'),
                                        commit,
                                        0, // force: Overwrite existing branch.
                                        repository.defaultSignature(),
                                        "Created new-branch on HEAD");
                                }).then(function () {
                                    repository.checkoutBranch('new-branch');
                                    res.render(template, context);
                                });
                        }
                        else {
                            res.render(template, context);
                        }
                    });
                }
            });
        });

};