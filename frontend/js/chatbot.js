// =========================================================
//  FORCE CLEAN SESSION (CRITICAL FIX)
// =========================================================
let session_id = null;   //  force new session (important)
let chatBox = null;
let chatHistory = [];





// =========================================================
//  INIT
// =========================================================
//  AUTO RESET INVALID SESSION
async function validateSession() {
  try {
    const res = await fetch(`/history/${session_id}`);
    if (!res.ok) {
      localStorage.removeItem("session_id");
      session_id = null;
    }
  } catch {
    localStorage.removeItem("session_id");
    session_id = null;
  }
}





window.addEventListener("DOMContentLoaded", async () => {

  chatBox = document.getElementById("chat-messages");

  const input = document.getElementById("user-input");

  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendMessage();
    });
  }

  await validateSession();  //  check session validity on load
  await initSession();
  await loadHistory();
});


// =========================================================
//  FORMAT MESSAGE
// =========================================================
function formatMessage(text) {

  if (!text) return "";

  // 🔹 Bold headings
  text = text.replace(/(^|\n)([^:\n]+:)/g, (match) => {
    return `<br><b>${match.trim()}</b>`;
  });

  // 🔹 Bullet points
  text = text.replace(/- /g, "• ");

  // 🔹 Table detection
  if (text.includes("|")) {
    return renderTable(text);
  }

  // 🔹 Line breaks
  text = text.replace(/\n/g, "<br>");

  return text;
}


// =========================================================
//  TABLE RENDER
// =========================================================
function renderTable(text) {

  const lines = text.split("\n");

  let html = "<table class='report-table'>";

  lines.forEach((line, i) => {

    if (!line.includes("|")) return;

    const cols = line.split("|").map(c => c.trim());

    if (i === 0) {
      html += "<tr>" + cols.map(c => `<th>${c}</th>`).join("") + "</tr>";
    } else {
      html += "<tr>" + cols.map(c => `<td>${c}</td>`).join("") + "</tr>";
    }
  });

  html += "</table>";
  return html;
}


// =========================================================
//  INIT SESSION (FIXED)
// =========================================================
async function initSession() {

  try {
    const res = await fetch(`/session`);
    const data = await res.json();

    session_id = data.session_id;  //  keep as number
    localStorage.setItem("session_id", session_id);

    console.log("✅ Session created:", session_id);

  } catch (err) {
    console.error("❌ Session failed", err);
  }
}


// =========================================================
//  LOAD HISTORY (SAFE)
// =========================================================
async function loadHistory() {

  if (!session_id) return;

  try {
    const res = await fetch(`/history/${session_id}`);

    if (!res.ok) return;  // ❗ prevent crash

    const data = await res.json();

    chatHistory = data.history || [];

    chatBox.innerHTML = "";

    chatHistory.forEach(msg => {
      addMessage(msg.content, msg.role === "user" ? "user" : "bot");
    });

    updateSidebar();

  } catch (err) {
    console.error("❌ History load failed", err);
  }
}


// =========================================================
//  ADD MESSAGE
// =========================================================
function addMessage(text, type) {

  const msg = document.createElement("div");
  msg.className = "message " + type;

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  //  smart coloring
  if (text.includes("💊")) {
    bubble.style.background = "#d4edda";
  } else if (text.includes("⚠️")) {
    bubble.style.background = "#fff3cd";
  } else if (text.includes("🚨")) {
    bubble.style.background = "#f8d7da";
  }

  bubble.innerHTML = formatMessage(text);

  msg.appendChild(bubble);
  chatBox.appendChild(msg);

  chatBox.scrollTop = chatBox.scrollHeight;
}


// =========================================================
//  SIDEBAR
// =========================================================
function updateSidebar() {

  const sidebar = document.getElementById("chat-sidebar");
  if (!sidebar) return;

  sidebar.innerHTML = "";

  chatHistory.slice(-10).forEach(msg => {

    if (msg.role !== "user") return;

    const item = document.createElement("div");

    item.innerText = msg.content.slice(0, 30) + "...";

    item.onclick = () => {
      document.getElementById("user-input").value = msg.content;
    };

    sidebar.appendChild(item);
  });
}


// =========================================================
//  SEND MESSAGE (FIXED)
// =========================================================
async function sendMessage() {

  const input = document.getElementById("user-input");
  const text = input.value.trim();

  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  //  loading
  const loading = document.createElement("div");
  loading.className = "message bot";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerText = "Typing...";

  loading.appendChild(bubble);
  chatBox.appendChild(loading);

  try {

    const res = await fetch(`/chat`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        message: text,
        session_id: Number(session_id)   // FIXED
      })
    });

    const data = await res.json();

    loading.remove();

    const response = data?.response || "⚠️ No response";

    addMessage(response, "bot");

    chatHistory.push({ role: "user", content: text });
    chatHistory.push({ role: "assistant", content: response });

    updateSidebar();

  } catch (err) {
    loading.remove();
    addMessage("❌ Server error", "bot");
  }
}


