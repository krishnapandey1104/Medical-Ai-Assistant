// =====================================================
//  CONFIG
// =====================================================
const API_URL = window.location.origin;
let chartInstance = null;
let SESSION_ID = null;

// =====================================================
//  CREATE SESSION (IMPORTANT)
// =====================================================
async function createSession() {
  try {
    const res = await fetch(`${API_URL}/session`);
    const data = await res.json();
    SESSION_ID = data.session_id;
    console.log('🆕 Session:', SESSION_ID);
  } catch (err) {
    console.error('Session error:', err);
  }
}

// =====================================================
//  UPLOAD REPORT
// =====================================================
async function uploadReport() {
  //  SESSION FIX
  if (!SESSION_ID) {
    await createSession();
  }

  const fileInput = document.getElementById('reportFile');
  const resultBox = document.getElementById('resultBox');
  const chartCanvas = document.getElementById('trendChart');

  if (!resultBox) return;

  const file = uploadedFile;

  if (!file) {
    alert('Upload file first');
    return;
  }

  if (file.size > 10 * 1024 * 1024) {
    alert('File must be less than 10MB');
    return;
  }

  const isValidType = file.type.includes('pdf') || file.type.includes('image');

  if (!isValidType) {
    alert('Only PDF or Image allowed');
    return;
  }

  // ----------------------------
  // SESSION INIT
  // ----------------------------
  // if (!SESSION_ID) {
  //     alert("Session not initialized. Please refresh the page.");
  //     await createSession();
  // }

  // ----------------------------
  // LOADING UI
  // ----------------------------
  resultBox.innerHTML = `
        <div style="text-align:center; padding:20px;">
            <p>🔍 Analyzing report...</p>
            <div class="loader"></div>
        </div>
    `;

  // reset chart
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', SESSION_ID);

  try {
    const res = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    const data = await res.json();

    //  SAVE SESSION (IMPORTANT)
    SESSION_ID = data.session_id;

    // ----------------------------
    //  SUMMARY
    // ----------------------------
    let html = `
            <div class="card">
                <h3>🧠 AI Report Summary</h3>
                <p>${data.summary || 'No summary available'}</p>
            </div>
        `;

    // ----------------------------
    //  LAB TABLE
    // ----------------------------
    if (Array.isArray(data.tables) && data.tables.length > 0) {
      html += `
                <div class="card">
                    <h3>📊 Lab Values</h3>
                    <table class="lab-table">
                        <tr>
                            <th>Test</th>
                            <th>Value</th>
                            <th>Status</th>
                        </tr>
            `;

      data.tables.forEach((t) => {
        let color = '#000';
        if (t.status === 'HIGH') color = 'red';
        if (t.status === 'LOW') color = 'orange';

        html += `
                    <tr>
                        <td>${t.test || '-'}</td>
                        <td>${t.value || '-'} ${t.unit || ''}</td>
                        <td style="color:${color}; font-weight:bold;">
                            ${t.status || 'UNKNOWN'}
                        </td>
                    </tr>
                `;
      });

      html += `</table></div>`;
    }

    // ----------------------------
    //  TRENDS TEXT
    // ----------------------------
    if (data.trends && Object.keys(data.trends).length > 0) {
      html += `<div class="card"><h3>📈 Trends</h3>`;

      for (const key in data.trends) {
        html += `<p><b>${key}:</b> ${data.trends[key].join(' → ')}</p>`;
      }

      html += `</div>`;
    }

    // ----------------------------
    //  CHATBOT UI
    // ----------------------------
    html += `
            <div class="card">
                <h3>💬 Ask About Report</h3>

                <div id="chatBox" style="
                    height:200px;
                    overflow:auto;
                    border:1px solid #ddd;
                    padding:10px;
                    margin-bottom:10px;
                    background:#fafafa;
                "></div>

                <input id="chatInput"
                    placeholder="Ask about your report..."
                    style="width:70%; padding:8px;" />

                <button onclick="sendMessage()" style="padding:8px;">
                    Send
                </button>
            </div>
        `;

    // ----------------------------
    // RENDER
    // ----------------------------
    resultBox.innerHTML = html;

    // ----------------------------
    //  CHART
    // ----------------------------
    if (chartCanvas && data.trends && Object.keys(data.trends).length > 0) {
      const labels = [];
      const values = [];

      for (const key in data.trends) {
        labels.push(key);
        values.push(data.trends[key].slice(-1)[0]);
      }

      const ctx = chartCanvas.getContext('2d');

      chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Latest Values',
              data: values,
            },
          ],
        },
        options: {
          responsive: true,
        },
      });
    }
  } catch (err) {
    console.error('UPLOAD ERROR:', err);

    resultBox.innerHTML = `
            <div style="color:red; padding:15px;">
                ❌ Failed to analyze report<br>
                Check backend connection
            </div>
        `;
  }
}
// =============================
// AUTO INIT SESSION ON LOAD
// =============================
window.onload = async () => {
  await createSession();
};

