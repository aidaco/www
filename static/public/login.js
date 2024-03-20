let username = document.querySelector("input[name=username]");
let password = document.querySelector("input[name=password]");

async function formFetch(url, parts) {
  var data = [];
  for (var [k, v] of Object.entries(parts)) {
    data.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
  }

  return await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    },
    body: data.join("&"),
  })
}

async function checkRefresh() {
  var response = await formFetch(
    '/auth/token',
    {
      grant_type: "refresh_token",
      response_type: "cookie"
    }
  )
  if (response.ok) {
    location.href = "/admin";
  }
  await response.arrayBuffer()
}

async function login() {
  var response = await formFetch(
    '/auth/token',
    {
      username: username.value,
      password: password.value,
      grant_type: "password",
      response_type: "cookie"
    }
  )
  if (response.ok) {
    location.href = "/admin";
  } else {
    alert('Failed to authenticate');
  }
}

addEventListener('load', checkRefresh)
document.querySelector("button").addEventListener('click', login);
