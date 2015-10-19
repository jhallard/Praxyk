// JavaScript Document
function login(){
   $("#login_error").html("");
   $("#login_error").removeClass("alert alert-error");
	var email = $("#email").val();
	var pass = $("#password").val();
   var token = get_api_token(email,pass);
	if((token != null && token != undefined)){
		sessionStorage.setItem("login",true);
        sessionStorage.setItem("token",token);
        window.location = "dashboard.html"
	}else{
      $("#login_error").html("User Not Found!");
      $("#login_error").addClass("alert alert-error");
	}
}
