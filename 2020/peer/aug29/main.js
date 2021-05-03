var app = {}

app.username = null
app.myPeer = null

app.otherPeers = {}

app.my_status = "closed"
// status is either "open", "closed" or "visiting"
app.visiting = null

app.doorTimer = null
app.canClose = true

app.messages = []

app.knockTimer = 0

app.gui = {}
app.mic = null

//var host = "ec2-3-14-82-216.us-east-2.compute.amazonaws.com"
var host = "localhost"


function errorstate() {
    app.gui.login.style.display = "none"
    app.gui.user.style.display = "none"
    app.gui.others.style.display = "none"
    app.gui.messages.style.display = "none"
    app.gui.sendmessage.style.display = "none"
    app.gui.knockdisplay.style.display = "none"
    app.gui.error.style.display = ""
}

function init() {
    for (var id of ["login", "username", "password", "user", "userstatus", "openbutton", "closebutton", "closetimer", "doorstatus", "others", "messages", "sendmessage", "knockdisplay", "error", "media"]) {
        app.gui[id] = document.getElementById(id)
    }

    app.gui.login.style.display = "none"
    app.gui.user.style.display = "none"
    app.gui.others.style.display = "none"
    app.gui.messages.style.display = "none"
    app.gui.sendmessage.style.display = "none"
    app.gui.knockdisplay.style.display = "none"
    app.gui.error.style.display = "none"
    
    // launch timers
    doorTick()

    // Create own peer object with connection to shared PeerJS server
    app.myPeer = new Peer(null, { 
        debug: 0,
        port: 8000,
        host: host,
        path: '/'
    })
    app.myPeer.on('open', function(id) {
        app.gui.login.style.display = ""

        if (app.myPeer.id === null) {
            errorstate()
            app.gui.error.innerText = 'Received null id from peer open!'
            return
        }

        console.log("I am "+app.myPeer.id)
    })

    app.myPeer.on('connection', init_data_connection)

    app.myPeer.on('disconnected', errorstate)
    app.myPeer.on('close', errorstate);
    app.myPeer.on('error', function (err) {
        errorstate()
        app.gui.error.innerText = "" + err
    })

  
   function loginKeyPressListener(e) {
        if (e.which == '13') {
            var username = app.gui.username.value
            var password = app.gui.password.value

            if (username.length == 0) return
            //if (password.length == 0) return
    
            password = "snickerdoodle"
            
            app.gui.login.style.display = "none"

            var xhr = new XMLHttpRequest()
            xhr.open("POST", "clients", true)
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
            xhr.onreadystatechange = function() { 
                if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                    var data = JSON.parse(this.responseText)
                    if (data == null) {
                        errorstate()
                        app.gui.error.innerText = "Bad login: wrong password, or "+username+" is already logged in."
                        return
                    }

                    app.username = username

                    for (const id in data) {
                        if (data[id] == 0) continue
                        if (data[id] == username) continue
                       
                        init_data_connection(app.myPeer.connect(id, { reliable: true }))
                    }
                    
                    update_gui()
                }
            }
            xhr.send("pass="+password+"&name="+username+"&id="+app.myPeer.id)
        }
    }
    app.gui.username.addEventListener('keypress', loginKeyPressListener)
    app.gui.password.addEventListener('keypress', loginKeyPressListener)


    app.gui.openbutton.addEventListener('click', function(e) {        
        app.my_status = "open"

        app.canClose = false
        app.doorTimer = 10

        update_status()
        update_gui()
    })
    app.gui.closebutton.addEventListener('click', function(e) {
        app.my_status = "closed"
        
        // to remove delay
        app.gui.closetimer.innerText = ""

        update_status()
        update_gui()
    })


    app.gui.sendmessage.addEventListener('keypress', function (e) {
        if (e.which == '13') {
            var message = this.value.trim()
            this.value = ""
            if (message.length == "") return

            for (var id in app.otherPeers) {
                app.otherPeers[id].data.send({"kind":"message", "message":message})
            }
            displayMessage(app.username, message)
        }
    })

    app.myPeer.on('call', function(call) {
        app.otherPeers[call.peer].status = call.metadata.status
        app.otherPeers[call.peer].visiting = call.metadata.visiting

        console.log("got call from "+ app.otherPeers[call.peer].name + " who is "+app.otherPeers[call.peer].status +" at "+app.otherPeers[call.peer].visiting)

        var media = document.createElement("audio")
        media.controls = true
        media.autoplay = true

        call.on('stream', function(remoteStream) {
            app.otherPeers[call.peer].their_mic = call
            media.srcObject = remoteStream
            app.gui.media.appendChild(media)
        })

        call.on('close', function() {
            // supposedly unsupported on firefox
            app.otherPeers[call.peer].their_mic = null
            if (app.gui.media.contains(media)) {
                app.gui.media.removeChild(media)
            }
        })

        call.answer()

        // if you are being visited and are unmuted, call them back
        // if you are visiting the same person they are, also call them back
        
        if (app.otherPeers[call.peer].status == "visiting" && app.otherPeers[call.peer].visiting == app.username) {
            if (app.mic != null) call_peer(call.peer)
        }

        if (app.otherPeers[call.peer].status == "visiting" && app.my_status == "visiting") {
            if (app.otherPeers[call.peer].visiting = app.visiting) {
                call_peer(call.peer) 
            }
        }

    })

}

