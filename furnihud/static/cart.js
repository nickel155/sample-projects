
let cartProducts = JSON.parse(localStorage.getItem('cart')) || []; // Initialize as an empty array if no data is found

// Use the received data
document.getElementById('total-items').innerText = cartProducts.length;

const productData = document.getElementById("cart-products");
let totalCartPrice = 0;
for (let i = 0; i < cartProducts.length; i++) {
    totalCartPrice = totalCartPrice + Number(cartProducts[i].cost*cartProducts[i].ordered_quantity);
    const div = document.createElement('div');
   div.innerHTML = `
    <div class='d-flex flex-row justify-content-between align-items-center pt-lg-4 pt-2 pb-3 border-bottom mobile'>
        <div class='d-flex flex-row align-items-center'>
            <div><img id='image' width='150' height='150' alt='' src=${cartProducts[i].image_url} /></div>
            <div class='d-flex flex-column pl-md-3 pl-1'>
                <div><h6>${cartProducts[i].name}</h6></div>
                <div>Brand: <span class='pl-2'>${cartProducts[i].brand}</span></div>
                <div>Color:<span class='pl-3'>${cartProducts[i].color}</span></div>
            </div>
        </div>
        <div class='pl-md-0 pl-1'><b>${cartProducts[i].cost}</b></div>
        <div class='pl-md-0 pl-2'>
<!--            <span class='fa fa-minus-square text-secondary'></span>-->
            <span class='px-md-3 px-1'>${cartProducts[i].ordered_quantity}</span>
<!--            <span class='fa fa-plus-square text-secondary'></span>-->
        </div>
        <div class='pl-md-0 pl-1'><b>${cartProducts[i].cost}</b></div>
        <div class='close' id='close-product' onclick='deleteProduct("${cartProducts[i].name}")'>&times;</div>
    </div>`;
    productData.appendChild(div);
}
document.getElementById('total-cart').innerText = "$" + totalCartPrice + "";

document.getElementById('payment-button').addEventListener('click', function () {
    if(cartProducts.length > 0){
        document.getElementById('payment-button').disabled = false;
        window.location.href = `payment_page`;
    } else {
        document.getElementById('payment-button').disabled = true;
    }

});

document.getElementById('go-back').addEventListener('click', function () {
    // window.history.go(-1);
    let cData = JSON.parse(localStorage.getItem('cData'));
        let customer_id = '';
        if (cData && cData !== 'undefined') {
            customer_id = cData.id;
            window.location.href = `/get_product_page/${customer_id}`;
        }
    // return false;
});

productData.addEventListener('click', function (event) {
    if (event.target.classList.contains('close')) {
        const productName = event.target.parentNode.querySelector('h6').innerText;
        deleteProduct(productName);
    }
});

// Define the deleteProduct function
function deleteProduct(name) {
    cartProducts = cartProducts.filter(item => item.name !== name);
    console.log(name);
    localStorage.setItem('cart', JSON.stringify(cartProducts));
    location.reload(); // Refresh the page after the deletion
}

 var jsonData = {
            productName: "Example Product",
            price: 19.99,
            quantity: 2
        };

        // Send JSON data to the payment page
        window.postMessage({ type: 'cartData', data: jsonData }, '*');
