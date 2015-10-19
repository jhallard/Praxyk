//Praxyk JS Binding

//api urls
var base_api_url= "http://api.praxyk.com:5000/";
var pod_api_url = base_api_url + "pod/";
var tlp_api_url = base_api_url + "tlp/";
var token_api_url = base_api_url + "tokens/";
var user_api_url = base_api_url + "users/";

function get_text_from_image(token,input,output){
	
   var files = input.files;
   
   for(var i=0;i<files.length;++i){
	 
	//get the data ready
	var ocr_data = new Object();
	ocr_data.append("token",token);
	ocr_data.append("image",files[0]);
	
	//call api
	var result = api_call(pod_api_url+"ocr/","POST",ocr_data,"multipart/form-data");
	alert(result);
	
	
   }
   
}

function get_api_token(username,password){
   
   //get data ready
	var login_data = new Object();
	login_data.email = username;
	login_data.password = password;
	
	var json_data = JSON.stringify(login_data);

	//api call
	var result = api_call(token_api_url,"POST",json_data,"application/json");

	var login_json = $.parseJSON(result);
	if(json.code == 200) return json.token;
	else return null;
}

function register_user(first,last,email,password){
   
   //get data ready
   var register_data = new Object();
   register_data.email = email;
   register_data.password = password;
   register_data.name = first + " " +last;
   
   var json_data = JSON.stringify(register_data);
   
   //api call
   var result = api_call(user_api_url,"POST",json_data,"application/json");
   
   var json = $.parseJSON(result);
   
   if(json.code == 200) return true;
   else return false;
}

function api_call(url,method,payload,content_type){
	alert(payload);
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function (){
		if(xhr.readyState==4 &&xhr.status==200){
			return xhr.responseText;
		} 
	}
	xhr.open(method,url,true);
	xhr.setRequestHeader('Content-Type',content_type);
	xhr.send(payload);
}

