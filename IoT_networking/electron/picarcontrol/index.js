document.onkeydown = updateKey;
document.onkeyup = resetKey;

var net
var client
var server_port = 65432;
var server_addr = "192.168.1.7";   // the IP address of your Raspberry PI
var server_addr_vamera="192.168.1.7:9000/mjpg";


window.onload=function clientConnect() {
    net = require('net');
    client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('connected to server!');
        // send the message
        // client.write(`${input}\r\n`);
        // client.write(`${input}`);
    });
};

function clientCommunication(message){
    // const net = require('net');
    // var message = document.getElementById("message").value;
    // const client = net.createConnection({ port: server_port, host: server_addr }, () => {
    //     // 'connect' listener.
    //     console.log('connected to server!');
    //     // send the message
    //     // client.write(`${input}\r\n`);
    //     client.write(`${input}`);
    // });
    if (message!=undefined && message !=null){
        client.write(`${message}`);
        // if (message=='start camera'){
        //     document.getElementById("video_streaming").src="http://192.168.1.7:9000/mjpg" 
        // }
    }
    
    // get the data from the server
    client.on('data', (data) => {
        JSONParsedData=JSON.parse(data)
        document.getElementById("direction").innerHTML = (JSONParsedData.car_direction).toString();
        document.getElementById("speed").innerHTML = (JSONParsedData.power).toString();
        document.getElementById("temperature").innerHTML = (JSONParsedData.CPU_temp).toString();
        document.getElementById("ultrasonic").innerHTML = (JSONParsedData.ultrasonic_distance).toString();
        // document.getElementById("bluetooth").innerHTML = data;
        // console.log(data.toString(), typeof(data));
        // client.end();
        // client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });


}

function send_data(arrowInput){

    if (arrowInput!=undefined && arrowInput !=null){
        client.write(`${arrowInput}`);
        // if (message=='start camera'){
        //     document.getElementById("video_streaming").src="http://192.168.1.7:9000/mjpg" 
        // }
    }

    // const net = require('net');
    // var input = arrowInput

    // const client = net.createConnection({ port: server_port, host: server_addr }, () => {
    //     // 'connect' listener.
    //     console.log('connected to server!');
    //     // send the message
    //     // client.write(`${input}\r\n`);
    //     client.write(`${input}`);
    // });
    
    // get the data from the server
    // client.on('data', (data) => {
    //     JSONParsedData=JSON.parse(data)
    //     document.getElementById("direction").innerHTML = typeof(data);
    //     document.getElementById("speed").innerHTML = JSONParsedData;
    //     document.getElementById("temperature").innerHTML = (JSONParsedData.CPU_temp).toString();
    //     document.getElementById("ultrasonic").innerHTML = (JSONParsedData.ultrasonic_distance).toString();
    //     document.getElementById("bluetooth").innerHTML = data;
    //     console.log(data.toString(), typeof(data));
    //     client.end();
    //     client.destroy();
    // });

    client.on('end', () => {
        console.log('disconnected from server');
    });


}

// for detecting which key is been pressed w,a,s,d
function updateKey(e) {

    e = e || window.event;
    console.log (e)
    console.log (e.target.id)
    if (e.target.id!='message'){
    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "green";
        send_data("87");
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "green";
        send_data("83");
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "green";
        send_data("65");
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "green";
        send_data("68");
    }
    else if (e.keyCode == '88') {
        // stop (x)
        send_data("88");
    }
    console.log ('this is log for key press outside the input', e.keyCode)
}

}

// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";
}

function disableArrows(){
    console.log ('disableArrows triggered')
    document.getElementById("upArrow").disabled=true;
    document.getElementById("downArrow").disabled=true;
    document.getElementById("leftArrow").disabled=true;
    document.getElementById("rightArrow").disabled=true;
}


// update data for every 50ms
function update_data(message){
    console.log ('update data triggered with message of: ', message)
    clientCommunication(message);
    // setInterval(function(){
    //     // get image from python server
    //     client();
    // }, 50);
}

