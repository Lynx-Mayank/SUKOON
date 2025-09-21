// Wait until DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  // FAQ toggle
  const faqItems = document.querySelectorAll(".faq-item");

  faqItems.forEach(item => {
    item.addEventListener("click", () => {
      item.classList.toggle("active");

      const content = item.querySelector("p");
      if (content) {
        content.style.display = item.classList.contains("active") ? "block" : "none";
      }
    });
  });

  // Optional: Scroll to top button
  const scrollBtn = document.createElement("button");
  scrollBtn.innerText = "⬆";
  scrollBtn.className = "scroll-top-btn";
  document.body.appendChild(scrollBtn);

  // Show button on scroll
  window.addEventListener("scroll", () => {
    scrollBtn.style.display = window.scrollY > 300 ? "block" : "none";
  });

  // Scroll to top when clicked
  scrollBtn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
});
<div class="toolkit-card" onclick="location.href='chatbot.html'">
  <h3>Instant AI Chatbot Support</h3>
  <p>Get instant support and answers anytime you need it.</p>
</div>
