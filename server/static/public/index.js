const { WSRewrite } = await import("/wsrewrite.js");

let target = document.querySelector("main");
let activated = false;
let originalContent = target.innerHTML;
let rewriteContent = "";

function update() {
  target.innerHTML = activated ? rewriteContent : originalContent;
}

let rewrite = new WSRewrite("/client", {
  oncommand: (command, data) => {
    switch (command) {
      case "CONNECT":
        break;
      case "ACTIVATE":
        activated = true;
        break;
      case "UPDATE":
        rewriteContent = data;
        break;
      case "DEACTIVATE":
        activated = false;
        break;
    }
    update();
  },
  onclose: () => {
    activated = false;
    update();
  },
  onerror: (event) => {
    console.log(event);
  },
});

rewrite.connect();
window.onbeforeunload = function () {
  rewrite.disconnect();
  activated = false;
};