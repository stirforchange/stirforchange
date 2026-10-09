// Mobile nav toggle
var hamburger = document.getElementById('hamburger');
var navLinks  = document.getElementById('navLinks');
if(hamburger && navLinks){
  hamburger.addEventListener('click', function(){
    navLinks.classList.toggle('open');
  });
  document.addEventListener('click', function(e){
    if(!hamburger.contains(e.target) && !navLinks.contains(e.target)){
      navLinks.classList.remove('open');
    }
  });
}

// Active nav link highlight
var path = window.location.pathname;
document.querySelectorAll('.nav-links a').forEach(function(a){
  var href = a.getAttribute('href');
  if(href === path || (href !== '/' && path.startsWith(href))){
    a.classList.add('active');
  }
});
