async function dispatch(uid, command, content = "") {
  return await fetch("/api/dispatch", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ uid, command, content }),
  });
}

export class LiveClient {
  uid;
  active;
  content;
  li;
  button;
  input;

  constructor(parent, uid, active, content) {
    this.uid = uid;
    this.active = active;
    this.content = content;
    let elements = this.#createElements(parent);
    this.li = elements[0];
    this.button = elements[1];
    this.input = elements[2];
  }

  disconnect() {
    this.li.remove();
  }

  async activate() {
    await dispatch(this.uid, "ACTIVATE");
    this.#activate();
  }

  #activate() {
    this.input.classList.add("active");
    this.button.classList.add("active");
    this.button.onclick = this.deactivate.bind(this);
    this.active = true;
  }

  async deactivate() {
    await dispatch(this.uid, "DEACTIVATE");
    this.#deactivate();
  }

  #deactivate() {
    this.input.classList.remove("active");
    this.button.classList.remove("active");
    this.button.onclick = this.activate.bind(this);
    this.active = false;
  }

  update(value) {
    dispatch(this.uid, "UPDATE", value).then((_) => this.#update(value));
  }

  #update(content) {
    this.content = content;
    if (!this.active) this.input.value = content;
  }

  set(active, content) {
    if (this.active !== active) active ? this.#activate() : this.#deactivate();
    if (this.content !== content) this.#update(content);
  }

  #createElements(parent) {
    let button = document.createElement("button");
    button.onclick = this.active
      ? this.deactivate.bind(this)
      : this.activate.bind(this);
    button.textContent = this.uid;

    let input = document.createElement("input");
    input.type = "text";
    input.value = this.content;
    input.oninput = (event) => this.update(event.target.value);

    let li = document.createElement("li");
    if (this.active) li.classList.add("active");
    li.appendChild(button);
    li.appendChild(input);
    parent.appendChild(li);

    return [li, button, input];
  }
}
