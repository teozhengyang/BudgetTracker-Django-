// when user want to edit goal
function edit_goal(id) {
    // change 'edit' button to 'save' button
    document.querySelector(`#editbutton${id}`).innerHTML = `<button class="btn btn-sm btn-outline-primary" onclick="save_goal(${id})">Save</button>`
    let account = document.querySelector(`#goalaccount${id}`)
    let amount = document.querySelector(`#goalamount${id}`)
    let description = document.querySelector(`#goaldescription${id}`)
    // allow user to edit account, amount, description
    if (account.innerHTML == "Savings") {
        account.innerHTML = `<select name="account" id="newgoalaccount${id}"><option value="Savings">Savings</option><option value="Budget">Budget</option></select>`
    } else {
        account.innerHTML = `<select name="account" id="newgoalaccount${id}"><option value="Budget">Budget</option><option value="Savings">Savings</option></select>`
    }
    amount.innerHTML = `<textarea id="newgoalamount${id}" rows="1" cols="12">${amount.innerHTML}</textarea>`
    description.innerHTML = `<textarea id="newgoaldescription${id}" rows="3" cols="12">${description.innerHTML}</textarea>`
}

// save edited goal of user
function save_goal(id) {
    let newaccount = document.querySelector(`#newgoalaccount${id}`).value
    let newamount = document.querySelector(`#newgoalamount${id}`).value
    let newdescription = document.querySelector(`#newgoaldescription${id}`).value
    // change account, amount, description of goal if edited
    fetch(`/goals/${id}`, {
        method: 'PUT',
        body: JSON.stringify ({
            newaccount: newaccount,
            newamount: newamount,
            newdescription: newdescription
        })
    })
    // return back to goals index page
    fetch(`/goals`)
    .then(response => response.text())
    .then(html => {
        document.body.innerHTML = html
    })
}

// delete goal upon user's click on button
function delete_goal(id) {
    fetch(`/goals/${id}`, {
        method: 'PUT',
        body: JSON.stringify ({
            delete: "yes"
        })
    })
    // return back to goals index page
    fetch(`/goals`)
    .then(response => response.text())
    .then(html => {
        document.body.innerHTML = html
    })
}

// calculator function
let display = document.querySelector('#calcdisplay')
let buttons = Array.from(document.querySelectorAll('.calcbutton'))
buttons.map(button => {
    button.addEventListener('click', (e) => {
        switch(e.target.innerText){
            case 'C':
                display.innerText = '';
                break;
            case '=':
                try{
                    display.innerText = eval(display.innerText);
                } catch {
                    display.innerText = "Error" 
                }
                break;
            case '←':
                if (display.innerText){
                    display.innerText = display.innerText.slice(0, -1);
                }
                break;
            default:
                display.innerText += e.target.innerText;
        }
    });
});