document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      if (window.location.protocol === "file:") {
        activitiesList.innerHTML = "<p>Please open this page through the app server (for example, http://localhost:8000/) so activities can load.</p>";
        return;
      }

      activitiesList.innerHTML = "<p>Loading activities...</p>";
      const response = await fetch("/activities");
      if (!response.ok) {
        throw new Error(`Failed to load activities: ${response.status}`);
      }
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      const activityEntries = Object.entries(activities || {});
      if (activityEntries.length === 0) {
        activitiesList.innerHTML = "<p>No activities available at this time.</p>";
        return;
      }

      activityEntries.forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const title = document.createElement("h4");
        title.textContent = name;

        const description = document.createElement("p");
        description.textContent = details.description;

        const schedule = document.createElement("p");
        schedule.innerHTML = `<strong>Schedule:</strong> ${details.schedule}`;

        const participants = Array.isArray(details.participants) ? details.participants : [];
        const spotsLeft = details.max_participants - participants.length;
        const availability = document.createElement("p");
        availability.innerHTML = `<strong>Availability:</strong> ${spotsLeft} spots left`;

        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";

        const participantsTitle = document.createElement("p");
        participantsTitle.className = "participants-title";
        participantsTitle.textContent = "Participants";
        participantsSection.appendChild(participantsTitle);

        if (participants.length > 0) {
          const list = document.createElement("ul");
          participants.forEach((participant) => {
            const item = document.createElement("li");
            const participantSpan = document.createElement("span");
            participantSpan.textContent = participant;
            const removeButton = document.createElement("button");
            removeButton.textContent = "×";
            removeButton.className = "remove-participant";
            removeButton.addEventListener("click", async () => {
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(name)}/signup?email=${encodeURIComponent(participant)}`,
                  { method: "DELETE" }
                );
                if (response.ok) {
                  fetchActivities(); // Refresh the list
                } else {
                  const result = await response.json();
                  alert(result.detail || "Failed to remove participant");
                }
              } catch (error) {
                alert("Failed to remove participant");
                console.error("Error removing participant:", error);
              }
            });
            item.appendChild(participantSpan);
            item.appendChild(removeButton);
            list.appendChild(item);
          });
          participantsSection.appendChild(list);
        } else {
          participantsSection.classList.add("participants-empty");
          const noParticipants = document.createElement("p");
          noParticipants.innerHTML = `<strong>Participants:</strong> None yet.`;
          participantsSection.appendChild(noParticipants);
        }

        activityCard.appendChild(title);
        activityCard.appendChild(description);
        activityCard.appendChild(schedule);
        activityCard.appendChild(availability);
        activityCard.appendChild(participantsSection);

        activitiesList.appendChild(activityCard);

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
