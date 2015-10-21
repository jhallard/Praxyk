// JavaScript Document
	var first;
	var last;
	var email;
	var password;
	var password_comp;
	var terms;

function register_result(result) {
      if(result) {
        $("#form_error").html("Registration Successful! Check your email to confirm your account!");
        $("#form_error").addClass("alert alert-success");
        $("#first_name").val("");
		$("#last_name").val("");
		$("#email").val("");
		$("#password").val("");
		$("#confirm_password").val("");
		$("#agree").prop("checked") = false;
         return true
      }else{
         $("#form_error").html("Registration Not Successful! Please try again!");
         $("#form_error").addClass("alert alert-error");
         $("#agree").prop("checked") = false;
         return false
      }
}

function register(){
	$("#form_error").html("");
	$("#form_error").removeClass("alert alert-error");
	$("#form_error").removeClass("alert alert-success");
   
    first = $("#first_name").val();
	last = $("#last_name").val();
	email = $("#email").val();
	password = $("#password").val();
	password_comp = $("#confirm_password").val();
	terms = $("#agree").prop("checked");
	
	if(validate()){
        register_user(first, last, email, password, register_result);
	}
}

function validate(){
	
	var error = false;	
	var error_message = "<h3>Error</h3>";
	
	//Make sure that the fields arent empty
	if(first == null || first == ""){
		error_message += "<h4>First Name</h4><p>Make sure that the <strong>First Name</strong> field is filled</p>";
		error = true;
	}
	
	if(last == null || last == ""){
		error_message += "<h4>Last Name</h4><p>Make sure that the <strong>Last Name</strong> field is filled</p>";
		error = true;
	}
	
	if(email == null ||  email == ""){
		error_message += "<h4>E-Mail</h4><p>Make sure that the <strong>E-Mail</strong> field is filled</p>";
		error = true;
	}
	
	if(password == null ||  password == ""){
		error_message += "<h4>Password</h4><p>Make sure that the <strong>Password</strong> field is filled</p>";
		if(password_comp == null || password_comp == "") error_message += "<p>Make sure that the <strong>Confirm Password</strong> field is filled</p>";
		error = true;
	}
	
	if(password_comp == null || password_comp == "" && !(password == null ||  password == "")){
		error_message += "<h4>Password</h4><p>Make sure that the <strong>Confirm Password</strong> field is filled</p>";
		error = true;
	}
   
   if(password.length < 5){
      error_message += "<h4>Password</h4><p>Make sure your <strong>Password</strong> contains atleast 6 characters!</p>";
		error = true;
	}
	
	if(!terms){
		error_message += "<h4>Terms of Service</h4><p>Please agree to the <strong>Terms of Service</strong>!</p>";
		error =true;
	}
	
	if(error){
		post_error(error_message);
		return false;
	}
	
	//make sure that the fields match
	var reg = /[a-z0-9!#$%&'*+=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/;
	if(!reg.test(email)){
		error_message += "<h4>E-Mail</h4><p>Make sure that the <strong>E-Mail</strong> is valid!</p>";
		error = true;
	}
	
	if(password_comp != password) {
		error_message += "<h4>Password</h4><p>Make sure that the <strong>Passwords</string> match!</p>";
		error = true;
	}
	
	if(error){
		post_error(error_message);
		return false;
	}
	
	return true;
}

function post_error(message){
	$("#form_error").html(message);
	$("#form_error").addClass("alert alert-error");
}
