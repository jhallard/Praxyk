//Praxyk JS Binding

//api urls
var base_api_url= "http://api.praxyk.com:5000/";
var pod_api_url = base_api_url + "pod/";
var tlp_api_url = base_api_url + "tlp/";
var token_api_url = base_api_url + "tokens/";
var user_api_url = base_api_url + "users/";
var transaction_api_url = base_api_url + "transactions/";
var results_api_url = base_api_url + "results/";

function get_text_from_image(token,input,callback){
	 
	//get the data ready
	var ocr_data = new FormData();
	for(var i=0;i<input.length;++i){
		var file = input[i];
		ocr_data.append("files",file,file.name);
	}
	
	
	//call api
	var result = api_call(pod_api_url+"ocr/?token="+token,"POST",ocr_data,null, function(result) {
		callback(result)
    });
	
	
}

function get_api_token(username,password, callback){
   
   //get data ready
	var login_data = new Object();
	login_data.email = username;
	login_data.password = password;
	
	var json_data = JSON.stringify(login_data);

	//api call
	return api_call(token_api_url,"POST",json_data,"application/json", function(result) { 
        var login_json = $.parseJSON(result);
        if(login_json.code == 200) { 
            return callback(login_json);
        }
        else {
            return callback(null);
        }
    });
}

function register_user(first,last,email,password, callback){
   
   //get data ready
   var register_data = new Object();
   register_data.email = email;
   register_data.password = password;
   register_data.name = first + " " +last;
   
   var json_data = JSON.stringify(register_data);

   
   //api call
   return api_call(user_api_url,"POST",json_data,"application/json", function(result) {
       var json = $.parseJSON(result);
       
       if(json.code == 200) { return callback(true) }
       else { return callback(false) };
   });

}

function get_user_info(token,userid,callback){	
	//api call
	var url = user_api_url+userid.toString()+"?token="+token;
	return api_call(url,"GET",null,null, function(result) {
		var json = $.parseJSON(result);
       return callback(json);
   });
}

function get_recent_transactions(token,userid,callback){
	var url = transaction_api_url + "?user_id=" + userid.toString() + "&token=" + token;
	return api_call(url, "GET",null,null,function(result) {
		var json = $.parseJSON(result);
		return callback(json);
	});
}

function get_transaction_result(token,trans_id,user_id,callback){
}

function api_call(url,method,payload,content_type, callback){
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function (){
		if(xhr.readyState==4 && xhr.status==200){
            callback(xhr.responseText);
		} 
	}
	xhr.open(method,url,true);
	if(payload!=null){
		if(content_type!=null) xhr.setRequestHeader('Content-Type',content_type);
		xhr.send(payload);
	}else{
		xhr.send();
	}
}

