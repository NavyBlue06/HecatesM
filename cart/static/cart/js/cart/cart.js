document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".add-to-cart");

    buttons.forEach(button => {
        button.addEventListener("click", function () {
            const productId = this.dataset.productId;

            fetch("/cart/ajax/add/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ product_id: productId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update cart count in the navbar
                    const cartCount = document.getElementById("cart-count");
                    if (cartCount) {
                        cartCount.innerText = data.cart_quantity;
                    }

                    // Show feedback
                    showToast("🛒 Added to cart!");
                }
            });
        });
    });

    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                return cookie.substring("csrftoken=".length, cookie.length);
            }
        }
        return "";
    }

    function showToast(message) {
        const toast = document.createElement("div");
        toast.className = "toast position-fixed bottom-0 end-0 m-3 bg-success text-white p-2 rounded shadow";
        toast.innerText = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }
});
