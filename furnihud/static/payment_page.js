let cartDetails = localStorage.getItem('cart');
let cData = JSON.parse(localStorage.getItem('cData'));
let payload = {
    "customer_id": "",
    "products": [],
    "total_cost": 0,
    "delivery_type": "delivery"
};
let cardPayload = {
    "payment_date": "",
    "payment_method": "",
    "amount": 0,
    "order_id":"",
};

if (cData && cData !== 'undefined') {
    payload.customer_id = cData.id;
}

if (cartDetails && cartDetails !== 'undefined') {
    cartDetails = JSON.parse(cartDetails);

    payload.products = cartDetails.map(product => {
        let info = {};
        info.product_id = product.product_id;
        info.quantity = 1;
        return info;
    });

   const cartCost = cartDetails.reduce((sum, product) => sum + product.cost, 0);
   payload.total_cost = cartCost;

    console.log(payload);

} else {
    console.error("Cart details not found or invalid.");
}

document.getElementById("total-cost").innerText = parseFloat(payload.total_cost.toFixed(2));


let payButton = document.getElementById('payment-button');

// Attach the onclick event handler function to the button
payButton.onclick = proceedPayment;

function proceedPayment(e) {
    e.preventDefault();
    const cardNumber = document.getElementById('card-number').value;
    if (!isValidCardNumber(cardNumber)) {
        document.getElementById("card-error").innerText = "Please enter a 16-digit credit/debit card number";
        return;
    }else{
        document.getElementById("card-error").innerText = "";

    }

    const cardHolder = document.getElementById('card-holder').value;
    if (!isValidCardHolder(cardHolder)) {
        document.getElementById("card-name").innerText = "Please enter valid cardholder's name";
        return;
    } else{
        document.getElementById("card-name").innerText = "";

    }

    const expiryDate = document.getElementById('expiry').value;
    if (!isValidExpiryDate(expiryDate)) {
        document.getElementById("card-expiry").innerText = "Please enter valid expiry date";
        return;
    } else{
        document.getElementById("card-expiry").innerText = "";

    }

    const cvv = document.getElementById('cvv').value;
    if (!isValidCVV(cvv)) {
        document.getElementById("card-cvv").innerText = "Please enter a 3-digit cvv number";
        return;
    } else{
        document.getElementById("card-cvv").innerText = "";

    }

    const deliveryType = document.getElementById("delivery-type").value;
    payload.delivery_type = deliveryType;
    console.log(payload)
    const url = 'http://localhost:5000/add_order';
    postData(url, payload)
        .then(responseData => {
            console.log('Success:', responseData);
            if(responseData.order_id !=undefined) {
                // window.location.href = `order_summary`;
                const url1 = 'http://localhost:5000/add_payment';
                cardPayload.payment_date = new Date().toLocaleString();
                cardPayload.payment_method = "card";
                cardPayload.amount = cartDetails.reduce((sum, product) => sum + product.cost, 0);;
                cardPayload.order_id = responseData.order_id;

                console.log("CardPayload",cardPayload);
                postData(url1, cardPayload)
                    .then(responseData => {
                        if(responseData.payment_id != undefined) {
                            console.log('Success:', responseData);
                            window.location.href = `order_summary`;
                        } else {
                            window.location.href = `failure_page`;
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        window.location.href = `failure_page`;
                    });
            } else{
               window.location.href = `failure_page`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
               window.location.href = `failure_page`;
        });
}

// Validation functions
function isValidCardNumber(cardNumber) {
    const cardNumberRegex = /^\d{16}$/;
    return cardNumberRegex.test(cardNumber);
}

function isValidCardHolder(cardHolder) {
    const cardHolderRegex = /^[A-Za-z\s]+$/;
    return cardHolderRegex.test(cardHolder);
}

function isValidExpiryDate(expiryDate) {
    const expiryDateRegex = /^(0[1-9]|1[0-2])\/\d{2}$/;

    if (!expiryDateRegex.test(expiryDate)) {
        return false;
    }

    const currentDate = new Date();
    const currentYear = currentDate.getFullYear() % 100; // Get last two digits of the current year
    const currentMonth = currentDate.getMonth() + 1; // getMonth returns 0-11, so add 1

    const [expiryMonth, expiryYear] = expiryDate.split('/').map(Number);

    // Check if the expiry date is in the future
    if (expiryYear > currentYear || (expiryYear === currentYear && expiryMonth >= currentMonth)) {
        return true;
    }

    return false;
}


function isValidCVV(cvv) {
    const cvvRegex = /^\d{3}$/;
    return cvvRegex.test(cvv);
}


function postData(url = '', data = {}) {
    // Default options are marked with *
    return fetch(url, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data), // body data type must match "Content-Type" header
        })
        .then(response => response.json());
}