
var app = {}

app.lastPeedId = null
app.myPeer = null
app.otherPeers = {}

app.messages = []

app.gui = {}


app.userMedia = {
    "mic": null,
    "cam": null,
    "screen": null,
    "speaker": null,
}



/*
getUserMedia({video: true, audio: true}, function(userMedia) {
    app.userMedia = userMedia
}
*/
// Maybe separate audio/video, and allows disabling of each independently.
// Even supports screen sharing:
// https://developer.mozilla.org/en-US/docs/Web/API/Screen_Capture_API/Using_Screen_Capture


// Supposedly PIXI supports these
// https://www.html5gamedevs.com/topic/42086-using-webcam-with-pixijs-v4/

///////////////////////////////////////////////////////////////////////////
function init() {
    for (var id of ["my_id", "try_connect", "other_peers", "broadcast", "chat_log", "mic_checkbox", "cam_checkbox", "screen_checkbox", "speaker_checkbox"]) {
        app.gui[id] = document.getElementById(id)
    }
    app.gui.my_id.innerHTML = "Obtaining id..."
    app.gui.try_connect.innerHTML = ""

    app.gui.mic_checkbox.checked = false
    app.gui.cam_checkbox.checked = false
    app.gui.screen_checkbox.checked = false
    app.gui.speaker_checkbox.checked = false

    // Create own peer object with connection to shared PeerJS server
    app.myPeer = new Peer(null, { 
        debug: 2,
        port: 9000,
        host:'localhost',
        path: '/'

    })

    app.myPeer.on('open', function (id) {
        // Workaround for peer.reconnect deleting previous id
        // TODO: this is untested!
        if (app.myPeer.id === null) {
            console.log('Received null id from peer open.')
            app.myPeer.id = app.lastPeerId
        } else {
            app.lastPeerId = app.myPeer.id
        }

        app.gui.my_id.innerHTML = "My ID: " + app.myPeer.id
    })

    app.myPeer.on('connection', init_data_connection)

    app.myPeer.on('disconnected', function () {
        app.gui.my_id.innerHTML = "Reconnecting..."

        // Workaround for peer.reconnect deleting previous id
        // TODO: this is untested!
        // Does otherPeers gui need to change?
        app.myPeer.id = app.lastPeerId
        app.myPeer._lastServerId = app.lastPeerId
        app.myPeer.reconnect()
    })

    app.myPeer.on('close', function() {
        app.gui.my_id.innerHTML = "Connection destroyed."
        updatePeerGui() 
    });

    app.myPeer.on('error', function (err) {
        console.log(err)
        alert('' + err)
    })


    app.gui.try_connect.addEventListener('keypress', function (e) {
        if (e.which == '13') {
            var target = this.value
            this.value = ""

            if (target == app.myPeer.id) {
                alert("Can't connect to yourself.")
                return
            }

            if (target in app.otherPeers) {
                alert("Already connected to "+target+".")
                return
            }

            var c = app.myPeer.connect(target, { reliable: true })
            c.on('open', function() { init_data_connection(c) })
        }
    })

    app.gui.broadcast.addEventListener('keypress', function (e) {
        if (e.which == '13') {
            var message = this.value.trim()
            this.value = ""

            for (var id in app.otherPeers) {
                if (app.otherPeers[id].data != null) {
                    app.otherPeers[id].data.send(message)
                }
            }
            app.messages.push(app.myPeer.id + " (me): " + message)
            updateMessageGui()
        }
    })

    /*
     // show your own video+audio for debugging
    navigator.getUserMedia({video: true, audio: true}, function(userMedia) {
        var video = document.createElement("video")
        video.controls = true
        video.srcObject = userMedia
        document.body.appendChild(video)

    }, function(err) {
        alert('Failed to get local stream' ,err)
        app.gui.mic_checkbox.checked = false
    })
    */


    app.myPeer.on('call', function(call) {
        console.log("got call from "+ call.peer)

        call.on('stream', function(remoteStream) {

            var id = call.peer
            if (!(id in app.otherPeers)) {
                app.otherPeers[id] = {
                    "data": null,
                    "mic": null, "cam": null, "screen": null, "speaker": null,
                    "my_calls": { "mic": null, "cam": null, "screen": null, "speaker": null, }
                }
            }

            app.otherPeers[id][call.metadata] = remoteStream
            
            updatePeerGui() 
        })
        call.on('close', function() {
            // supposedly unsupported on firefox
            app.otherPeers[call.peer][call.metadata] = null
            updatePeerGui() 
        })

        call.answer()
    })


}


