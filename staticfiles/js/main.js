document.addEventListener('DOMContentLoaded', function(){
  const menuBtn = document.querySelector('.menu-btn');
  const sidebar = document.querySelector('.sidebar');
  if(menuBtn && sidebar){
    menuBtn.addEventListener('click', function(){
      sidebar.classList.toggle('open');
    });
  }

  // Simple placeholder: close sidebar on content click for small screens
  const content = document.querySelector('.content');
  if(content && sidebar){
    content.addEventListener('click', function(){
      if(window.innerWidth < 1100){
        sidebar.classList.remove('open');
      }
    });
  }
});