function call_peer(id) {
    if (app.otherPeers[id].my_mic != null) {
        console.log("Already calling "+ app.otherPeers[id].name)
        return
    }

    var mediaResponse = function(media) {
        app.mic = media

        console.log("Calling "+ app.otherPeers[id].name)
        var call = app.myPeer.call(id, app.mic, {"metadata": {
            "status": app.my_status,
            "visiting": app.visiting,
        }})
        app.otherPeers[id].my_mic = call

        call.on('close', function() {
            app.otherPeers[id].my_mic = null
        })

        update_gui()
    }

    if (app.mic == null) {
        navigator.getUserMedia({"audio": true},mediaResponse,function(err) {
            alert("Could not get mic.")
        })
    } else {
        mediaResponse(app.mic)
    }
}

function displayMessage(who, message) {
    p = document.createElement("p")
    p.t = 5
    p.base = who+ ": " + message
    p.innerText = p.base + " ("+p.t+"s)"

    app.gui.messages.appendChild(p)

    function tickMessage() {
        p.t -= 1
        if (p.t == 0) {
            app.gui.messages.removeChild(p)
            return
        }
        p.innerText = p.base + " ("+p.t+"s)"
        setTimeout(tickMessage, 1000)
    }
    setTimeout(tickMessage, 1000)
}

// a function to keep app.gui.closetimer up to date
function doorTick() {

    if (app.my_status != "closed") {

        if (app.canClose == false) app.doorTimer -= 1
        else {
            var shouldtick = app.my_status != "visiting"
            if (shouldtick) {
                for (const id in app.otherPeers) {
                    if (app.otherPeers[id].status == "visiting" && app.otherPeers[id].visiting == app.username) {
                        shouldtick = false
                        break
                    }
                }
            }
            if (shouldtick) app.doorTimer -= 1
        }

        if (app.doorTimer == 0) {
            if (app.canClose == false) {
                app.canClose = true
                app.doorTimer = 1800


                app.gui.closebutton.disabled = app.my_status == "closed" || app.my_status == "visiting" || !app.canClose
                for (const id in app.otherPeers) {
                    if (app.otherPeers[id].status == "visiting" && app.otherPeers[id].visiting == app.username) {
                        app.gui.closebutton.disabled = true
                    }
                }

            } else {
                app.my_status = "closed"
                update_status()
                update_gui()
            }
        }
    } 


    if (app.my_status == "closed") {
        app.gui.closetimer.innerText = ""
    } else {

        if (!app.canClose) {
            app.gui.closetimer.innerText = "Can close in "+app.doorTimer+"s."
        } else {
            var s = app.doorTimer % 60
            app.gui.closetimer.innerText = "Will close in "+(app.doorTimer-s)/60+"m "+s+"s."
        }

    }
    
    setTimeout(doorTick,1000)
}





