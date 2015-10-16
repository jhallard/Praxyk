// JavaScript Document

var error_message = $("#error_message");

function evaluate_service(){
	error_message.removeClass("alert alert-error");
	error_message.html("");
	
	var service = $("#pod_service").val();
	
	if(service == "false"){
		print_error("Please choose a valid service");
	}else{
		switch(service){
			case "ocr":
				alert("OCR was called!");
            get_text_from_image("",$("#pod_input"),error_message);
				break;
		}
	}
}

function print_error(message){
	error_message.addClass("alert alert-error");
	error_message.html(message);
}