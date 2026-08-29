console.log("script loaded");
const joinTabs = document.querySelectorAll(".join-tab");
const picnicTabs = document.querySelectorAll(".picnic-tab");
const closeBtn = document.getElementById("close-btn");
const deletePicnicBtns = document.querySelectorAll(".delete-picnic-btn");
const copyBtns = document.querySelectorAll(".copy-btn");

/** 'First Time Joinging' and 'Returning' Tab selection for guests */
joinTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const forms = document.querySelectorAll(".join-form");
    const formType = tab.dataset.tab;

    joinTabs.forEach((tab) => {
      tab.classList.remove("active");
    });

    forms.forEach((form) => {
      form.classList.remove("active");
    });

    tab.classList.add("active");
    document.getElementById(formType).classList.add("active");
  });
});

/** 'Details' and 'Participants' Tab selection for picnic page */
picnicTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const picnicTabsContent = document.querySelectorAll(".picnic-tab-content");
    const picnicTabType = tab.dataset.tab;

    picnicTabs.forEach((tab) => {
      tab.classList.remove("active");
    });

    picnicTabsContent.forEach((tabContent) => {
      tabContent.classList.remove("active");
    });

    tab.classList.add("active");
    document.getElementById(picnicTabType).classList.add("active");
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

    const messagePopUp = createFlashMessage(
      `Are you sure you want to delete "${picnicName}" picnic?`,
    );
    const actions = document.createElement("div");
    const cancelAncor = document.createElement("a");
    const confirmForm = document.createElement("form");
    const confirmBtn = document.createElement("button");

    confirmForm.action = deleteUrl;
    confirmForm.method = "POST";
    confirmForm.classList.add("picnic-action", "picnic-confirm-delete");
    confirmBtn.textContent = "Confirm";
    confirmBtn.type = "submit";
    confirmForm.appendChild(confirmBtn);

    cancelAncor.classList.add("picnic-action");
    cancelAncor.textContent = "Cancel";

    actions.classList.add("picnic-card-actions", "container");
    actions.appendChild(cancelAncor);
    actions.appendChild(confirmForm);

    messagePopUp.appendChild(actions);

    feedback.replaceChildren(messagePopUp); // to avoid adding up messages if the previous feedback message wasn't closed.

    cancelAncor.addEventListener("click", () => {
      console.log(`"${picnicName}" picnic deletion cancelled.`);
      messagePopUp.remove();
    });
  });
});

/** Create feedback messages helper function with optional category for "error" */
function createFlashMessage(message, category = "") {
  const messagePopUp = document.createElement("div");
  const p = document.createElement("p");

  messagePopUp.classList.add("flash-messages");
  if (category) {
    p.classList.add(category);
  }
  p.textContent = message;

  messagePopUp.appendChild(p);

  return messagePopUp;
}

/** Copy to clipboard operation */
function updateClipboard(content, label) {
  const feedback = document.querySelector(".feedback");

  navigator.clipboard.writeText(content).then(
    () => {
      const message = createFlashMessage(`${label} copied to clipboard.`);

      feedback.replaceChildren(message);
      setTimeout(() => {
        message.remove();
      }, 2000);
    },
    () => {
      const message = createFlashMessage(
        `Failed to copy ${label.toLowerCase()}.`,
        "error",
      );

      feedback.replaceChildren(message);
      setTimeout(() => {
        message.remove();
      }, 2000);
    },
  );
}

/** Triggering updateClipboard function to copy content */
copyBtns.forEach((copyBtn) => {
  copyBtn.addEventListener("click", () => {
    const content = copyBtn.dataset.content;
    const label = copyBtn.dataset.label;
    console.log(`data to copy: ${content}`);
    updateClipboard(content, label);
  });
});

/** Insert illustrations source for each item category */
function setCategoryIllustrations() {
  const illustrations = document.querySelectorAll(".category-img");

  illustrations.forEach((illustration) => {
    const category = illustration.dataset.category.toLowerCase();
    illustration.src = `/static/images/category_icons/${category}.svg`;
  });
}

setCategoryIllustrations();
