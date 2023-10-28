function main_(){
    const getAllUsersBtn = document.getElementById("get-users-button");

    getAllUsersBtn.addEventListener("click", async (e: MouseEvent) => {
        eventCleanUp();
        const users = await getAllUsers();
        const dialog = createAddStaffDialog(e.pageX, e.pageY, users);
        document.body.appendChild(dialog);
        dialog.show();
    });

    document.body.addEventListener('click', (e: MouseEvent) => {
        const target = e.target as HTMLButtonElement;

        if (target.classList.contains('remove-staff')){
            const username: string = target.parentElement.dataset.username;
            sendRemoveStaffRequest(username);
        }
    });
}

function eventCleanUp(): void {
    const dialog = document.getElementById(
        "staff-dialog") as HTMLDialogElement;
    if (dialog) dialog.remove();
}

async function getAllUsers(): Promise<[string[]]> {
    const url = window.location.origin + '/all_usernames/';
    const response = await fetch(url, {
            method: "GET",
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": CSRFTOKEN
            }
        })

    const js = await response.json();
    const users = await js['context'];
    return JSON.parse(users);
}

function createAddStaffDialog(x: number, y: number,
                              users: [string[]]): HTMLDialogElement {
    const dialog = document.createElement('dialog');
    dialog.id = 'staff-dialog';

    // Clicking outside the dialog should close it...
    document.body.addEventListener("click", () => {
        eventCleanUp();
        document.body.removeEventListener("click", () => {}, false);
    })

    // ...but not clicking on the dialog itself
    dialog.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
    })

    const clsBtn = document.createElement('button');
    clsBtn.id = 'close-button';
    clsBtn.innerHTML = 'Cancel';
    clsBtn.addEventListener('click', () => {
        eventCleanUp();
    });
    dialog.appendChild(clsBtn);

    const inp = document.createElement('input');
    inp.setAttribute("list", "datalist-add-users");
    inp.type = 'text';
    inp.id = 'username-input';
    dialog.appendChild(inp);

    const dtl = document.createElement('datalist');
    dtl.id = "datalist-add-users";
    dialog.appendChild(dtl);

    for (const [id, username] of users){
        const opt = document.createElement("option");
        opt.value = username;
        opt.dataset.userId = id;
        dtl.appendChild(opt);
    }

    const sendBtn = document.createElement("button");
    sendBtn.id = 'send-button';
    sendBtn.innerHTML = 'Add';
    sendBtn.addEventListener('click', sendAddStaffRequest);
    dialog.appendChild(sendBtn);

    dialog.setAttribute('style', `position: absolute; left: ${x}px;`
                                  + `top: ${y}px; margin: 0`)
    return dialog;
};

async function sendAddStaffRequest(){
    const currentURL = window.location.href;
    const URLsegments = new URL(currentURL).pathname.split('/');

    // this takes care of possible trailing slashes making '' the last element
    const eventId = URLsegments.pop() || URLsegments.pop()
    const username = (document.getElementById(
                      'username-input')as HTMLInputElement).value;
    const url = window.location.origin + `/add_staff/${eventId}/`;

    const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": CSRFTOKEN
        },
        body: JSON.stringify({payload: username})
    })

    if (response.ok){
        eventCleanUp();
        addUserToStaffList(username);
    }
}

function addUserToStaffList(username: string): void {
    const staffList = document.getElementById('staff-list');
    const newUser = document.createElement('li');
    newUser.innerHTML = username;
    staffList.appendChild(newUser);
}

async function sendRemoveStaffRequest(username: string){
    // repeating myself quite a bit here
    const currentURL = window.location.href;
    const URLsegments = new URL(currentURL).pathname.split('/');

    // this takes care of possible trailing slashes making '' the last element
    const eventId = URLsegments.pop() || URLsegments.pop()
    const url = window.location.origin + `/remove_staff/${eventId}/`;

    const response = await fetch(url, {
        method: "DELETE",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": CSRFTOKEN
        },
        body: JSON.stringify({payload: username})
    });

    if (response.ok){
        removeUserFromStaffList(username);
    }
}

function removeUserFromStaffList(username: string){
    const staffList = document.getElementById('staff-list').children;
    for (const member of staffList){
        if ((member as HTMLLIElement).dataset.username === username){
            member.remove();
            break;
        }
    }
}

function getEventCookie(name: string) {
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

const CSRFTOKEN: string = getEventCookie('csrftoken');

window.onload = main_;