function update_status() {
    for (const id in app.otherPeers) {
        app.otherPeers[id].data.send({
            "kind": "status_update",
            "status": app.my_status,
            "visiting": app.visiting
        })
    }
}


function init_data_connection(conn) {


    conn.on('open', function() {
        conn.send({"kind": "please_identify"})
    })


    conn.on('data', function(data) {
        message_handler(conn,conn.peer,data)
    })

    conn.on('close', function() {

        if (app.my_status == "visiting" && app.visiting == app.otherPeers[conn.peer].name) {
            app.my_status = "open"
            app.visiting = null

            for (const id in app.otherPeers) {
                if (app.otherPeers[id].my_mic != null) {
                    app.otherPeers[id].my_mic.close()
                    app.otherPeers[id].my_mic = null
                    app.otherPeers[id].data.send({"kind": "close_call_from_me"})
                }

                if (app.otherPeers[id].their_mic != null) {
                    app.otherPeers[id].their_mic.close()
                    app.otherPeers[id].their_mic = null
                    app.otherPeers[id].data.send({"kind": "close_call_from_you"})
                }
            }


            update_status()
            update_gui()
        }

        if (conn.peer in app.otherPeers) delete app.otherPeers[conn.peer]

    })
}


function message_handler(conn,id,data) {


    
    if (data.kind == "please_identify") {

        conn.send({
            "kind": "identify",
            "name": app.username,
            "status": app.my_status,
            "visiting": app.visiting
        })

        return
    }

    if (data.kind == "identify") {

        app.otherPeers[id] = {
            "name": data.name,
            "status": data.status,
            "visiting": data.visiting,
            "data": conn,
            "their_mic": null, 
            "my_mic": null, 
        }
        
        update_gui()
        return
    }
    
    if (!(id in app.otherPeers)) alert("Unidentified user "+ id)

    if (data.kind == "status_update") {
        app.otherPeers[id].status = data.status
        app.otherPeers[id].visiting = data.visiting
        update_gui()
    }


    if (data.kind == "message") {
        displayMessage(app.otherPeers[id].name, data.message)
    }
    

    if (data.kind == "knock") {
        function knockTick() {
            app.knockTimer -= 1
            if (app.knockTimer == 0) {
                app.gui.knockdisplay.innerText = ""
                return
            }
            app.gui.knockdisplay.innerText = "Someone knocked on your door ("+app.knockTimer+"s)"
            setTimeout(knockTick,1000)
        }


        if (app.knockTimer == 0) {
            app.knockTimer = 5
            setTimeout(knockTick,1000)
        } else {
            app.knockTimer = 5
        }
        app.gui.knockdisplay.innerText = "Someone knocked on your door ("+app.knockTimer+"s)"
    }

    if (data.kind == "close_call_from_you") {
        console.log("My call to "+app.otherPeers[id].name+" ended")
        app.otherPeers[id].my_mic = null
    }

    if (data.kind == "close_call_from_me") {
        console.log("Call from "+app.otherPeers[id].name+" to me ended")
        app.otherPeers[id].their_mic = null
    }
}


