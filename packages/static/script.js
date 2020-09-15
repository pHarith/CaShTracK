
var body = document.getElementById('body');
var body_form = document.getElementById('body-form');
var body_main = document.getElementById('body-main');

function toogleSidebar() {
    // sidebar-expand sidebar and its content
    document.getElementById("Sidebar").classList.replace('sidebar-shrink', 'sidebar-expand');
    document.querySelectorAll("#Sidebar > header > div, .text, #closeSidebar").forEach(function(element)
        {element.style.display = "inline-block";});
    /* Here I am making the sidebar visible by sidebar-expanding its width, changing its z-index,
    and display the logo and text, while also changing the padding
    */

    document.querySelectorAll("#Sidebar > div > a").forEach(function(element){
        element.classList.add('rows')
    })
    document.querySelectorAll("#Sidebar > div > a > .material-icons").forEach(function(element){
        element.classList.add('icons-active')
    })
    document.querySelectorAll("#Sidebar > div > a > .text").forEach(function(element){
        element.classList.add('text-active')
    })
    // Remove flashed message if it's still there
    document.getElementById("flashMessage").style.display = "none";

    // Push navBar contents
    document.getElementById("navBar").style.marginLeft = "250px";
    document.getElementById("navBar").style.opacity = "0.5";
    document.getElementById("navBar").style.zIndex = "-1";
    document.getElementById("sitelogo").style.display = "none";
    
    // Push elements with id body
    if (body) {body.classList.add("inactive");}

    else if (body_form) {body_form.classList.add("inactive-form");}

    else if (body_main){ body_main.classList.add('inactive-table');};
    
    // Darken background color
    document.body.style.backgroundColor = "rgba(0,0,0,0.5)";
    document.getElementById("footer").style.display = "none";
}

function closeSidebar(){
    // Shrink sidebar and its contents
    document.getElementById("Sidebar").classList.replace('sidebar-expand', 'sidebar-shrink');
    document.querySelectorAll("#Sidebar > header > div, .text, #closeSidebar").forEach(function(element)
        {element.style.display = "none";});
    
    document.querySelectorAll("#Sidebar > div > a > div").forEach(function(element){
        element.classList.remove('rows');
    });
    document.querySelectorAll("#Sidebar > div > a > .material-icons").forEach(function(element){
        element.classList.remove('icons-active')
    });
    document.querySelectorAll("#Sidebar > div > a > .text").forEach(function(element){
        element.classList.remove('text-active')
    });
    // Bring back navbar to position
    document.getElementById("navBar").style.marginLeft = "0";
    document.getElementById("navBar").style.opacity = "1";
    document.getElementById("navBar").style.zIndex = "2";

    // Push body back to normal position
    if (body) {body.classList.remove("inactive");}

    else if (body_form) {body_form.classList.remove("inactive-form");}

    else if (body_main){ body_main.classList.remove('inactive-table');};

    // Lighten background to normal and show the page normally
    document.getElementById("sitelogo").style.display = "block";
    document.body.style.backgroundColor = localStorage.getItem('colour');   
    document.getElementById('footer').style.display = "block";
}

// jQuery script to automate alert closing
$(document).ready(function() {
    // show the alert
    setTimeout(function() {
        $(".alert").alert('close');
    }, 3000);
});

let expired = document.getElementById('expired');
let btn = document.getElementById('budgetbtn');

function showExpired(){  
    if (expired.classList.contains('show')) {
        expired.classList.replace('show', 'hide');
        btn.innerHTML = 'Show Expired Budgets';
    }
    else{
        expired.classList.replace('hide', 'show');
        btn.innerHTML = 'Hide Expired Budgets';
    }
}

function toogleDark(){
    if (localStorage.getItem('colour') === 'white'){
        localStorage.setItem('colour', "rgba(50,50,50,1)");
        localStorage.setItem('table-class', 'table-dark');
        localStorage.setItem('text-colour', "rgb(240,240,240)");
        localStorage.setItem('button', 'Toogle Light Mode');
        localStorage.setItem('list-bg', 'list-group-item-secondary');
    }
    else{
        localStorage.setItem('colour', "white");
        localStorage.setItem('text-colour', "black");
        localStorage.setItem('table-class', 'table-light');
        localStorage.setItem('button', 'Toogle Dark Mode');
        localStorage.setItem('list-bg', '');
    }
    setdarkmode();
}

function setdarkmode(){
    if (localStorage.getItem('colour')){
        $('.list-group-item-action').each(function(){
            if ($(this).hasClass('list-group-item-dark')){
                $(this).removeClass('list-group-item-dark');}
            $(this).addClass(localStorage.getItem('list-bg'));
        });
        document.body.style.backgroundColor = localStorage.getItem('colour');
        document.body.style.color = localStorage.getItem('text-colour');
        $('.table').each(function(){
            if ($(this).hasClass('table-light')){ 
                $(this).removeClass('table-light');
            };

            if ($(this).hasClass('table-dark')){ 
                $(this).removeClass('table-dark');};
            $(this).addClass(localStorage.getItem('table-class'));
        });

        $('.modal-text').each(function(){
            $(this).css('color', localStorage.getItem('text-colour'));
        }) ;

        $('.modal-content').css('background-color', localStorage.getItem('colour'));

        $('.content-side, .content-section, .content-settings').each(function(){
            $(this).css('background-color', localStorage.getItem('colour'));
        })
        
        document.querySelector('#dark-mode').innerHTML = localStorage.getItem('button')
    }
}

setdarkmode();

$(window).bind('resize', function(){
    if ($(this).height()<400){
        $('.dropdown-account').css('display', 'none')
        $('.dropdown-divider').css('display', 'none')
        $('.dropdown-currency').css('display', 'none')
    }
    else{
        $('.dropdown-account').css('display', 'block')
        $('.dropdown-divider').css('display', 'block')
        $('.dropdown-currency').css('display', 'block')
    }
})
