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

document.addEventListener('click', function(e){
    if (e.target.classList.contains("addShiftFromRun")){
        console.log("addShiftFromRun");
        openDialog(e.clientX, e.clientY, "addShiftFromRun")
    }
    else if (e.target.classList.contains("editShift")){
        console.log("editShift");
        openDialog(e.clientX, e.clientY, "editShift")
    }
    else if (e.target.classList.contains("removeShift")){
        console.log("removeShift");
        openDialog(e.clientX, e.clientY, "removeShift");
    }
})

const waitLoad = setInterval(() => {
    if (document.getElementsByClassName("block") !== null){
        clearInterval(waitLoad);
        main();
    }
}, 100)
