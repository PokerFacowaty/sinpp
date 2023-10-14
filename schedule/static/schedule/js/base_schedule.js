// TODO: fix them as const once I figure out the loading
let TABLE_START_TIME;
let TABLE_END_TIME;

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

function openDialog(x, y, type, id=null){
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
                 + "<p>Are you sure?</p>"
                 + `<button id="remove-button">Remove</button>`)
        dialog.classList.add("remove-shift");
        dialog.dataset.shiftId = id;
    }
    else if (type === "addShift"){
        /*
        A short intro to what's going to happen here. Currently, the event is
        operating in UTC and I plan to always have the event stored internally
        in UTC (with inputs / output in local timezones).

        RIGHT NOW though, the event is UTC and the output to the schedule page
        in UTC in a sense that it starts at the same time no matter where you
        view the page. This isn't an issue by itself BUT the datetime-local
        input obviously has timezones. So FOR NOW I'm going to hack around it
        by turning the UTC into local (as 1:1 the same time) and vice versa
        for actual place on the event timeline <-> the input field. This will
        be fixed once I get around to viewing the events in local timezones
        properly, since the lack of this feature is what's causing the issue.

        Personally, I think there should be a choice to see the event and times
        in the event's timezone (so the internal UTC value + event's offset)
        for on-site events aside from the local tz.
        */

        shift_pos_top = Number(document.getElementById("unsaved-shift").style.top.slice(0, -2));
        inner = (`<button autofocus id="closeButton">Cancel</button>`
                 + '<label for="start-time" style="display: block">Start time:</label>'
                 + `<input type="datetime-local" id="start-time" value="${(new Date(TABLE_START_TIME.getTime() + shift_pos_top * 30 * 1000)).toISOString().replace("Z", "")}" name="start-time" style="display: block">`
                 + '<label for="end-time" style="display: block">End time:</label>'
                 + `<input type="datetime-local" id="end-time" value="${(new Date(TABLE_START_TIME.getTime() + (shift_pos_top + 60) * 30 * 1000)).toISOString().replace("Z", "")}" name="end-time" style="display: block">`
                 + `<button id="add-button">Add</button>`)
        dialog.classList.add("add-shift");
    }

    dialog.innerHTML = inner;
    dialog.id = "form-dialog"
    dialog.classList.add("form-dialog");
    dialog.style = `position: absolute; left: ${x}px; top: ${y}px; margin: 0`
    document.body.appendChild(dialog);

    const closeButton = document.getElementById("closeButton");
    closeButton.addEventListener("click", () => {
        if (document.getElementById("unsaved-shift")){
            document.getElementById("unsaved-shift").remove();
            }
        dialog.close();
        dialog.remove();
    })

    if (type === "addShift"){
        const addButton = document.getElementById("add-button");
        addButton.addEventListener("click", sendRequest, false);
        document.body.addEventListener("click", () => {
            // This is so a click outside the dialog "cleans up"
            if (document.getElementById("unsaved-shift")){
            document.getElementById("unsaved-shift").remove();
            }
            dialog.close();
            dialog.remove();
            document.body.removeEventListener("click", () => {}, false);
        })
        dialog.addEventListener("click", (e) => {
            // So that clicking inside the dialog doesn't "clean up"
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
        })
    }
    else if (type === "removeShift"){
        const removeButton = document.getElementById("remove-button");
        removeButton.addEventListener("click", sendRequest, false);
        document.body.addEventListener("click", () => {
            dialog.close();
            dialog.remove();
            document.body.removeEventListener("click", () => {}, false);
        })
        dialog.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
        })
    }

    dialog.show();
}

function createShiftBox(e){
    let rect = e.target.getBoundingClientRect();
    let y = e.clientY - rect.top;
    let rounded_pos = Math.round(y - y % 30);

    let shiftBox = document.createElement("div");
    shiftBox.id = "unsaved-shift";
    shiftBox.classList.add("shift", "block");
    shiftBox.style.position = "absolute";
    shiftBox.style.top = `${rounded_pos}px`;
    shiftBox.style.height = `${60}px`;
    shiftBox.style.visibility = "visible";

    e.target.appendChild(shiftBox);
}

function sendRequest(e){
    const dialog = e.target.parentElement;
    const classes = dialog.classList;

    if (classes.contains("add-shift")){
        const shift = document.getElementById("unsaved-shift");
        const roleId = Number(shift.parentElement.dataset.roleId);
        const eventId = 21; // TODO: replace hardcoded values
        const roomId = 2;

        // TODO: unhack the timezone shenanigans
        const start_time = document.getElementById("start-time").value + "Z"
        const end_time = document.getElementById("end-time").value + "Z"

        fetch("https://sinpp-dev.pokerfacowaty.com/add_shift/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({payload: {ROLE: roleId,
                                            EVENT: eventId,
                                            ROOM: roomId,
                                            START_DATE_TIME: start_time,
                                            END_DATE_TIME: end_time}})})
            .then(response => {
                if (response.ok){
                    return new Promise(resolve => {resolve(response.json())})
                }
                // response.json()
            })
            .then(data => {
                shift.id = "";
                shift.classList.add("shift", "block");
                shift.innerHTML = `<button class="editShift">Edit Shift</button>
                <button class="removeShift">Remove Shift</button>`;
            })
            // .then(data => {
            //     console.log(data);
            // })
    }
    else if (classes.contains("remove-shift")){
        const shiftId = Number(e.target.parentElement.dataset.shiftId);
        fetch(`https://sinpp-dev.pokerfacowaty.com/remove_shift/${shiftId}`, {
            method: "DELETE",
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })
    }
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
        const shiftId = Number(e.target.parentElement.dataset.shiftId);
        openDialog(e.pageX, e.pageY, "removeShift", shiftId);
    }
    else if (e.target.classList.contains("shifts-column")){
        // close Dialog if it's open
        if (document.getElementById("form-dialog")){
            document.getElementById("form-dialog").close();
            document.getElementById("form-dialog").remove();
        }
        if (document.getElementById("unsaved-shift")){
            document.getElementById("unsaved-shift").remove();
        }
        createShiftBox(e);
        openDialog(e.pageX, e.pageY, "addShift");
    }
})

const waitLoad = setInterval(() => {
    // TODO: needs changing, this won't work with an empty schedule
    if (document.getElementsByClassName("block") !== null){
        clearInterval(waitLoad);
        TABLE_START_TIME = new Date(document.getElementById("schedule-table").dataset.startTs);
        TABLE_END_TIME = new Date(document.getElementById("schedule-table").dataset.endTs);
        console.log(TABLE_START_TIME, TABLE_END_TIME)
        main();
    }
}, 100)
