/* Switched the initial interface to a class as advised here:
   https://stackoverflow.com/a/49750752/22485799 */
class Constants {
    "--timeHeight": string = '';
    "--timeTopBorder": string = '';
    PX_PER_MIN: number = Number();
    TABLE_START_TIME: Date = new Date();
    TABLE_END_TIME: Date = new Date();
    NEW_SHIFT_MINS: number = Number();
    CSRFTOKEN: string = '';
}

let cnsts: Constants = new Constants();

function main(){
    loadCSSRoot();
    addOtherCnsts();
    setBlockPosHeight();

    document.addEventListener("click", (e: MouseEvent) => {
        const target = e.target as HTMLElement;
        if (target.classList.contains("add-shift-from-run")){
            cleanUp();
            const dialog = createDialog(e.pageX, e.pageY,
                                        "add-shift-from-run");
        }
        else if (target.classList.contains("edit-shift")){
            cleanUp();
            const dialog = createDialog(e.pageX, e.pageY, "edit-shift",
                                        target.parentElement);
            document.body.appendChild(dialog);
            addDialogListeners(dialog, "edit-shift");
            dialog.show();
        }
        else if (target.classList.contains("remove-shift")){
            cleanUp();
            const dialog = createDialog(e.pageX, e.pageY, "remove-shift",
                                        target.parentElement);
            document.body.appendChild(dialog);
            addDialogListeners(dialog, "remove-shift");
            dialog.show();
        }
        else if (target.classList.contains("shifts-column")){
            cleanUp();
            const unsaved_shift = createNewShiftBox(e);
            const dialog = createDialog(e.pageX, e.pageY, "add-shift",
                                        unsaved_shift);
            document.body.appendChild(dialog);
            addDialogListeners(dialog, "add-shift");
            dialog.show();
        }
    })
}

function loadCSSRoot(){
    const propsToGet = ["--timeHeight",
                        "--timeTopBorder"]
    for (const prop of propsToGet){
        cnsts[prop] = getComputedStyle(document.documentElement, null)
                      .getPropertyValue(prop);
    }
}

function addOtherCnsts(){
    cnsts.PX_PER_MIN = (Number(cnsts["--timeHeight"].slice(0, -2))
                        + Number(cnsts["--timeTopBorder"].slice(0, -2))) / 60;
    cnsts.TABLE_START_TIME = new Date(document.getElementById(
                                      "schedule-table").dataset.startTs);
    cnsts.TABLE_END_TIME = new Date(document.getElementById(
                                    "schedule-table").dataset.endTs);
    cnsts.NEW_SHIFT_MINS = 30;
}

function setBlockPosHeight(){
    // https://stackoverflow.com/a/59341431/22485799
    const blocks = document.querySelectorAll<HTMLElement>(".block");
    for (const bl of blocks){
        bl.style.position = 'absolute';
        bl.style.top = `${Number(bl.getAttribute("data-start"))
                          * cnsts.PX_PER_MIN}px`
        const length = Number(bl.getAttribute("data-length"));
        bl.style.height = `${length * cnsts.PX_PER_MIN}px`;
    }
}

function cleanUp(){
    let dialog = document.getElementById("form-dialog");
    let unsaved_shift = document.getElementById("unsaved-shift");
    let edited_shift = document.getElementById("edited-shift");

    if (dialog) dialog.remove();
    if (unsaved_shift) unsaved_shift.remove();
    if (edited_shift){
        setDefaultTopHeight(edited_shift);
        edited_shift.removeAttribute("id");
    }
}

function createNewShiftBox(e: MouseEvent){
    const target = e.target as HTMLElement;
    // target is the shifts column

    const rect = target.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const roundedY = Math.round(y - y % cnsts.NEW_SHIFT_MINS);

    const shiftBox = document.createElement("div");
    shiftBox.id = "unsaved-shift";
    shiftBox.classList.add("shift", "block");
    shiftBox.style.position = "absolute";
    shiftBox.style.top = `${roundedY}px`;
    shiftBox.style.height = `${cnsts.NEW_SHIFT_MINS * cnsts.PX_PER_MIN}px`;

    target.appendChild(shiftBox);
    return shiftBox;
}

