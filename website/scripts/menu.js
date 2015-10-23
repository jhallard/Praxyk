// JavaScript Document
function menu_init() {
//set the menu
var menu = '<div class="navbar">'
menu += '<button type="button" class="btn btn-navbar-highlight btn-large btn-primary" data-toggle="collapse" data-target=".nav-collapse">Menu<span class="icon-chevron-down icon-white"></span></button>';
menu += '<div class="nav-collapse collapse"><ul class="nav nav-pills ddmenu">';
menu += '<li id="Home"><a href="index.html">Home</a></li>';
menu += '<li id="Documentation"><a href="documentation.html">Documentation</a></li>';
if(sessionStorage.getItem("login")){
			menu += '<li id="Dashboard"><a href="dashboard.html">Dashboard</a></li>';
			menu += '<li id="Logout"><a href="#" id="logout">Logout</a></li>';
}else{
	menu += '<li id="Login"><a href="login.html">Login</a></li>';
	menu += '<li id="Register"><a href="register.html">Register</a></li>';
}
menu += '</ul></div></div>';

$("#divMenuRight").html(menu);

//set the active page
var page_title = $("#page_title").text();
var page_id = "#"+page_title;
$(page_id).addClass("active");

$("#logout").click(function() {
	sessionStorage.clear();
	if(page_title == "Dashboard") window.location = "index.html";
	else menu_init();
	return false;
});

}

function logout(){
	
	return true;
}