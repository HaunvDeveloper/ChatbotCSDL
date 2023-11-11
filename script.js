function getInput(event) {
    if (event == null || event.key == 'Enter') {
        var giaTri = document.getElementById("input").value;
        //alert(giaTri);
        document.getElementById("input").value = "";
        addMessage(giaTri);
    }
}
var d = 0;
function addMessage(message) {
    if(message.length > 0){ 
        var moiLi = document.createElement("li");
        moiLi.className = "myMessage right";
        moiLi.textContent = message;
            
        var danhSach = document.getElementById("listchat");
        danhSach.appendChild(moiLi);
        var reply = "Câu trả lời " + ++d;
        chatReply(reply);
        //alert(JSON.stringify(saveData, null, 2));
    }
}

function chatReply(message){
    var moiLi = document.createElement("li");
    moiLi.className = "myMessage left";
    moiLi.textContent = message;
    var danhSach = document.getElementById("listchat");
    danhSach.appendChild(moiLi);
}