// Initialize cart only once when the page loads
let cart = JSON.parse(localStorage.getItem('cart')) || [];

function getATCButtons() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    let totalCost = 0;
    document.getElementById('cart-count').innerText = cart.reduce((total,product)=>total+product.ordered_quantity,0);

    addToCartButtons.forEach(button => {
        if (!button.hasEventListener) {
            button.hasEventListener = true; // Mark the button to avoid attaching multiple event listeners
            button.addEventListener('click', function(e) {
                var product = button.getAttribute('data-product-id');
                product = JSON.parse(product.replace(/'/g, '"'));

                // Check if the product is already in the cart
                const existingProductIndex = cart.findIndex(item => item.product_id === product.product_id);
                if (existingProductIndex !== -1) {
                    // Product already exists, update the ordered_quantity
                    if(cart[existingProductIndex].ordered_quantity===product.available_quantity){
                        alert("No more items available")
                        return cart
                    }
                    cart[existingProductIndex].ordered_quantity += 1;

                } else {
                    // Product doesn't exist, add it to the cart
                    product.ordered_quantity = 1;
                    cart.push(product);
                }
                totalCost += product.cost;
                document.getElementById('cart-count').innerText = cart.reduce((total,product)=>total+product.ordered_quantity,0);
            });
        }
    });

    console.log(cart);
    return cart;
}


function getViewProductButtons() {
    console.log("Get view Products");
    const viewProductButtons = document.querySelectorAll('.view-product');
    let totalCost = 0;

    viewProductButtons.forEach(button => {
        // Check if the event listener has been attached before attaching it
        if (!button.hasEventListener) {
            button.hasEventListener = true; // Mark the button to avoid attaching multiple event listeners
            button.addEventListener('click', function(e) {
                console.log("clicked");
                let product = button.getAttribute('data-product-id');
                product = JSON.parse(product.replace(/'/g, '"'));
                openProductModal(product);
            });
        }
    });
}

// ------------- View Product Section -------------- //
function openProductModal(product) {
    var modal = document.getElementById('productModal');
    var modalContent = document.getElementById('product-details');

    modalContent.innerHTML = `
             <div class = "view-product-div">
                <div class = "pl-4">
                  <img id="product-image" width="400" height="400" alt="${product.name}" src="${product.image_url}" />
                </div>
            
                <div class="view-product-details">
                  <h2 style = "font-size: 32px; font-weight: 700">${product.name}</h2>
                  <p><b>Cost:</b> ${product.cost}</p>
                  <p><b>Dimensions:</b> ${product.dimensions}</p>
                  <p><b>Color:</b> ${product.color}</p>
                  <p><b>Brand:</b> ${product.brand}</p>
                  <p><b>Material:</b> ${product.material}</p>
                  <p><b>Weight:</b> ${product.weight}</p>
                  <p><b>Rating:</b> ${product.rating}</p>
                  <p><b>Description:</b> ${product.description}</p>
                  <!-- Add other details as needed -->
                </div>
            </div>`;
    modal.style.display = 'block';
}

function getProductsByCategory(category) {
    if (category.toLowerCase() === 'all') {
        return products;
    } else {
        return products.filter(product => product.category === category);
    }
}

function loadProducts(category) {
    const productListElement = document.getElementById('product-type');
    productListElement.innerHTML = '';

    const filteredProducts = getProductsByCategory(category);

    filteredProducts.forEach(product => {
        if (product.available_quantity > 0) {
            const productElement = document.createElement('div');
            productElement.className = 'product';
            productElement.innerHTML = `
            <img src="${product.image_url}" alt="${product.name}" class="product-image">
            <p>Name: ${product.name}</p>
            <p>${product.color}</p>
            <p>Price: $${product.cost}</p>
            <p>ID: ${product.product_id}</p>
            <button class="add-to-cart" data-product-id='${JSON.stringify(product)}' id="add-cart">
                Add to Cart
            </button>
            <button class="view-product" data-product-id='${JSON.stringify(product)}' id="view-cart">
                View Product
            </button>
        `;
            productListElement.appendChild(productElement);
        }
    });

    // Reattach event listeners for the "Add to Cart" buttons
    getATCButtons();
    getViewProductButtons();
    return filteredProducts; // Return the filtered products
}

function getCancelButtons() {
    const cancelButtons = document.querySelectorAll('.cancel-order-button');
    cancelButtons.forEach(button => {
        if (!button.hasEventListener) {
            button.hasEventListener = true; // Mark the button to avoid attaching multiple event listeners
            button.addEventListener('click', function(e) {
                var orderID = button.getAttribute('data-product-id');
                console.log(orderID);
                const url = 'http://localhost:5000/customer/cancel_order';
                const order = orders.filter(order=>order.order_id == orderID);
                const customerID = order[0].customer_id;
                console.log(order);
                let orderPayload = {
                    "order_id": orderID,
                    "customer_id": customerID
                };
                console.log(orderPayload);
                postData(url, orderPayload)
                    .then(responseData => {
                            console.log('Success:', responseData);
                             orders.map(order => {
                                if(order.order_id == orderID){
                                    order.order_status = "cancelled";
                                    button.parentElement.parentElement.querySelector('.order-status').innerText = order.order_status;
                                    button.style.visibility = 'hidden';
                                }
                            });
                            console.log(orders);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            });
        }
    });
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

document.addEventListener('DOMContentLoaded', function() {
    var products = JSON.parse(JSON.stringify(productsData)); // Copy the data to a new array

    var orders = JSON.parse(JSON.stringify(ordersData)); // Copy the data to a new array
    const allProductsLink = document.getElementById('category-home');
    const coffeeTableLink = document.getElementById('coffee-table-link');
    const diningChairLink = document.getElementById('dining_chair-link');
    const diningSetLink = document.getElementById('dining_set_link');
    const officeChairLink = document.getElementById('office-chair-link');
    const reclinerLink = document.getElementById('recliners-link');
    const shoeCabinetLink = document.getElementById('shoe-cabinet-link');
    const sofaLink = document.getElementById('sofa-link');


    // Initial loading of products and attaching event listeners
    const initialFilteredProducts = loadProducts('all');
    getATCButtons(); // Attach event listeners
    getViewProductButtons();

    allProductsLink.addEventListener('click', function(event) {
        event.preventDefault();
        const filteredProducts = loadProducts('all');
        console.log("Load cart", cart);
    });

    coffeeTableLink.addEventListener('click', function(event) {
        event.preventDefault();
        const filteredProducts = loadProducts('coffee_table');
        console.log("Load cart", cart);
    });

    diningChairLink.addEventListener('click', function(event) {
        event.preventDefault();
        const filteredProducts = loadProducts('dining_chair');
        console.log("Load cart", cart);
    });

    diningSetLink.addEventListener('click', function(event) {
        event.preventDefault();
        const filteredProducts = loadProducts('dining_set');
        console.log("Load cart", cart);
    });

    officeChairLink.addEventListener('click', function(event) {
        event.preventDefault();
        const filteredProducts = loadProducts('office_chair');
        console.log("Load cart", cart);
    });

    reclinerLink.addEventListener('click', function(event) {
        event.preventDefault();
        const filteredProducts = loadProducts('reclyner');
        console.log("Load cart", cart);
    });

    shoeCabinetLink.addEventListener('click', function(event) {
        event.preventDefault();
        const filteredProducts = loadProducts('shoe_cabinet');
        console.log("Load cart", cart);
    });

    sofaLink.addEventListener('click', function(event) {
        event.preventDefault();
        const filteredProducts = loadProducts('sofa');
        console.log("Load cart", cart);
    });

    // Go To Cart
    document.getElementById('go-to-cart-button').addEventListener('click', function() {
        if(cart.length > 0) {
            let cartString = JSON.stringify(cart);
            localStorage.setItem('cart', cartString);
            window.location.href = `/customer/cart_page`;
        }
    });


    // -------------User Profile Section--------------- //
    const userDropdown = document.getElementById('user-dropdown');
    const userDropdownContent = document.getElementById('user-dropdown-content');

    userDropdown.addEventListener('click', function() {
        userDropdownContent.classList.toggle('show');
    });

    // Add click events for dropdown items
    document.getElementById('logout').addEventListener('click', function() {
        console.log("Logout");
        // Implement logout functionality
        // Example: window.location.href = 'logout_page';
        localStorage.setItem("cart","");
        localStorage.setItem("cData","");
        window.location.href = '/';
    });

    document.getElementById('my-orders').addEventListener('click', function() {
        document.getElementById('ordersModal').style.display = 'block';

        let orderModal = document.getElementById('order-model');

        orders.forEach(order => {
            var orderHTML = `
            <div class="order">
                <div class="order-head">
                    <div>
                        <div class="order-number">Order #${order.order_id}</div>
                        <div class="order-status">${order.order_status}</div>
                    </div>
                    <div>
                        <button class="cancel-order-button" 
                                data-product-id='${order.order_id}' 
                                id="cancel-order" style="background-color: red; visibility: ${order.order_status.toLowerCase() === 'cancelled' ? 'hidden' : 'visible'};" >
                            Cancel Order
                        </button>
                    </div>
                </div>
                <p class="total-cost">Total Cost: $${order.total_cost}</p>
                <div class="orders-list">
                   ${order.products.map(currentProduct => {
                        var product = products.find(p => p.product_id === currentProduct.product_id);
                        if (product) {
                            return `
                                <div class="product-card">
                                    <img src="${product.image_url}" alt="${product.name}" class="order-image">
                                    <div class="product-details">
                                        <p>Name: ${product.name}</p>
                                        <p>Product ID: ${product.product_id}</p>
                                        <p>Quantity: ${currentProduct.quantity}</p>
                                    </div>
                                </div>
                            `;
                        } else {
                            return ''; // Handle if product is not found
                        }
                    }).join('')}
                </div>
            </div>
        `;

            // Append each order's HTML to the container
            orderModal.innerHTML += orderHTML;
        });

        getCancelButtons();

    });

    document.getElementById('profile').addEventListener('click', function() {
        document.getElementById('profileModal').style.display = 'block';
    });

    // -------------User Profile Section--------------- //
});