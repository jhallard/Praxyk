// JavaScript Document
function register(){
	$("#form_error").html("");
	$("#form_error").removeClass("alert alert-error");
	
	if(validate()){
	alert("everything is fine");
	}
}

function validate(){
	var first = $("#first_name").val();
	var last = $("#last_name").val();
	var email = $("#email").val();
	var email_comp = $("#confirm_email").val();
	var password = $("#password").val();
	var password_comp = $("#confirm_password").val();
	var terms = $("#agree").prop("checked");
	
	var error = false;	
	var error_message = "<h3>Error</h3>";
	
	//Make sure that the fields arent empty
	if(first == null || first == ""){
		error_message += "<h4>First Name</h4><p>Make sure that the <strong>First Name</strong> field is filled</p>";
		error = true;
	}
	
	if(last == null || last == ""){
		error_message += "<h4>Last Name</h4><p>Make sure that the <strong>Last Name field</strong> is filled</p>";
		error = true;
	}
	
	if(email == null ||  email == ""){
		error_message += "<h4>E-Mail</h4><p>Make sure that the <strong>E-Mail</strong> field is filled</p>";
		if(email_comp == null || email_comp == "") error_message += "<p>Make sure that the <strong>Confirm E-Mail</strong> field is filled</p>";
		error = true;
	}
	
	if(email_comp == null || email_comp == "" && !(email == null ||  email == "")){
		error_message += "<h4>E-Mail</h4><p>Make sure that the <strong>Confirm E-Mail</strong> field is filled</p>";
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
	
	if(!terms){
		error_message += "<h4>Terms & Conditions</h4><p>Please agree to the <strong>Terms & Conditions</strong>!</p>";
		error =true;
	}
	
	if(error){
		post_error(error_message);
		return false;
	}
	
	//make sure that the fields match
	if(email != email_comp){
		error_message += "<h4>E-Mail</h4><p>Make sure that the <strong>E-Mails</strong> match!</p>";
		error = true;
	}
	var reg = /[a-z0-9!#$%&'*+=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/;
	if(!reg.test(email)){
		error_message += "<h4>E-Mail</h4><p>Make sure that the <strong>E-Mails</strong> are valid!</p>";
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