// =====================================================
// CHATBOT FUNCTION
// =====================================================
async function sendMessage() {

    const input = document.getElementById('chatInput');
    const chatBox = document.getElementById('chatBox');

    const message = input.value.trim();
    if (!message) return;

    // USER MESSAGE
    chatBox.innerHTML += `<p><b>You:</b> ${message}</p>`;
    input.value = '';

    try {
        const res = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: SESSION_ID
            })
        });

        const data = await res.json();

        // AI RESPONSE (STRUCTURED)
        chatBox.innerHTML += `
        <div class="ai-msg">
            ${data.response.replace(/\n/g, "<br>")}
        </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (err) {
        chatBox.innerHTML += `<p style="color:red;">Error</p>`;
    }
}
window.addEventListener('DOMContentLoaded', () => {
  createSession();
});








// // ----------------------------
// // CONFIG
// // ----------------------------
// const API_URL = ""; // same-origin
// let chartInstance = null;

// // ----------------------------
// // MAIN FUNCTION
// // ----------------------------
// async function uploadReport() {

//     const fileInput = document.getElementById("reportFile");
//     const resultBox = document.getElementById("resultBox");
//     const chartCanvas = document.getElementById("trendChart");

//     if (!fileInput || !resultBox) return;

//     const file = fileInput.files[0];

//     // ----------------------------
//     // VALIDATION
//     // ----------------------------
//     if (!file) {
//         alert("Upload file first");
//         return;
//     }

//     if (file.size > 10 * 1024 * 1024) {
//         alert("File must be less than 10MB");
//         return;
//     }

//     const isValidType =
//         file.type.includes("pdf") ||
//         file.type.includes("image");

//     if (!isValidType) {
//         alert("Only PDF or Image allowed");
//         return;
//     }

//     // ----------------------------
//     // LOADING UI
//     // ----------------------------
//     resultBox.innerHTML = `
//         <div style="text-align:center; padding:20px;">
//             <p>🔍 Analyzing report...</p>
//             <div class="loader"></div>
//         </div>
//     `;

//     // clear previous chart
//     if (chartInstance) {
//         chartInstance.destroy();
//         chartInstance = null;
//     }

//     const formData = new FormData();
//     formData.append("file", file);

//     try {

//         const res = await fetch(`/upload`, {
//             method: "POST",
//             body: formData
//         });

//         if (!res.ok) {
//             throw new Error(`Server error: ${res.status}`);
//         }

//         const data = await res.json();

//         // ----------------------------
//         // SUMMARY CARD
//         // ----------------------------
//         let html = `
//             <div class="card">
//                 <h3>🧠 AI Report Summary</h3>
//                 <p>${data.summary || "No summary available"}</p>
//             </div>
//         `;

//         // ----------------------------
//         // LAB VALUES TABLE
//         // ----------------------------
//         if (Array.isArray(data.tables) && data.tables.length > 0) {

//             html += `
//                 <div class="card">
//                     <h3>📊 Lab Values</h3>
//                     <table class="lab-table">
//                         <tr>
//                             <th>Test</th>
//                             <th>Value</th>
//                             <th>Status</th>
//                         </tr>
//             `;

//             data.tables.forEach(t => {

//                 let color = "#000";
//                 if (t.status === "HIGH") color = "red";
//                 if (t.status === "LOW") color = "orange";

//                 html += `
//                     <tr>
//                         <td>${t.test || "-"}</td>
//                         <td>${t.value || "-"} ${t.unit || ""}</td>
//                         <td style="color:${color}; font-weight:bold;">
//                             ${t.status || "UNKNOWN"}
//                         </td>
//                     </tr>
//                 `;
//             });

//             html += `</table></div>`;
//         }

//         // ----------------------------
//         // TRENDS TEXT
//         // ----------------------------
//         if (data.trends && Object.keys(data.trends).length > 0) {

//             html += `<div class="card"><h3>📈 Trends</h3>`;

//             for (const key in data.trends) {
//                 html += `
//                     <p><b>${key}:</b> ${data.trends[key].join(" → ")}</p>
//                 `;
//             }

//             html += `</div>`;
//         }

//         // ----------------------------
//         // RENDER RESULT
//         // ----------------------------
//         resultBox.innerHTML = html;

//         // ----------------------------
//         // 🔥 CHART.JS GRAPH
//         // ----------------------------
//         if (
//             chartCanvas &&
//             data.trends &&
//             Object.keys(data.trends).length > 0
//         ) {

//             const labels = [];
//             const values = [];

//             for (const key in data.trends) {
//                 labels.push(key);
//                 values.push(data.trends[key].slice(-1)[0]); // latest value
//             }

//             const ctx = chartCanvas.getContext("2d");

//             chartInstance = new Chart(ctx, {
//                 type: "bar",
//                 data: {
//                     labels: labels,
//                     datasets: [{
//                         label: "Latest Values",
//                         data: values
//                     }]
//                 },
//                 options: {
//                     responsive: true
//                 }
//             });
//         }

//     } catch (err) {

//         console.error("UPLOAD ERROR:", err);

//         resultBox.innerHTML = `
//             <div style="color:red; padding:15px;">
//                 ❌ Failed to analyze report<br>
//                 Check backend connection
//             </div>
//         `;
//     }
// }
