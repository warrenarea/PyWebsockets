/*
    pyServer  2023.Oct.12
    _____________________
    io_SocketClient.js  
   
    Written by Warren
  
    WebSocket client for dispatching event-driven data to io_SocketServer.py

*/
try {

function io_SocketClient(ip,port,query) {
    var _this = this;
    this.socket = '';
    this.uid = 0;
    this.sign = '';
    this.connect = function(myIP, myPORT) {
        if (this.socket != '' && this.socket.readyState != 3) { 
            return;   // Readystate is status of WebSocket connection. (3 = connected)
        }

        // Websocket connect address. 
        myIP   = "127.0.0.1";
        myPort = "54123";
        this.socket = new WebSocket('ws://' + myIP + ':' + myPORT + '/pyServer');
        this.socket.onopen = function() {
            _this.onOpen();
        
        }
        this.socket.onmessage = function(event) {

            if (event.data.length == 1) {
                return;
            }
            data = event.data;
            console.log(data)
            data = data.split("<split>");  // Input data (from server) gets split with this text as a delimiter.
            _this.uid = data[0];           // Unique hash identifier is acquired as first piece of data.
            _this.sign = data[1];          // 
            text = data[2];                // Data.
            
            if (text == undefined) {
                //console.log("Undefined? " + event.data)
            }
            
            // This is used to acquire custom data from your programs API. 
            // Think of it as an API layer, to pass data to your browser.
            if (Number.isInteger(text[0]) == false) {
                command = text.substring(0,8);
                if (command == "pyServer:::") {   
                    _this.onCommand(text);
                    return;
                }
            }
            // Sets unique hash identifier (Required for Websocket handshaking)
            if (text != 'SETUID') {  
               _this.onData(text);
            } else {
                _this.onRegist();
            }
        }        
        this.socket.onclose = function(event) { 
            if (this.socket == '') { return; }
            _this.onClose();
        }; 
    }
    this.onRegist = function() {
    }
    this.onClose = function() {
    }

    // Indicates socket is connected (ie. socket is open)
    // Check the browsers (inspection) console to read this data.
    this.onOpen = function() {
        console.log('Socket Open');
    }

    this.onData = function(text) {
    }
    
    // Data to send.  Checks the sockets "readystate" before transmitting data packet.
    this.sendData = function (text) {
        if (this.socket == '') { 
        return; }
        if (this.socket.readyState != 1) {
        return; }
        var data = this.uid+'<split>'+this.sign+'<split>'+text;
        this.socket.send(data);
    }
    
    this.close = function() {
        if (this.socket == '') { 
        return; }
        this.socket.close();
    }
}
}

// Catch any socket errors along the way.
catch(err) {
  console.log("Debug Error io_socketClient.js >>> " + err.message);
}