function init_data_connection(conn) {
    var id = conn.peer
    if (!(id in app.otherPeers)) {
        app.otherPeers[id] = {
            "data": null,
            "mic": null, "cam": null, "screen": null, "speaker": null,
            "my_calls": { "mic": null, "cam": null, "screen": null, "speaker": null, }
        }
    }

    app.otherPeers[id]["data"] = conn

    
    for (var which of ["mic", "cam", "screen", "speaker"]) {
        var media = app.userMedia[which]
        if (media != null) {
            console.log("calling new user for", which)
            var call = app.myPeer.call(id, media, {"metadata": which})
            app.otherPeers[id].my_calls[which] = call
            call.on("close", function() {
                app.otherPeers[id].my_calls[which] = null
            })
        }
    }

    updatePeerGui() 

    conn.on('data', function(data) {
        app.messages.push(id + ": " + data)
        updateMessageGui()
    })

    conn.on('close', function() {
        delete app.otherPeers[id]
        updatePeerGui()
    })
}



function updatePeerGui() {
    var found = []
    var rows = app.gui.other_peers.children
    
    // Delete rows that are no longer present
    // loop in reverse so we don't mess up the indexes
    for (var i = rows.length-1; i >= 0; i--) {
        if (!(rows[i].id in app.otherPeers)) rows[i].remove()
        else found.push(rows[i].id)
    }
    
    // add new rows
    for (var id in app.otherPeers) {
        if (found.indexOf(id) > -1) continue
        
        var row = document.createElement("tr")
        row.id = id

        for (var key of ["name","mic","cam","screen","speaker"]) {
            row[key] = document.createElement("td")
            row.appendChild(row[key])
        }
        row.name.innerHTML = id
        app.gui.other_peers.appendChild(row)
    }


    for (var i = 0; i < rows.length; i++) {
        var peer = app.otherPeers[rows[i].id]

        
        for (var which of ["mic", "cam", "screen", "speaker"]) {
            if (!peer[which]) rows[i][which].innerHTML = " (no "+which+")"
            else {
                rows[i][which].innerHTML = ""
                if (which == "mic" || which == "speaker") {
                    var media = document.createElement("audio")
                } else {
                    var media = document.createElement("video")
                }
                media.controls = true
                media.srcObject = peer[which]
                media.autoplay = true
                rows[i][which].appendChild(media)
            }
        }


    }
}


function updateMessageGui() {
    var s = ""
    for (var msg of app.messages) {
        s += "<p>"+msg+"</p>"
    }
    app.gui.chat_log.innerHTML = s
}


function get_media(which, success, error) {
    if (which == "mic") navigator.getUserMedia({"audio": true},success,error)
    if (which == "cam") navigator.getUserMedia({"video": true},success,error)
  
        
    async function get_display() {
        if (which == "screen") {
            if (navigator.getDisplayMedia) {
                return await navigator.getDisplayMedia({"video": true})
            } else if (navigator.mediaDevices.getDisplayMedia) {
                return await navigator.mediaDevices.getDisplayMedia({"video": true})
            } else {
                return await navigator.mediaDevices.getUserMedia({"video": {mediaSource: 'screen'}})
            }
        }

        if (which == "speaker") {
            return await navigator.mediaDevices.getUserMedia({"audio": {mediaSource: 'speaker'}})

            /*
            if (navigator.getDisplayMedia) {
                return await navigator.getDisplayMedia({"audio": true})
            } else if (navigator.mediaDevices.getDisplayMedia && false) {
                return await navigator.mediaDevices.getDisplayMedia({"audio": true})
            } else {
            }
            */
        }
    }


    if (which == "speaker" || which == "screen") {
        get_display().then(x => success(x)).catch(x => error(x))
    }


}

function checkbox_change(which) {
    box = which+"_checkbox"

    if (app.gui[box].checked == true) {
        app.userMedia[which] = null
        
        get_media(which, function(media) {
            app.userMedia[which] = media

            for (var id in app.otherPeers) {
                console.log("calling",id, "for", which, "with",media)
                var call = app.myPeer.call(id, media, {"metadata": which})
                app.otherPeers[id].my_calls[which] = call
                call.on("close", function() {
                    app.otherPeers[id].my_calls[which] = null
                })
            }

        }, function(err) {
            alert('Failed to get local stream' ,err)
            app.gui[box].checked = false
        })

    } else {
        for (var id in app.otherPeers) {
            app.otherPeers[id].my_calls[which].close()
        }

        app.userMedia[which].getTracks().forEach(function(track) { track.stop() })
        app.userMedia[which] = null
    }
}


