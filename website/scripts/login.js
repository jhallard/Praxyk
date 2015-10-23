// JavaScript Document
function login(){
   $("#login_error").html("");
   $("#login_error").removeClass("alert alert-error");
	var email = $("#email").val();
	var pass = $("#password").val();
    var token = get_api_token(email,pass, function(data) {
        if((data != null && data != undefined)){
            sessionStorage.setItem("login",true);
            sessionStorage.setItem("token",data.token);
            sessionStorage.setItem("uid",data.user.user_id);
            window.location = "dashboard.html"
        }else{
          $("#login_error").html("User Not Found!");
          $("#login_error").addClass("alert alert-error");
        }
        return token
    });
}