// =========================================================
//  NEW CHAT
// =========================================================
async function newChat() {

  localStorage.removeItem("session_id");
  session_id = null;
  chatHistory = [];

  chatBox.innerHTML = "";

  await initSession();
}








// let session_id = localStorage.getItem("session_id") || null;
// let chatBox = null;
// let chatHistory = [];

// window.addEventListener("DOMContentLoaded", async () => {

//   chatBox = document.getElementById("chat-messages");

//   const input = document.getElementById("user-input");

//   if (input) {
//     input.addEventListener("keydown", function(e) {
//       if (e.key === "Enter") sendMessage();
//     });
//   }

//   await initSession();
//   await loadHistory();
// });


// // =========================================================
// // INIT SESSION
// // =========================================================
// async function initSession() {

//   if (session_id) return;

//   try {
//     const res = await fetch(`/session`);
//     const data = await res.json();

//     session_id = String(data.session_id);
//     localStorage.setItem("session_id", session_id);

//   } catch {
//     console.error("❌ Session failed");
//   }
// }


// // =========================================================
// // LOAD HISTORY
// // =========================================================
// async function loadHistory() {

//   if (!session_id) return;

//   try {
//     const res = await fetch(`/history/${session_id}`);
//     const data = await res.json();

//     chatHistory = data.history || [];

//     chatBox.innerHTML = "";

//     chatHistory.forEach(msg => {
//       addMessage(msg.content, msg.role === "user" ? "user" : "bot");
//     });

//     updateSidebar(); // ⭐ IMPORTANT

//   } catch {
//     console.error("❌ History load failed");
//   }
// }


// // =========================================================
// // 🔥 ADD MESSAGE
// // =========================================================
// function addMessage(text, type) {

//   const msg = document.createElement("div");
//   msg.className = "message " + type;

//   const bubble = document.createElement("span");
//   bubble.className = "bubble";

//   // 🎯 Highlight
//   if (text.includes("💊")) {
//     bubble.style.background = "#d4edda";
//   } else if (text.includes("⚠️")) {
//     bubble.style.background = "#fff3cd";
//   }

//   function formatMessage(text) {

//   // 🔹 Bold headings (lines ending with :)
//   text = text.replace(/(^|\n)([^:\n]+:)/g, (match) => {
//     return `<br><b>${match.trim()}</b>`;
//   });

//   // 🔹 New lines
//   text = text.replace(/\n/g, "<br>");

//   return text;
// }

//   bubble.innerHTML = formatMessage(text);
//   msg.appendChild(bubble);
//   chatBox.appendChild(msg);

//   chatBox.scrollTop = chatBox.scrollHeight;
// }


// // =========================================================
// // 🔥 SIDEBAR UPDATE (NEW)
// // =========================================================
// function updateSidebar() {

//   const sidebar = document.getElementById("chat-sidebar");
//   if (!sidebar) return;

//   sidebar.innerHTML = "";

//   chatHistory.slice(-10).forEach(msg => {

//     const item = document.createElement("div");
//     item.innerText = msg.content.slice(0, 40);

//     // 🎯 color coding
//     if (msg.content.includes("💊")) {
//       item.style.color = "green";
//     } else if (msg.content.includes("⚠️")) {
//       item.style.color = "orange";
//     }

//     sidebar.appendChild(item);
//   });
// }


// // =========================================================
// // 🔥 SEND MESSAGE
// // =========================================================
// async function sendMessage() {

//   const input = document.getElementById("user-input");
//   const text = input.value.trim();

//   if (!text) return;

//   addMessage(text, "user");
//   input.value = "";

//   // ⏳ loading
//   const loading = document.createElement("div");
//   loading.className = "message bot";

//   const bubble = document.createElement("span");
//   bubble.className = "bubble";
//   bubble.innerText = "Typing...";

//   loading.appendChild(bubble);
//   chatBox.appendChild(loading);

//   try {

//     const res = await fetch(`/chat`, {
//       method: "POST",
//       headers: {"Content-Type": "application/json"},
//       body: JSON.stringify({
//         message: text,
//         session_id: session_id
//       })
//     });

//     const data = await res.json();

//     loading.remove();

//     const response = data.response || "No response";

//     addMessage(response, "bot");

