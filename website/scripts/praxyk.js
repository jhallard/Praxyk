//Praxyk JS Binding

//api urls
var base_api_url= "http://api.praxyk.com/v1/";
var pod_api_url = base_api_url + "pod/";
var tlp_api_url = base_api_url + "tlp/";
var token_api_url = base_api_url + "tokens/";
var user_api_url = base_api_url + "users/";
var transaction_api_url = base_api_url + "transactions/";
var results_api_url = base_api_url + "results/";

function get_text_from_image(token,input,progress,callback){
	 
	//get the data ready
	var ocr_data = new FormData();
	for(var i=0;i<input.length;++i){
		var file = input[i];
		ocr_data.append("files",file,file.name);
	}
	
	
	//call api
	var result = api_call(pod_api_url+"ocr/?token="+token,"POST",ocr_data,null,progress,function(result) {
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
	return api_call(token_api_url,"POST",json_data,"application/json",null,function(result) { 
        var login_json = $.parseJSON(result);
        if(login_json.code == 200) { 
            return callback(login_json);
        }
        else {
            return callback(null);
        }
    });
}

function register_user(first,last,email,password,callback){
   
   //get data ready
   var register_data = new Object();
   register_data.email = email;
   register_data.password = password;
   register_data.name = first + " " +last;
   
   var json_data = JSON.stringify(register_data);

   
   //api call
   return api_call(user_api_url,"POST",json_data,"application/json",null,function(result) {
       var json = $.parseJSON(result);
       
       if(json.code == 200) { return callback(true) }
       else { return callback(false) };
   });

}

function get_user_info(token,userid,callback){	
	//api call
	var url = user_api_url+userid.toString()+"?token="+token;
	return api_call(url,"GET",null,null,null,function(result) {
		var json = $.parseJSON(result);
       return callback(json);
   });
}

function get_all_transactions(token,userid,callback){
	var url = transaction_api_url + "?user_id=" + userid.toString() + "&pagination=False&token=" + token;
	return api_call(url, "GET",null,null,null,function(result) {
		var json = $.parseJSON(result);
		return callback(json);
	});
}

function get_all_transaction_results(token,trans_id,callback){
   var url = results_api_url + trans_id.toString() + "?pagination=False&token=" + token;
   return api_call(url,"GET",null,null,null,function(result){
      var json = $.parseJSON(result);
      return callback(json);
   });
}

function api_call(url,method,payload,content_type,prog,callback){
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function (){
		if(xhr.readyState==4 && xhr.status==200){
            callback(xhr.responseText);
		} 
	}
   if(prog != null){
   xhr.upload.onprogress = function(e) {
        var percentComplete = (e.loaded / e.total) * 100;
        prog.html(percentComplete.toString());
    };

    xhr.onload = function() {
        if (xhr.status == 200) {
            prog.html("Sucess! Upload completed");
        } else {
            prog.html("Error! Upload failed");
        }
    };
   }
	xhr.open(method,url,true);
	if(payload!=null){
		if(content_type!=null) xhr.setRequestHeader('Content-Type',content_type);
		xhr.send(payload);
	}else{
		xhr.send();
	}
}

