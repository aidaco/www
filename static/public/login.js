let username = document.querySelector("input[name=username]");
let password = document.querySelector("input[name=password]");

async function login(event) {
  var data = [];
  for (var [k, v] of Object.entries({
    username: username.value,
    password: password.value,
    grant_type: "password",
  })) {
    data.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
  }
  try {
    var resp = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
      },
      body: data.join("&"),
    });
    var respData = await resp.json();
    console.log(`Success ${JSON.stringify(respData)}`);
    document.cookie = `Authorization=${respData.access_token};secure;max-age=86400;`;
    location.href = "/admin";
  } catch (exc) {
    alert('Failed to authenticate')
  }
}

document.querySelector("button").onclick = login;
