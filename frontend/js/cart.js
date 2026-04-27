function saveCart() {
  localStorage.setItem("medi_cart", JSON.stringify(cart));
  updateCartCount();
  renderProducts();
}

function addToCart(id) {
  const prod = products.find(p => p.id === id);
  const item = cart.find(c => c.id === id);
  if (item) { item.qty++; }
  else { cart.push({ id, name: prod.name, price: prod.price, qty: 1 }); }
  showToast(`${prod.name} added to cart ✓`);
  saveCart();
}

function changeQty(id, delta) {
  const item = cart.find(c => c.id === id);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) cart = cart.filter(c => c.id !== id);
  saveCart();
}

function removeFromCart(id) {
  cart = cart.filter(c => c.id !== id);
  saveCart();
  renderCartModal();
}

function updateCartCount() {
  const total = cart.reduce((s, i) => s + i.qty, 0);
  document.getElementById("cartCount").textContent = total;
}

function renderCartModal() {
  const el = document.getElementById("cartItems");
  const footer = document.getElementById("cartFooter");
  if (!cart.length) {
    el.innerHTML = `<div class="cart-empty"><i class="fa-solid fa-cart-shopping"></i><p>Your cart is empty</p></div>`;
    footer.style.display = "none";
    return;
  }
  footer.style.display = "block";
  const total = cart.reduce((s, i) => s + i.price * i.qty, 0);
  document.getElementById("cartTotal").textContent = `₹${total}`;
  el.innerHTML = cart.map(item => `
    <div class="cart-item">
      <div class="cart-item-info">
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-price">₹${item.price} × ${item.qty} = ₹${item.price * item.qty}</div>
      </div>
      <div class="cart-item-qty">
        <button class="cart-qty-btn" onclick="changeQty(${item.id},-1);renderCartModal()">−</button>
        <span class="cart-qty-num">${item.qty}</span>
        <button class="cart-qty-btn" onclick="changeQty(${item.id},1);renderCartModal()">+</button>
        <button class="btn-remove" onclick="removeFromCart(${item.id})" title="Remove" style="margin-left:6px;">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    </div>`).join('');
}

function checkout() {
  if (!localStorage.getItem("isLoggedIn")) {
    closeModal("cartModal");
    setTimeout(() => openModal("loginModal"), 200);
    showToast("Please login to checkout");
    return;
  }
  showToast("🎉 Order placed successfully!");
  cart = [];
  saveCart();
  renderCartModal();
  setTimeout(() => closeModal("cartModal"), 800);
}

// ═══════════════════════════════════════════
//  MODALS
// ═══════════════════════════════════════════
function openModal(id) {
  document.getElementById(id).classList.add("open");
  if (id === "cartModal") renderCartModal();
  document.body.style.overflow = "hidden";
}
function closeModal(id) {
  document.getElementById(id).classList.remove("open");
  document.body.style.overflow = "";
}
document.querySelectorAll('.modal-overlay').forEach(m => {
  m.addEventListener('click', e => { if (e.target === m) closeModal(m.id); });
});
