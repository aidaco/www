import BorderCard from "./BorderCard.svelte";
import LiveControl from "./LiveControl.svelte";

var state = {};

function dispatch(uid, command, content = "") {
  fetch("/api/dispatch", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      command: command,
      uid: uid,
      content: content,
    }),
  });
}

class State {
  active
  content
  #_active
  #_content

  constructor(active, content) {
    this._active = active
    this._content = content
  }

  get active() {return this._active}
  set active(value) {
    await 
    this._active = value
  }
  get content() {return this._content}
  set content(value) {this._content = value}
}

class LiveControl {
  uid
  state
  elements

  constructor(parent, uid, active=false, content='') {
    this.uid = uid
    this.content = content
    this.elements = this.createElement(parent)
  }

  createElement(parent) {
    let button = document.createElement('button')
    button.textContent = this.uid
    button.onclick = (event) => this.active = !this.active

    let input = document.createElement('input')
    input.type='text'
    input.onchange = (event) => this.content = input.value

    let li = document.createElement('li')
    li.className = this.active? 'active' : ''
    li.appendChild(button)
    li.appendChild(input)
    parent.appendChild(li)
    return {li, button, input}
  }

  activate() {
    dispatch("ACTIVATE", this.uid);
    this.active = true;
  }

  update() {
    dispatch("UPDATE", uid, content);
  }

  deactivate() {
    dispatch("DEACTIVATE", uid);
    active = false;
  }  

  get active() {
    return this.elements.li.className = 'active'
  }

  set active(newValue) {
    this.elements.li.className = newValue? 'active': ''
  }

  get content() {
    return this.elements.input.value
  }

  set content(newValue) {
    this.content = newValue
    if (this.elements.input.value !== newValue) this.elements.input.value = newValue
    console.log('TODO: actually send updates.')
  }
}

async function refresh() {
  const response = await fetch("/api/state");
  state = await response.json();
}

async function auto_refresh() {
  await refresh();
  setTimeout(auto_refresh, 5000);
}

auto_refresh()
