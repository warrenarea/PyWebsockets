/*
    PyWebsockets  04.21.2024
    _________________________
    js_interface.js       
   
    Written by Warren
  
    Back-end for controlling interface and handling data.
 */

//  Send Data  (by send button)
// -----------------------------
var myHost = "127.0.0.1"; 
var myPort = "54123"; 
var client = new io_SocketClient(myHost, myPort, "pyServer");
document.getElementById('pyInput').innerHTML = "<br>"
document.getElementById('pyDisconnect').onclick = function(e) {   
    client.sendData("pyServer:::Disconnect");
}

//  Send Button.
// ---------------
document.getElementById('pySend').onclick = function(e) {
    var data_to_send = document.getElementById('pyOutput').value;
    console.log("Sending Data ?? ");
    client.sendData("pyServer:::PRINTDATA:::" + data_to_send);
}
//  Connect Button.
// ------------------
document.getElementById('pyConnect').onclick = function(e) {
    var myHost = "127.0.0.1"; 
    var myPort = "54123"; 

    if (client == null) {
        client = new io_SocketClient(myHost, myPort, "pyServer");
    }
    client.connect(myHost, myPort);

}

//  Disconnect Button.
// ---------------------
document.getElementById('pyDisconnect').onclick = function(e) {   
    console.log("Disconnecting . . .")
    client.sendData("pyServer:::Disconnect");   // Soft Disconnect. (Requests the socket server close the socket from python)
}
document.addEventListener("DOMContentLoaded", function(event) {
        
        //  Socket Command Input.
        // ------------------------
        client.onCommand  = function(text) {

            // Commands received from py server.  (Split by ::: delimiter)
            var newCmd = text.split(":::");
            var pyStatus = document.getElementById('pyStatus');
            if (newCmd[1] == "connected") {
                pyStatus.innerText = "Connected.";
                }
        }
    
    client.onData  = function(text) {
        var pyInput = document.getElementById('pyInput');
        pyInput.innerHTML = pyInput.innerHTML + "<br>" + text;
        
    }
});