function createDialog(x: number, y: number, type: string,
                      el: HTMLElement=null){
    // el is an optional element that may make creating the dialog easier
    const dialog = document.createElement("dialog");
    let inner = '<button autofocus id="close-button">Cancel</button>';

    if (type === "add-shift"){
        // el is unsaved shift
        /*

        tl;dr: ignore stuff like adding "Z" to timezone-aware strings, I know
        what I'm doing for this temporary hack

        A short intro to what's going to happen here. Currently, the event is
        operating in UTC and I plan to always have the event stored internally
        in UTC (with inputs / output in local timezones).

        RIGHT NOW though, the event is UTC and the output to the schedule page
        in UTC in a sense that it starts at the same time no matter where you
        view the page. This isn't an issue by itself BUT the datetime-local
        input obviously has timezones. So FOR NOW I'm going to hack around it
        by simply ignoring the timezone and taking the time as UTC. This will
        be fixed once I get around to viewing the events in local timezones
        properly, since the lack of this feature is what's causing the issue.

        Also personally, I think there should be a choice to see the event
        and times in the event's timezone (so the internal UTC value
        + event's offset) for on-site events aside from the local tz.

        */
        let shift = el;
        let shift_pos_top = Number(shift.style.top.slice(0, -2));
        let initial_start = (new Date(cnsts.TABLE_START_TIME.getTime()
                             + shift_pos_top * (60 / cnsts.PX_PER_MIN) * 1000))
                             .toISOString().replace("Z", "");
        let initial_end = (new Date(cnsts.TABLE_START_TIME.getTime()
                           + (shift_pos_top + cnsts.NEW_SHIFT_MINS
                            * cnsts.PX_PER_MIN) * (60 / cnsts.PX_PER_MIN)
                            * 1000).toISOString().replace("Z", ""));

        inner += ('<label for="start-time" style="display: block">'
                  + 'Start time:</label>'

                  + '<input type="datetime-local" id="start-time" '
                  + `value=${initial_start} name="start-time" `
                  + 'style="display: block">'

                  + '<label for="end-time" style="display:block">'
                  + 'End time:</label>'

                  + '<input type="datetime-local" id="end-time" '
                  + `value=${initial_end} name="end-time" `
                  + `style="display: block">`

                  + '<button id="add-button">Add</button>')

        dialog.classList.add(type); // switch to dataset?
    }
    else if (type === "remove-shift"){
        // el is the shift to be removed
        inner += ('<p>Are you sure?</p>'
                  + '<button id="remove-button">Remove</button>')
        dialog.classList.add("remove-shift");
        dialog.dataset.shiftId = el.dataset.shiftId;
    }
    else if (type === "edit-shift"){
        // el is the shift being edited
        let shift = el;
                                     // timezone hackery for now
        let initial_start = shift.dataset.startTs.slice(0, -6);
        let initial_end = shift.dataset.endTs.slice(0, -6);

        inner += ('<label for="start-time" style="display: block">'
        + 'Start time:</label>'

        + '<input type="datetime-local" id="start-time" '
        + `value="${initial_start}" name="start-time" `
        + 'style="display: block">'

        + '<label for="end-time" style="display:block">'
        + 'End time:</label>'

        + '<input type="datetime-local" id="end-time" '
        + `value="${initial_end}" name="end-time" `
        + 'style="display: block">'

        + '<button id="edit-button">Edit</button>')

        dialog.classList.add("edit-shift");
        dialog.dataset.shiftId = el.dataset.shiftId;
        shift.id = "edited-shift";
    }

    dialog.innerHTML = inner;
    dialog.id = "form-dialog";
    dialog.setAttribute("style", `position: absolute; left: ${x}px;`
                                  + `top: ${y}px; margin: 0`);

    return dialog;
}

function addDialogListeners(dialog: HTMLElement, type: string){
    const closeButton: HTMLElement = dialog.querySelector('#close-button');

    closeButton.addEventListener("click", cleanUp);

    // Clicking outside the dialog should close it...
    document.body.addEventListener("click", () => {
        cleanUp();
        document.body.removeEventListener("click", () => {}, false);
    })

    // ...but not clicking on the dialog itself
    dialog.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
    })

    if (type === "add-shift" || type === "edit-shift"){
        const startTime = document.getElementById("start-time");
        const endTime = document.getElementById("end-time");

        startTime.addEventListener("focusout", setNewTopHeight);
        endTime.addEventListener("focusout", setNewTopHeight);

        if (type === "add-shift"){
            const addButton = document.getElementById("add-button");
            addButton.addEventListener("click", sendRequest);
        }
        else if (type === "edit-shift"){
            const editButton = document.getElementById("edit-button");
            editButton.addEventListener("click", sendRequest);
        }
    }
    else if (type === "remove-shift"){
        const removeButton = document.getElementById("remove-button");
        removeButton.addEventListener("click", sendRequest);
    }
}

