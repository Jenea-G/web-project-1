console.log("script loaded");
const tabs = document.querySelectorAll(".join-tab");
const closeBtn = document.getElementById("close-btn");
const deletePicnicBtns = document.querySelectorAll(".delete-picnic-btn");

/** 'First Time Joinging' and 'Returning' Tab selection for guests */
tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const forms = document.querySelectorAll(".join-form");
    const formType = tab.dataset.tab;

    tabs.forEach((tab) => {
      tab.classList.remove("active");
    });

    forms.forEach((form) => {
      form.classList.remove("active");
    });

    tab.classList.add("active");
    document.getElementById(formType).classList.add("active");
  });
});

/** 'Feedback flash messages closing logic' */
if (closeBtn) {
  closeBtn.addEventListener("click", () => {
    const feedback = document.querySelector(".flash-messages");
    feedback.remove();
  });
}

/** Pop-up warning for accidental delete picnic prevention. */
deletePicnicBtns.forEach((deletePicnicBtn) => {
  deletePicnicBtn.addEventListener("click", (event) => {
    event.preventDefault();

    console.log("delete-picnic button clicked");

    const feedback = document.querySelector(".feedback");
    const picnicName = deletePicnicBtn.dataset.picnicName;
    const deleteUrl = deletePicnicBtn.dataset.deleteUrl;

    const messagePopUp = document.createElement("div");
    const p = document.createElement("p");
    const actions = document.createElement("div");
    const cancelAncor = document.createElement("a");
    const confirmForm = document.createElement("form");
    const confirmBtn = document.createElement("button");

    messagePopUp.classList.add("flash-messages");
    p.textContent = `Are you sure you want to delete "${picnicName}" picnic?`;

    confirmForm.action = deleteUrl;
    confirmForm.method = "POST";
    confirmForm.classList.add("picnic-action", "picnic-action-delete");
    confirmBtn.textContent = "Confirm";
    confirmBtn.type = "submit";
    confirmForm.appendChild(confirmBtn);

    cancelAncor.classList.add("picnic-action");
    cancelAncor.textContent = "Cancel";

    actions.classList.add("picnic-card-actions", "container");
    actions.appendChild(cancelAncor);
    actions.appendChild(confirmForm);

    messagePopUp.appendChild(p);
    messagePopUp.appendChild(actions);

    feedback.replaceChildren(messagePopUp); // to avoid adding up messages if the previous feedback message wasn't closed.

    cancelAncor.addEventListener("click", () => {
      console.log(`"${picnicName}" picnic deletion cancelled.`);
      messagePopUp.remove();
    });
  });
});
