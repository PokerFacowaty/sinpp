function main(){
    const blocks = document.getElementsByClassName("block");
    for (const bl of blocks){
        bl.style.position = "absolute";
        bl.style.top = `${Number(bl.getAttribute("data-start")) * 2 + 1}px`;
        let length = Number(bl.getAttribute("data-length"));
        bl.style.height = `${length * 2}px`;
        bl.style.visibility = "visible";
    }
}

function openDialog(x, y, type){
    if (document.getElementsByTagName("dialog").length > 0){
        document.getElementsByTagName("dialog")[0].remove();
    }

    const dialog = document.createElement("dialog");
    let inner = "";
    if (type === "addShiftFromRun"){
        inner = ('<button autofocus id="closeButton">Cancel</button>'
                 + "<p>Adding Shift from Run dialog</p>"
                 + "</dialog>")
    }
    else if (type === "editShift"){
        inner = ('<button autofocus id="closeButton">Cancel</button>'
                 + "<p>Editing Shift</p>"
                 + "</dialog>")
    }
    else if (type === "removeShift"){
        inner = ('<button autofocus id="closeButton">Cancel</button>'
                 + "<p>Removing Shift</p>"
                 + "</dialog>")
    }

    dialog.innerHTML = inner;
    dialog.classList.add("form-dialog");
    dialog.style = `position: absolute; left: ${x}px; top: ${y}px; margin: 0`
    document.body.appendChild(dialog);

    const closeButton = document.getElementById("closeButton");
    closeButton.addEventListener("click", () => {
        dialog.close();
        dialog.remove();
    })
    dialog.show();
}

// https://docs.djangoproject.com/en/4.2/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

document.addEventListener('click', function(e){
    if (e.target.classList.contains("addShiftFromRun")){
        console.log("addShiftFromRun");
        openDialog(e.pageX, e.pageY, "addShiftFromRun")
    }
    else if (e.target.classList.contains("editShift")){
        console.log("editShift");
        openDialog(e.pageX, e.pageY, "editShift")
    }
    else if (e.target.classList.contains("removeShift")){
        console.log("removeShift");
        openDialog(e.pageX, e.pageY, "removeShift");
    }
})

const waitLoad = setInterval(() => {
    if (document.getElementsByClassName("block") !== null){
        clearInterval(waitLoad);
        main();
    }
}, 100)
