// JavaScript Document

var error_message = $("#error_message");

function evaluate_service(){
	error_message.removeClass("alert alert-error");
	error_message.html("");
   
   var token = sessionStorage.getItem("token");	
	var service = $("#pod_service").val();
	
	if(service == "false"){
		print_error("Please choose a valid service");
	}else{
		switch(service){
			case "ocr":
				get_text_from_image(token,$("#pod_input"),error_message,function(result){
					alert(JSON.stringify(result));
				});
				break;
		}
	}
}

function print_error(message){
	error_message.addClass("alert alert-error");
	error_message.html(message);
}

function dashboard_init(){
	var user_info = get_user_info(sessionStorage.getItem("token"),sessionStorage.getItem("uid"),function(data){
		if(data != null && data.code == 200){
			$("#name").text(data.user.name);
			alert(data.user.name);
		}
	});
	
}
