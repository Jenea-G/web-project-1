console.log("script loaded");
const tabs = document.querySelectorAll(".join-tab");
const forms = document.querySelectorAll(".join-form");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
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