function sendRequest(e: MouseEvent){
    const target = e.target as HTMLElement;
    // target is the button that sends the request
    // TODO: change urls from hardcoded ones
    const types = ["add-shift-from-run", "remove-shift",
                   "edit-shift", "add-shift"];
    let type = "";
    for (const cl of target.parentElement.classList){
        if (types.indexOf(cl) > -1){
            type = types[types.indexOf(cl)];
        }
    }

    let url: string;
    let method: string;
    let body: string;
    let shift: HTMLElement;
    let shiftId: number;

    if (type === "add-shift"){
        method = "POST";
        url = "https://sinpp-dev.pokerfacowaty.com/add_shift";
        shift = document.getElementById("schedule-table");
        const roleId = Number(shift.parentElement.dataset.roleId);
        const scheduleTable = document.getElementById("schedule-table");
        const eventId = Number(scheduleTable.dataset.eventId);
        const roomId = Number(scheduleTable.dataset.roomId);
        // TODO: unhack the timezones once the rest works properly
        const startTime = (document.getElementById(
                            "start-time") as HTMLInputElement).value + "Z";
        const endTime = (document.getElementById(
                         "start-time") as HTMLInputElement).value + "Z";
        body = JSON.stringify({payload: {ROLE: roleId,
                                         EVENT: eventId,
                                         ROOM: roomId,
                                         START_DATE_TIME: startTime,
                                         END_DATE_TIME: endTime}});
    }
    else if (type === "edit-shift"){
        method = "PUT";
        shiftId = Number(target.parentElement.dataset.shiftId);
        url = `https://sinpp-dev.pokerfacowaty.com/edit_shift/${shiftId}/`;
        const startTime = (document.getElementById(
                           "start-time") as HTMLInputElement).value + "Z";
        const endTime = (document.getElementById(
                         "start-time") as HTMLInputElement).value + "Z";
        body = JSON.stringify({payload: {START_DATE_TIME: startTime,
                                         END_DATE_TIME: endTime}});
    }

    fetch(url, {
        method: method,
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": cnsts.CSRFTOKEN,
        },
        body: body,
    })
    .then(response => {
        if (response.ok){
            return new Promise(resolve => {resolve(response.json())});
        }
    })
    .then(data => {
        if (type === "add-shift"){
            shift.removeAttribute("id");
            shift.innerHTML = ('<button class="edit-shift">Edit Shift</button>'
                               + '<button class="remove-shift">Remove Shift'
                               + '</button>');
            cleanUp();
        }
        else if (type === "remove-shift"){
            document.querySelector(`[data-shift-id="${shiftId}"].shift`)
            .remove();
            cleanUp();
        }
        else if (type === "edit-shift"){
            const shift = document.getElementById("edited-shift");
            shift.removeAttribute("id");
            cleanUp();
        }
    })
}

function setNewTopHeight(e: FocusEvent){
    const target = e.target as HTMLElement;
    // target is a datetime field

    let shift: HTMLElement;
    // TODO: target.parentElement.classList could use a variable
    if (target.parentElement.classList.contains("add-shift")){
        shift = document.getElementById("unsaved-shift");
    }
    else if (target.parentElement.classList.contains("edit-shift")){
        const shiftId = Number(target.parentElement.dataset.shiftId);
        shift = document.querySelector(`[data-shift-id="${shiftId}"].shift`);
    }

    const startTime = document.getElementById("start-time") as HTMLInputElement;
    const endTime = document.getElementById("end-time") as HTMLInputElement;

    const mins_since_start = ((new Date(startTime.value + "Z").getTime()
                               - cnsts.TABLE_START_TIME.getTime())
                               / 1000 / 60);
    const diff_mins = ((new Date(endTime.value + "Z").getTime()
                        - new Date(startTime.value + "Z").getTime())
                        / 1000 / 60);

    if (diff_mins > 0 && mins_since_start > 0){
        shift.style.height = `${diff_mins * cnsts.PX_PER_MIN}px`;
        shift.style.top = `${mins_since_start * cnsts.PX_PER_MIN}px`;
    }
}

function setDefaultTopHeight(shift: HTMLElement){
    // for edited shifts only
    const shift_start_ts = shift.dataset.startTs.slice(0, -6);
    const shift_end_ts = shift.dataset.endTs.slice(0, -6);
    const mins_since_start = ((new Date(shift_start_ts + "Z").getTime()
                               - cnsts.TABLE_START_TIME.getTime())
                               / 1000 / 60);
    const diff_mins = ((new Date(shift_end_ts).getTime()
                        - new Date(shift_start_ts).getTime() / 1000 / 60));

    shift.style.height = `${diff_mins * cnsts.PX_PER_MIN}px`;
    shift.style.top = `${mins_since_start * cnsts.PX_PER_MIN}px`;
}

// https://docs.djangoproject.com/en/4.2/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
function getCookie(name: string) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(
                                                 name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
cnsts.CSRFTOKEN = getCookie('csrftoken');

window.onload = main;