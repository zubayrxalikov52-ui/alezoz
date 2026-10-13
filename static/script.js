/* ==========================================================================
   ALLON CAFE - MENU & INTERACTIVE PAGE SCRIPT (script.js)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    const menuBtn = document.querySelector("#menu-btn");
    const menuDropdown = document.querySelector("#menu-dropdown");
    const categories = document.querySelectorAll(".category");
    const foodList = document.querySelector("#food-list");
    const foodCards = Array.from(document.querySelectorAll(".food-card"));
    const plusButtons = document.querySelectorAll(".plus");
    const minusButtons = document.querySelectorAll(".minus");

    if (foodList && foodCards.length > 0) {
        /* BO'LIMLAR */
        const groups = [
            { key: "food",    title: "🍽 Taomlar" },
            { key: "salad",   title: "🥗 Salatlar" },
            { key: "snack",   title: "🍟 Snacklar" },
            { key: "drink",   title: "🥤 Ichimliklar" },
            { key: "dessert", title: "🍰 Desertlar" }
        ];

        const titles = [];

        // Har bir bo'lim uchun sarlavha yaratamiz va kartalarni shu sarlavha ostiga joylaymiz
        groups.forEach((group) => {
            const groupCards = foodCards.filter((card) => card.dataset.category === group.key);
            if (groupCards.length > 0) {
                const title = document.createElement("h2");
                title.className = "category-title";
                title.dataset.category = group.key;
                title.textContent = group.title;

                foodList.appendChild(title);
                titles.push(title);

                groupCards.forEach((card) => foodList.appendChild(card));
            }
        });

        /* KATEGORIYA TANLASH */
        categories.forEach((category) => {
            category.addEventListener("click", () => {
                categories.forEach((item) => item.classList.remove("active"));
                category.classList.add("active");

                const selected = category.dataset.category;

                // Sarlavhalar
                titles.forEach((title) => {
                    const visible = selected === "all" || title.dataset.category === selected;
                    title.style.display = visible ? "" : "none";
                });

                // Kartalar
                foodCards.forEach((card) => {
                    const visible = selected === "all" || card.dataset.category === selected;
                    card.style.display = visible ? "" : "none";
                });

                if (menuDropdown) menuDropdown.classList.remove("show");
                foodList.scrollIntoView({ behavior: "smooth", block: "start" });
            });
        });
    }

    /* MENYU TUGMASI */
    if (menuBtn && menuDropdown) {
        menuBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            menuDropdown.classList.toggle("show");
        });

        document.addEventListener("click", (event) => {
            if (!menuDropdown.contains(event.target) && event.target !== menuBtn) {
                menuDropdown.classList.remove("show");
            }
        });
    }

    /* CARD PRODUCT EXTRACTOR */
    function extractCardProduct(card) {
        const title = card.querySelector("h3") ? card.querySelector("h3").textContent.trim() : "";
        const priceText = card.querySelector("strong") ? card.querySelector("strong").textContent.trim() : "0";
        const cleanPrice = parseInt(priceText.replace(/\D/g, "")) || 0;
        const img = card.querySelector("img") ? card.querySelector("img").src : "";
        const category = card.dataset.category || "food";
        const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, "-");
        return { name: title, price: cleanPrice, image: img, category, slug, id: slug };
    }

    function syncCardQuantities() {
        const cart = typeof AllonApp !== "undefined" ? AllonApp.getCart() : [];
        foodCards.forEach(card => {
            const prod = extractCardProduct(card);
            const item = cart.find(i => i.name === prod.name || i.slug === prod.slug);
            const qtyElem = card.querySelector(".quantity");
            if (qtyElem) {
                qtyElem.textContent = item ? item.quantity : 0;
            }
        });
    }

    function renderSidebarCart() {
        const cartList = document.querySelector("#cart-list");
        const totalElem = document.querySelector("#total");
        const cartCountElem = document.querySelector("#cart-count");

        if (!cartList) return;

        const cart = typeof AllonApp !== "undefined" ? AllonApp.getCart() : [];
        const total = typeof AllonApp !== "undefined" ? AllonApp.getCartTotal() : 0;
        const count = typeof AllonApp !== "undefined" ? AllonApp.getCartCount() : 0;
        const isRu = (typeof AllonApp !== "undefined" && AllonApp.getCurrentLanguage() === 'ru');
        const curr = isRu ? 'сум' : "so‘m";

        if (totalElem) totalElem.textContent = total.toLocaleString("uz-UZ");
        if (cartCountElem) cartCountElem.textContent = count;

        if (cart.length === 0) {
            cartList.innerHTML = `
                <div class="empty-cart">
                    <span>🛒</span>
                    <h3>${isRu ? 'Корзина пуста' : 'Savat bo‘sh'}</h3>
                    <p>${isRu ? 'Выберите блюда из меню' : 'Menyudan taom tanlang'}</p>
                </div>
            `;
            return;
        }

        let html = "";
        cart.forEach(item => {
            const displayName = (typeof AllonApp !== "undefined" && AllonApp.translateItemName) ? AllonApp.translateItemName(item.name) : item.name;
            const delTitle = isRu ? 'Удалить' : 'O‘chirish';
            html += `
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.08);">
                    <div style="flex-grow:1; padding-right:10px;">
                        <strong style="display:block; font-size:14px; margin-bottom:2px; color:var(--white);">${displayName}</strong>
                        <small style="color:var(--gold); font-size:12px;">${item.price.toLocaleString("uz-UZ")} ${curr} × ${item.quantity}</small>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="display:flex; align-items:center; gap:6px; background:rgba(255,255,255,0.06); padding:2px 6px; border-radius:14px;">
                            <button onclick="changeCartItem('${item.id}', -1)" style="border:none; background:transparent; color:#fff; cursor:pointer; font-size:14px; padding:0 4px;">−</button>
                            <span style="font-size:12px; min-width:14px; text-align:center; color:#fff;">${item.quantity}</span>
                            <button onclick="changeCartItem('${item.id}', 1)" style="border:none; background:transparent; color:#fff; cursor:pointer; font-size:14px; padding:0 4px;">+</button>
                        </div>
                        <button onclick="removeCartItem('${item.id}')" style="border:none; background:rgba(228,91,91,0.15); color:#e45b5b; width:24px; height:24px; border-radius:50%; cursor:pointer; font-size:12px; display:grid; place-items:center;" title="${delTitle}">✕</button>
                    </div>
                </div>
            `;
        });
        cartList.innerHTML = html;
    }

    window.addEventListener('appLanguageChanged', () => {
        renderSidebarCart();
    });

    window.changeCartItem = function(id, delta) {
        if (typeof AllonApp !== "undefined") {
            AllonApp.updateQuantity(id, delta);
            syncCardQuantities();
            renderSidebarCart();
        }
    };

    window.removeCartItem = function(id) {
        if (typeof AllonApp !== "undefined") {
            AllonApp.removeFromCart(id);
            syncCardQuantities();
            renderSidebarCart();
        }
    };

    /* PLUS */
    plusButtons.forEach((button) => {
        button.addEventListener("click", (e) => {
            e.stopPropagation();
            const card = button.closest(".food-card");
            const prod = extractCardProduct(card);
            if (typeof AllonApp !== "undefined") {
                AllonApp.addToCart(prod);
                syncCardQuantities();
                renderSidebarCart();
            }
        });
    });

    /* MINUS */
    minusButtons.forEach((button) => {
        button.addEventListener("click", (e) => {
            e.stopPropagation();
            const card = button.closest(".food-card");
            const prod = extractCardProduct(card);
            if (typeof AllonApp !== "undefined") {
                AllonApp.updateQuantity(prod.id, -1);
                syncCardQuantities();
                renderSidebarCart();
            }
        });
    });

    /* ORDER BUTTON CLICK -> CHECKOUT */
    const orderBtn = document.querySelector("#order-btn");
    if (orderBtn) {
        orderBtn.addEventListener("click", () => {
            const count = typeof AllonApp !== "undefined" ? AllonApp.getCartCount() : 0;
            if (count === 0) {
                const isRu = (typeof AllonApp !== "undefined" && AllonApp.getCurrentLanguage() === 'ru');
                alert(isRu ? "Корзина пуста! Пожалуйста, сначала выберите блюда из меню." : "Savat bo‘sh! Iltimos, avval biror taom tanlang.");
                return;
            }
            window.location.href = "/checkout/";
        });
    }

    // Initialize cart sync
    syncCardQuantities();
    renderSidebarCart();
});