function update_gui() {
    app.gui.login.style.display = "none"
    app.gui.error.style.display = "none"

    app.gui.user.style.display = ""

    app.gui.others.style.display = app.my_status != "closed" ? "" : "none"
    app.gui.messages.style.display = app.my_status != "closed" ? "" : "none"
    app.gui.sendmessage.style.display = app.my_status != "closed" ? "" : "none"
    app.gui.knockdisplay.style.display = app.my_status == "closed" ? "" : "none"


    // turn mic off if nobody is visiting me
    if (app.mic != null && app.my_status == "open") {
        var keep = false
        for (const id in app.otherPeers) {
            if (app.otherPeers[id].status == "visiting" && app.otherPeers[id].visiting == app.username) {
                keep = true
                break
            }
        }
        if (!keep) {
            app.mic.getTracks().forEach(function(track) { track.stop() })
            app.mic = null
        }
    }

    app.gui.userstatus.innerText = "Logged in as "+app.username+". Your mic is"
    if (app.mic == null) app.gui.userstatus.innerText += " off."
    else app.gui.userstatus.innerText += " on."
    
    app.gui.openbutton.disabled = app.my_status == "open" || app.my_status == "visiting"

    app.gui.closebutton.disabled = app.my_status == "closed" || app.my_status == "visiting" || !app.canClose
    for (const id in app.otherPeers) {
        if (app.otherPeers[id].status == "visiting" && app.otherPeers[id].visiting == app.username) {
            app.gui.closebutton.disabled = true
        }
    }


    
    if (app.my_status == "closed") {
        app.gui.doorstatus.innerText = "Your door is closed."
    }
    if (app.my_status == "visiting") {
        app.gui.doorstatus.innerText = "You are visiting "+app.visiting
    
        var others = []
        for (const id in app.otherPeers) {
            if (app.otherPeers[id].status == "visiting" && app.otherPeers[id].visiting == app.visiting) {
                others.push(app.otherPeers[id].name)
            }
        }
        
        if (others.length == 0) app.gui.doorstatus.innerText += "."
        else {
            app.gui.doorstatus.innerText += ", along with "

            if (others.length == 1) {
                app.gui.doorstatus.innerText += others[0]+"."
            } else {
                for (var i = 0; i < others.length-1; i++) {
                    app.gui.doorstatus.innerText += others[i] + ", "
                }
                app.gui.doorstatus.innerText += "and "+others[others.length-1]+"."
            }


        }

    }

    if (app.my_status == "open") {
        app.gui.doorstatus.innerText = "Your door is open"

        var others = []
        for (const id in app.otherPeers) {
            if (app.otherPeers[id].status == "visiting" && app.otherPeers[id].visiting == app.username) {
                others.push(app.otherPeers[id].name)
            }
        }
        
        if (others.length == 0) app.gui.doorstatus.innerText += "."
        else if (others.length == 1) app.gui.doorstatus.innerText += ", and "+others[0]+" is visiting you."
        else {
            app.gui.doorstatus.innerText += ", and"
            for (var i = 0; i < others.length-1; i++) {
                app.gui.doorstatus.innerText += " " +others[i] + ","
            }
            app.gui.doorstatus.innerText += " and "+others[others.length-1]+" are visiting you."
        }
    
        if (others.length > 0) {
            var mutebutton = document.createElement("input")
            mutebutton.type = "button"
            mutebutton.value = "Mute"
            mutebutton.disabled = (app.mic == null)
            app.gui.doorstatus.appendChild(mutebutton)

            mutebutton.addEventListener("click", function() {
                for (const id in app.otherPeers) {
                    if (app.otherPeers[id].status == "visiting" && app.otherPeers[id].visiting == app.username) {
                        app.otherPeers[id].my_mic.close()
                        app.otherPeers[id].my_mic = null
                        app.otherPeers[id].data.send({"kind": "close_call_from_me"})
                    }
                }
                
                app.mic.getTracks().forEach(function(track) { track.stop() })
                app.mic = null

                update_gui()
            })


            var unmutebutton = document.createElement("input")
            unmutebutton.type = "button"
            unmutebutton.value = "Unmute"
            unmutebutton.disabled = (app.mic != null)
            app.gui.doorstatus.appendChild(unmutebutton)


            unmutebutton.addEventListener("click", function() {
               
                for (const id in app.otherPeers) {
                    if (app.otherPeers[id].status == "visiting" && app.otherPeers[id].visiting == app.username) {
                        call_peer(id)
                    }
                }

                update_gui()

            })
        }

    }

    if (app.my_status != "closed") {
        app.gui.others.innerHTML = ""
        
        for (const id in app.otherPeers) {
            p = document.createElement("p")
            app.gui.others.appendChild(p)

            p.innerText = app.otherPeers[id].name + ":"

            if (app.otherPeers[id].status == "visiting") {
                p.innerText += " is visiting "+app.otherPeers[id].visiting+"."
            }
            if (app.otherPeers[id].status == "closed") {
                p.innerText += " door is closed."

                button = document.createElement("input")
                button.type = "button"
                button.value = "Knock"
                button.id = id
                
                button.addEventListener("click", function() {
                    app.otherPeers[button.id].data.send({"kind":"knock"})
                })  

                p.appendChild(button)
            }
            if (app.otherPeers[id].status == "open") {
                p.innerText += " door is open"

                var others = []
                for (const id2 in app.otherPeers) {
                    if (app.otherPeers[id2].status == "visiting" && app.otherPeers[id2].visiting == app.otherPeers[id].name) {
                        others.push(app.otherPeers[id2].name)
                    }
                }

                var imvisiting = app.my_status == "visiting" && app.visiting == app.otherPeers[id].name

                if (imvisiting && others.length == 0) {
                    p.innerText += " and you are visiting."
                } else if (imvisiting && others.length > 0) {
                    p.innerText += " and you are visiting, along with"
                } else if (!imvisiting && others.length > 0) {
                    p.innerText += " and is being visited by"
                } else {
                    p.innerText += "."
                }
            
                if (others.length > 0) {
                    if (others.length == 1) p.innerText += " "+others[0]+"."
                    else {
                        for (var i = 0; i < others.length-1; i++) {
                            p.innerText += " "+others[i] + ","
                        }
                        p.innerText += " and "+others[others.length-1]+"."
                    }
                }
                
                var button = document.createElement("input")
                button.type = "button"
                p.appendChild(button)

                if (imvisiting) {
                    button.value = "Leave"

                    button.addEventListener("click", function() {
                        app.my_status = "open"
                        app.visiting = null
                        
                        if (app.otherPeers[id].my_mic != null) {
                            app.otherPeers[id].my_mic.close()
                            app.otherPeers[id].my_mic = null
                            app.otherPeers[id].data.send({"kind": "close_call_from_me"})
                        }
                        if (app.otherPeers[id].their_mic != null) {
                            app.otherPeers[id].their_mic.close()
                            app.otherPeers[id].their_mic = null
                            app.otherPeers[id].data.send({"kind": "close_call_from_you"})
                        }

                        for (const id2 in app.otherPeers) {
                            if (app.otherPeers[id2].status == "visiting" && app.otherPeers[id2].visiting == app.otherPeers[id].name) {
                                if (app.otherPeers[id2].my_mic != null) {
                                    app.otherPeers[id2].my_mic.close()
                                    app.otherPeers[id2].my_mic = null
                                    app.otherPeers[id2].data.send({"kind": "close_call_from_me"})
                                }

                                if (app.otherPeers[id2].their_mic != null) {
                                    app.otherPeers[id2].their_mic.close()
                                    app.otherPeers[id2].their_mic = null
                                    app.otherPeers[id2].data.send({"kind": "close_call_from_you"})
                                }
                            }
                        }

                        app.mic.getTracks().forEach(function(track) { track.stop() })
                        app.mic = null

                        update_status()
                        update_gui()
                    })
                    
                } else {
                    button.value = "Visit"
                    
                    if (app.my_status == "visiting") button.disabled = true

                    for (const id2 in app.otherPeers) {
                        if (app.otherPeers[id2].status == "visiting" && app.otherPeers[id2].visiting == app.username) {
                            button.disabled = true
                            break
                        }
                    }

                    if (!button.disabled) {
                        button.addEventListener("click", function() {
                            
                            app.my_status = "visiting"
                            app.visiting = app.otherPeers[id].name

                            call_peer(id) 
                            for (const id2 in app.otherPeers) {
                                if (app.otherPeers[id2].status == "visiting" && app.otherPeers[id2].visiting == app.otherPeers[id].name) {
                                    call_peer(id2) 
                                }
                            }

                            update_status()
                            update_gui()
                        })
                    }

                }
            }
        }
    }
    
    // messages and knockdisplay are handled by their own timers.

}
