document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const toggleBtn = document.getElementById('sidebar-toggle');
  
    // Read from localStorage (true/false stored as string)
    let isOpen = (localStorage.getItem('sidebarOpen') === 'true');
  
    function applySidebarState(open) {
      if (open) {
        sidebar.classList.add('open');
        content.classList.add('with-sidebar');
      } else {
        sidebar.classList.remove('open');
        content.classList.remove('with-sidebar');
      }
      localStorage.setItem('sidebarOpen', open);
    }
  
    // Apply initial state
    applySidebarState(isOpen);
  
    // Clicking the toggle button flips the state
    toggleBtn.addEventListener('click', () => {
      isOpen = !isOpen;
      applySidebarState(isOpen);
    });
  });
  