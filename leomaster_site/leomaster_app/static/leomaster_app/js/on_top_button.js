window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
       document.querySelector("#onTopBtn").className = 'slow-visible';
    } else {
        document.querySelector("#onTopBtn").className = 'slow-hidden';
    }
}

function topFunction() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}