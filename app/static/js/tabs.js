document.addEventListener('DOMContentLoaded', function () {
    const tabTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="pill"]'));
    const tabList = tabTriggerList.map(tabTriggerEl => new bootstrap.Tab(tabTriggerEl));

    tabTriggerList.forEach(tabTriggerEl => {
      tabTriggerEl.addEventListener('click', function (event) {
        event.preventDefault();
        const tab = bootstrap.Tab.getInstance(event.currentTarget);
        tab.show();
      });
    });
  });
