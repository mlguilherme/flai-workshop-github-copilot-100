document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities", { cache: "no-store" });
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4></h4>
          <p class="activity-description"></p>
          <p><strong>Schedule:</strong> <span class="activity-schedule"></span></p>
          <p><strong>Availability:</strong> <span class="activity-spots"></span></p>
          <div class="participants-section">
            <p class="participants-title"></p>
          </div>
        `;

        activityCard.querySelector("h4").textContent = name;
        activityCard.querySelector(".activity-description").textContent = details.description;
        activityCard.querySelector(".activity-schedule").textContent = details.schedule;
        activityCard.querySelector(".activity-spots").textContent = `${spotsLeft} spots left`;
        activityCard.querySelector(".participants-title").textContent =
          `Participants (${details.participants.length}/${details.max_participants}):`;

        const participantsSection = activityCard.querySelector(".participants-section");

        if (details.participants.length > 0) {
          const ul = document.createElement("ul");
          ul.className = "participants-list";
          details.participants.forEach(p => {
            const li = document.createElement("li");
            const span = document.createElement("span");
            span.className = "participant-email";
            span.textContent = p;
            const btn = document.createElement("button");
            btn.className = "delete-btn";
            btn.dataset.activity = name;
            btn.dataset.email = p;
            btn.title = "Unregister";
            btn.setAttribute("aria-label", "Unregister");
            btn.textContent = "\uD83D\uDDD1";
            btn.addEventListener("click", async () => {
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(name)}/signup?email=${encodeURIComponent(p)}`,
                  { method: "DELETE" }
                );
                if (response.ok) {
                  fetchActivities();
                } else {
                  const result = await response.json();
                  alert(result.detail || "Failed to unregister");
                }
              } catch (error) {
                console.error("Error unregistering:", error);
              }
            });
            li.appendChild(span);
            li.appendChild(btn);
            ul.appendChild(li);
          });
          participantsSection.appendChild(ul);
        } else {
          const noParticipants = document.createElement("p");
          noParticipants.className = "no-participants";
          noParticipants.textContent = "No participants yet. Be the first!";
          participantsSection.appendChild(noParticipants);
        }

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
