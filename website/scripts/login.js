// JavaScript Document
function login(){
	var email = $("#email").val();
	var pass = $("#password").val();
	if(get_access(email,pass)){
		sessionStorage.setItem("login",true);
		sessionStorage.setItem("email",email);
		sessionStorage.setItem("password",pass);
	}else{
		alert("User not found!");
	}
	window.location = "dashboard.html"
}

function get_access(email,pass){
	if(email == "test" && pass == "test"){
		return true;
	}
	return false;
}