//     // ✅ update history
//     chatHistory.push({ role: "user", content: text });
//     chatHistory.push({ role: "assistant", content: response });

//     updateSidebar(); // ⭐ IMPORTANT

//   } catch (err) {
//     loading.remove();
//     addMessage("❌ Server error", "bot");
//   }
// }










// let session_id = null;
// let chatBox = null;

// window.addEventListener("DOMContentLoaded", async () => {

//   chatBox = document.getElementById("chat-messages");

//   const input = document.getElementById("user-input");

//   if (input) {
//     input.addEventListener("keydown", function(e) {
//       if (e.key === "Enter") sendMessage();
//     });
//   }

//   await initSession();
// });

// // SESSION
// async function initSession() {
//   try {
//     const res = await fetch(`/session`);
//     const data = await res.json();
//     session_id = String(data.session_id);
//   } catch {
//     console.error("Session failed");
//   }
// }

// // ADD MESSAGE
// function addMessage(text, type) {

//   const msg = document.createElement("div");
//   msg.className = "message " + type;

//   const bubble = document.createElement("span");
//   bubble.className = "bubble";
//   bubble.innerText = text;

//   msg.appendChild(bubble);

//   chatBox.appendChild(msg);

//   chatBox.scrollTop = chatBox.scrollHeight;
// }

// // SEND MESSAGE
// async function sendMessage() {

//   const input = document.getElementById("user-input");
//   const text = input.value.trim();

//   if (!text) return;

//   addMessage(text, "user");
//   input.value = "";

//   // loading
//   const loading = document.createElement("div");
//   loading.className = "message bot";

//   const bubble = document.createElement("span");
//   bubble.className = "bubble";
//   bubble.innerText = "Typing...";

//   loading.appendChild(bubble);
//   chatBox.appendChild(loading);

//   try {

//     const res = await fetch(`/chat`, {
//       method: "POST",
//       headers: {"Content-Type": "application/json"},
//       body: JSON.stringify({
//         message: text,
//         session_id: session_id
//       })
//     });

//     const data = await res.json();

//     loading.remove();

//     addMessage(data.response || "No response", "bot");

//   } catch (err) {
//     loading.remove();
//     addMessage("❌ Server error", "bot");
//   }
// }





// const API_URL = ""; // 🔥 IMPORTANT: same server (no localhost needed)

// let session_id = null;
// let chatBox = null;

// // ----------------------------
// // INIT DOM
// // ----------------------------
// window.addEventListener("DOMContentLoaded", () => {

//   chatBox = document.getElementById("chat-messages");

//   // ⚠️ safe check
//   const input = document.getElementById("user-input");

//   if (input) {
//     input.addEventListener("keydown", function(e) {
//       if (e.key === "Enter") {
//         sendMessage();
//       }
//     });
//   }

//   initSession();
// });


// // ----------------------------
// // INIT SESSION
// // ----------------------------
// async function initSession() {
//   try {
//     const res = await fetch(`/session`);

//     if (!res.ok) throw new Error("Session API failed");

//     const data = await res.json();
//     session_id = data.session_id;

//     console.log("Session created:", session_id);

//   } catch (err) {
//     console.error("Session error:", err);
//     alert("Backend not connected");
//   }
// }


// // ----------------------------
// // ADD MESSAGE
// // ----------------------------
// function addMessage(text, type) {

//   if (!chatBox) return;

//   const msg = document.createElement("div");
//   msg.className = "message " + type;
//   msg.innerText = text;

//   chatBox.appendChild(msg);

//   chatBox.scrollTop = chatBox.scrollHeight;
// }


// // ----------------------------
// // SEND MESSAGE
// // ----------------------------
// async function sendMessage() {

//   const input = document.getElementById("user-input");

//   if (!input) return;

//   const text = input.value.trim();

//   if (!text) return;

//   if (!session_id) {
//     await initSession();
//   }

//   addMessage(text, "user");
//   input.value = "";

//   const loading = document.createElement("div");
//   loading.className = "message bot";
//   loading.innerText = "Analyzing...";
//   chatBox.appendChild(loading);

//   try {
//     const res = await fetch(`/chat`, {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json"
//       },
//       body: JSON.stringify({
//         message: text,
//         session_id: session_id
//       })
//     });

//     if (!res.ok) {
//       throw new Error(`Server error: ${res.status}`);
//     }

//     const data = await res.json();

//     loading.remove();

//     addMessage(data.response || "⚠️ No response", "bot");

//   } catch (err) {
//     loading.remove();
//     addMessage("❌ Backend error", "bot");
//     console.error(err);
//   }
// }