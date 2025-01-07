document.getElementById("registrationForm").onsubmit = function(event) {
    event.preventDefault();
    // Simulate form submission success
    fetch("{% url 'register' %}", {
      method: "POST",
      body: new FormData(this)
    }).then(response => {
      if (response.ok) {
        // Show popup on successful registration
        document.getElementById("emailConfirmPopup").style.display = "block";
      }
    });
  };

  function redirectToSignIn() {
    window.location.href = "{% url 'login' %}";
  }