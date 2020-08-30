
const express = require('express');
const { ExpressPeerServer } = require('peer');

const app = express();

const basepath = "/home/prall/peer/"
const serverpass = "snickerdoodle"

var clients = {}


app.get('/favicon.ico', function (req, res) { res.send(null) });

app.get('/', function (req, res) {
    res.sendFile(basepath+"index.html")
});

app.get('/main.js', function (req, res) {
    res.sendFile(basepath+"main.js")
});

app.use(express.urlencoded({ extended: true })) // to parse post messages

app.post('/clients', function (req, res) {

    if (req.body["pass"] != serverpass) {
        console.log("Got a login with a bad password: "+req.body["pass"])
        return res.json(null)
    }

    if (!("name" in req.body && "id" in req.body)) {
        console.log("Got a login missing the name and id fields.")
        return res.json(null)
    }

    // Prevent user from logging in with a nonexistent id
    if (!(req.body["id"] in clients)) {
        console.log("Got a login with a nonexistent id.")
        return res.json(null)
    }

    // Prevent user from changing their name.
    if (clients[req.body["id"]] != 0) {
        console.log("Got a login trying to override an id.")
        return res.json(null)
    }

    for (const id in clients) {
        if (clients[id] == req.body["name"]) {
            console.log("Got a login with a duplicate name.")
            return res.json(null)
        }
    }

    console.log("Id "+req.body["id"]+" now has name "+req.body["name"])
    clients[req.body["id"]] = req.body["name"]

    res.json(clients)
});

const server = app.listen(8000);

const peerServer = ExpressPeerServer(server, {
  path: '/'
});

app.use('/', peerServer);

peerServer.on('connection', function(client) {
    console.log("New id "+client.id)
    clients[client.id] = 0
});

// use disconnect command to sanitize clients
peerServer.on('disconnect', function(client) {
    console.log("Lost user "+clients[client.id]+" with id "+client.id)
    delete clients[client.id]
});
