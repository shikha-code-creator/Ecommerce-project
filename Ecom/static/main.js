console.log("Sanity check!");

fetch("/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);

   document.querySelector("#submitBtn").addEventListener("click", () => {
      var txtadd=document.getElementById("txtadd").value;
      var txtcty=document.getElementById("txtcty").value;
      var txtsta=document.getElementById("txtsta").value;
      var txtzip=document.getElementById("txtzip").value;
      var tot=txtadd+"|"+txtcty+"|"+txtsta+"|"+txtzip;
      console.log(tot);
    // Get Checkout Session ID
    fetch("/create-checkout-session/?query="+tot)
    .then((result) => { return result.json(); })
    .then((data) => {
      console.log(data);
      // Redirect to Stripe Checkout
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    });
  });
});