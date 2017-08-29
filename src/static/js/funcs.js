$( "#CrawlingAcademic" ).click(function() {
    var file_prefix_uri = "";
    
    var file_name = $("#ListURL").val();
    var url_accepted = $("#URLAccepted").val();
    var filename = file_name.replace(/^.*\\/, "");
    console.log(file_prefix_uri.concat(filename));
    var full_path = file_prefix_uri.concat(filename);
    var requestbody = {};
    requestbody.fullpath = full_path;
    requestbody.urlpath = url_accepted;
    $.ajax({
        url: "http://localhost:5000/crawl-academic",
        data: JSON.stringify(requestbody),
        type: 'POST',
        dataType: 'json',
        crossType: true,
        contentType: 'application/json; charset=utf-8',
        success: function(data) {
            
        },
        error: function() { alert('Failed!'); },
        
    });
});
