console.log("Stripe elements loaded");

// Retrieve Stripe keys and client secret
const stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
const clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent);

// Debug: Log the clientSecret to ensure it's correct
console.log('Client Secret:', clientSecret);

const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();
const card = elements.create('card', {
    style: {
        base: {
            color: '#000',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSize: '16px',
            '::placeholder': { color: '#aab7c4' }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    }
});
card.mount('#card-element');

// Handle real-time card input errors
card.on('change', function (event) {
    const errorDiv = document.getElementById('card-errors');
    if (event.error) {
        errorDiv.textContent = event.error.message;
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submission
const form = document.getElementById('payment-form');
form.addEventListener('submit', function (ev) {
    ev.preventDefault();

    // Disable form during processing
    card.update({ 'disabled': true });
    document.querySelector('button[type="submit"]').disabled = true;

    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
            billing_details: {
                name: form.full_name.value.trim(),
                phone: form.phone_number.value.trim(),
                email: form.email.value.trim(),
                address: {
                    line1: form.street_address1.value.trim(),
                    line2: form.street_address2.value.trim(),
                    city: form.town_or_city.value.trim(),
                    country: form.country.value,
                    state: form.county.value.trim(),
                    postal_code: form.postcode.value.trim(),
                }
            }
        }
    }).then(function (result) {
        if (result.error) {
            console.error('Payment confirmation error:', result.error);
            console.log('Error type:', result.error.type);
            console.log('Error code:', result.error.code);
            console.log('Error message:', result.error.message);
            document.getElementById('card-errors').textContent = result.error.message;
            card.update({ 'disabled': false });
            document.querySelector('button[type="submit"]').disabled = false;
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                console.log('Payment succeeded, confirming payment...');
                fetch("/checkout/confirm_payment/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                    body: JSON.stringify({ pid: result.paymentIntent.id }),
                })
                .then(response => {
                    console.log('Confirm response status:', response.status);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Confirm data:', data);
                    if (data.order_number) {
                        console.log('Redirecting to success page with order number:', data.order_number);
                        window.location.href = `/checkout/checkout-success/${data.order_number}/`;
                    } else {
                        console.error('Order number not found in confirm response');
                        window.location.href = '/checkout/';
                    }
                })
                .catch(error => {
                    console.error('Confirm error:', error);
                    console.log('Falling back to get_order_number...');
                    fetch("/checkout/get_order_number/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                        },
                        body: JSON.stringify({ pid: result.paymentIntent.id }),
                    })
                    .then(response => {
                        console.log('Fallback fetch response status:', response.status);
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('Fallback data:', data);
                        if (data.order_number) {
                            console.log('Redirecting to success page with fallback order number:', data.order_number);
                            window.location.href = `/checkout/checkout-success/${data.order_number}/`;
                        } else {
                            console.error('Order number not found in fallback response');
                            window.location.href = '/checkout/';
                        }
                    })
                    .catch(error => {
                        console.error('Fallback fetch error:', error);
                        document.getElementById('card-errors').textContent = 'An error occurred while processing your order. Please try again.';
                        card.update({ 'disabled': false });
                        document.querySelector('button[type="submit"]').disabled = false;
                    });
                });
            } else {
                console.log('Payment intent status:', result.paymentIntent.status);
                document.getElementById('card-errors').textContent = 'Payment did not succeed. Please try again.';
                card.update({ 'disabled': false });
                document.querySelector('button[type="submit"]').disabled = false;
            }
        }
    }).catch(error => {
        console.error('Unexpected error during payment confirmation:', error);
        document.getElementById('card-errors').textContent = 'Payment processing failed unexpectedly. Please try again.';
        card.update({ 'disabled': false });
        document.querySelector('button[type="submit"]').disabled = false;
    });
});