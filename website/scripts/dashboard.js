// JavaScript Document

function evaluate_service(){
	$("#error_message").removeClass("alert alert-error");
	$("#error_message").html("");
   
	var token = sessionStorage.getItem("token");	
	var service = $("#pod_service").val();
	
	if(service == "false"){
		print_error("Please choose a valid service");
	}else{
		switch(service){
			case "ocr":
				var files = $("#pod_input").prop("files");
				get_text_from_image(token,files,$("#upload_progress"),function(result){
					get_trans();
				});
				break;
		}
	}
}

function print_error(message){
	$("#error_message").addClass("alert alert-error");
	$("#error_message").html(message);
}

function get_results(trans_id){
   get_all_transaction_results(sessionStorage.getItem("token"),trans_id,function(result){
      var results = result.results;
      var output = "Image Name: Predictive String\n";
      for(var i=0;i<results.length;++i){
         var line = results[i].item_name + ": " + results[i].prediction.result_string;
         output += line + "\n";
      }
      alert(output);
   });
}

function get_trans(){
		var user_transactions = get_all_transactions(sessionStorage.getItem("token"),sessionStorage.getItem("uid"),function(data){
		var table = "<table><tr><th>ID</th><th>Status</th><th>Created At</th><th>Upload Success</th><th>Upload Fail</th><th>Upload Total</th><th>Size (KB)</th><th>View Results</th></tr>";//"</table>";
		var trans = data.transactions;
      if(typeof trans != "undefined"){
         for(var i=0;i<trans.length;++i){
            var id = "<td>"+trans[i].trans_id.toString()+"</td>";
            var status = "<td>"+trans[i].status+"</td>";
            var created = "<td>"+trans[i].created_at+"</td>";
            var success = "<td><center>"+trans[i].uploads_success+"</center></td>";
            var failed = "<td><center>"+trans[i].uploads_failed+"</center></td>";
            var total = "<td><center>"+trans[i].uploads_total+"</center></td>";
            var size= "<td><center>"+trans[i].size_total_KB+"</center></td>";
            var result = "<td><button onclick=\'get_results(\""+trans[i].trans_id.toString()+"\")' class='btn'>Get Results</button></td>";
            var row = "<tr>"+id+status+created+success+failed+total+size+result+"</tr>";
            table += row;
         }
         table += "</table>";
         $("#transactions").html(table);}
      else{$("#transactions").html("<h5>There are no transactions!</h5>");}
	});
}
	

function dashboard_init(){
	var user_info = get_user_info(sessionStorage.getItem("token"),sessionStorage.getItem("uid"),function(data){
		if(data != null){
			$("#name").text(data.user.name);
		}
	});
	
	get_trans();
	

	
}
