let username;
let password;

async function login(event) {
  console.log(`POSTING ${username} ${password}`);
  var data = [];
  for (var [k, v] of Object.entries({
    username: username,
    password: password,
    grant_type: "password",
  })) {
    data.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
  }

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
}

document.querySelector("button").onclick = login;
