//Praxyk JS Bindings
var api_output;
var base_api_url= "http://api.praxyk.com/";
var pod_api_url = base_api_url + "pod/";
var tlp_api_url = base_api_url + "tlp/";
var token_api_url = base_api_url + "tokens/";
var user_api_url = base_api_url + "users/";

function get_text_from_image(token,input,output){
   var files = input.files;
   var ocr_data = new FormData();
   api_output = output;
   
   for(var i=0;i<files.length;++i){
      ocr_data.append(files[i].name,files[i]);
   }
   
   ocr_data.append("token",token);
   
   $.ajax({
      url: pod_api_url+"ocr/",
      type: "POST",
      data: images,
      processData: false,
      contentType: false,
      success: api_result(data,textStatus,jqXHR),
      error: api_result(data,textStatus,jqXHR)
   });
   
}

function get_api_token(username,password){
   var token;
   
   var login_data = new FormData();
   login_data.append("username",username);
   login_data.append("password",password);
   
   $.ajax({
      url: token_api_url,
      type: "POST",
      data: login_data,
      processData: false,
      contentType: false,
      success: function(data,textStatus,jqXHR){
         var json = $.parseJSON(data);
         if(json.code == 200) token = json.token;
         else token = null;
      },
      error:function(data,textStatus,jqXHR){
         token = null;
      }
   });
   
   return token;
}

function register_user(first,last,email,password){
   var register_status;
   
   var register_data = new FormData();
   register_data.append("email",email);
   register_data.append("password",password);
   register_data.append("first_name",first);
   register_data.append("last_name",last);
   
   $.ajax({
      url: user_api_url,
      type: "POST",
      data: register_data,
      processData: false,
      contentType: false,
      success: function(data,textStatus,jqXHR){
         var json = $.parseJSON(data);
         if(json.code == 200) register_status = true;
         else register_status = false;
      },
      error:function(data,textStatus,jqXHR){
         register_status = false;
      }
   });
   
   return register_status;
}

function api_result(data,textStatus,jqXHR){
   output.html(data);
}