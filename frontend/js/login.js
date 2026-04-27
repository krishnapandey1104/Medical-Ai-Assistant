let currentPhone = "";
function sendOtp() {
  const phone = document.getElementById("phoneInput").value;
  if (phone.length !== 10) { showToast("Enter a valid 10-digit number"); return; }
  currentPhone = phone;
  document.getElementById("maskedPhone").textContent = phone.slice(0,3) + "×××××" + phone.slice(-2);
  document.getElementById("phoneStep").style.display = "none";
  document.getElementById("otpStep").style.display = "block";
  showToast("OTP sent to +91 " + phone + " (use 1234)");
}

function otpMove(el, idx) {
  el.value = el.value.replace(/\D/g,'');
  if (el.value) {
    const next = document.querySelectorAll(".otp-digit")[idx + 1];
    if (next) next.focus();
  }
}

function verifyOtp() {
  const otp = [...document.querySelectorAll(".otp-digit")].map(i => i.value).join('');
  if (otp === "1234") {
    document.getElementById("otpStep").style.display = "none";
    document.getElementById("loginSuccess").style.display = "block";
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("userPhone", currentPhone);
    updateLoginState(currentPhone);
    setTimeout(() => closeModal("loginModal"), 1800);
  } else {
    showToast("Wrong OTP. Try 1234");
    document.querySelectorAll(".otp-digit").forEach(i => { i.value = ""; i.style.borderColor = "var(--red)"; });
  }
}

function resendOtp(e) {
  e.preventDefault();
  document.querySelectorAll(".otp-digit").forEach(i => { i.value = ""; i.style.borderColor = ""; });
  showToast("OTP resent! (use 1234)");
}

function googleLogin() {
  showToast("Google Login Successful ✓");
  localStorage.setItem("isLoggedIn", "true");
  localStorage.setItem("userPhone", "GoogleUser");
  updateLoginState("Google");
  setTimeout(() => closeModal("loginModal"), 500);
}

function updateLoginState(phone) {
  document.getElementById("loginBtn").style.display = "none";
  const pill = document.getElementById("userPill");
  pill.classList.add("show");
  const initial = phone === "Google" ? "G" : phone.charAt(0);
  document.getElementById("userAvatar").textContent = initial;
  document.getElementById("userName").textContent = phone === "Google" ? "Google User" : phone.slice(0,4) + "×××";
}

function logoutUser() {
  if (!confirm("Logout from MediReport?")) return;
  localStorage.removeItem("isLoggedIn");
  localStorage.removeItem("userPhone");
  document.getElementById("loginBtn").style.display = "";
  document.getElementById("userPill").classList.remove("show");
  showToast("Logged out successfully");
}