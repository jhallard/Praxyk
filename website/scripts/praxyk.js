//Praxyk JS Bindings
var api_output;
var base_api_url= "http://api.praxyk.com/";
var pod_api_url = base_api_url + "pod/";
var tlp_api_url = base_api_url + "tlp/";

function get_text_from_image(api_key,input,output){
   var files = input.files;
   var images = new FormData();
   api_output = output;
   
   for(int i=0;i<files.length;++i){
      images.append(files[0].name,files[0]);
   }
   
   $.ajax({
      url: pod_api_url+"ocr/",
      type: "POST",
      data: images,
      processData: false,
      contentType: false,
      crossDomain: true,
      success: api_result(data,textStatus,jqXHR),
      error: api_result(data,textStatus,jqXHR)
   });
   
}

function api_result(data,textStatus,jqXHR){
   output.html(data);
}