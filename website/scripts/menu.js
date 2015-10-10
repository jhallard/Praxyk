// JavaScript Document
function menu_init() {
//set the menu
var menu = '<div class="navbar">'
menu += '<button type="button" class="btn btn-navbar-highlight btn-large btn-primary" data-toggle="collapse" data-target=".nav-collapse">NAVIGATIO<span class="icon-chevron-down icon-white"></span></button>';
menu += '<div class="nav-collapse collapse"><ul class="nav nav-pills ddmenu">';
menu += '<li id="Home"><a href="index.html">Home</a></li>';
menu += '<li id="Documentation"><a href="documentation.html">Documentation</a></li>';
menu += '<li id="Login"><a href="login.html">Login</a></li>';
menu += '<li id="Register"><a href="register.html">Register</a></li>';
menu += '</ul></div></div>';

$("#divMenuRight").html(menu);

//set the active page
var page_title = $("#page_title").text();
var page_id = "#"+page_title;
$(page_id).addClass("active");

}

window.onload = menu_init;