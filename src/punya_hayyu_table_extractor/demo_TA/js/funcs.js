$( "#RuleExtractButton" ).click(function() {
    var prefix_uri = "E:\\Dropbox\\[8]\\[cin]TA\\RawData\\downloaded\\ClearHtml\\"; // TODO: ganti dengan folder yang emang disiapin buat demo
    var file_name = $("#cleanHTML").val();
    console.log(prefix_uri.concat(file_name));
    var full_path = prefix_uri.concat(file_name);
    var requestbody = {};
    requestbody.fullpath = full_path;
    $.ajax({

        url: "http://localhost:5000/rule-based",
        data: JSON.stringify(requestbody),
        type: 'POST',
        crossDomain: true,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function(data) { 
            var resultsegment = document.getElementById('ruleBasedResult');
            resultsegment.innerHTML = "";
            if (data.length == 0) {
                var notfoundtext = document.createTextNode("No table found.");
                resultsegment.appendChild(notfoundtext);
            } else {
                var resultlist = document.createElement('ul');
                for (var i = 0; i < data.length; i++) {
                    var ul = document.createElement('li');
                    var e = document.createElement('a');
                    e.href = data[i];
                    e.text = data[i];
                    ul.appendChild(e);
                    resultlist.appendChild(ul);
                }
                resultsegment.appendChild(resultlist);
            }
            
            // console.log(data[0]);
        },
        error: function() { alert('Failed!'); },
        
    });
});

$( "#GetFeaturesButton" ).click(function() {
    var prefix_uri = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\DemoData\\HTMLTable\\"; // TODO: ganti dengan folder yang emang disiapin buat demo
    var file_name = $("#HTMLtable").val();
    console.log(prefix_uri.concat(file_name));
    var full_path = prefix_uri.concat(file_name);
    var requestbody = {};
    requestbody.fullpath = full_path;
    $.ajax({

        url: "http://localhost:5000/get-features",
        data: JSON.stringify(requestbody),
        type: 'POST',
        crossDomain: true,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function(data) { 
            var resultsegment = document.getElementById('featureResult');
            resultsegment.innerHTML = "";
            var e = document.createElement('a');
            e.href = data["featuresfile"];
            e.text = data["featuresfile"];
            resultsegment.appendChild(e);
            
            console.log(data["featuresfile"]);
        },
        error: function() { alert('Failed!'); },
        
    });
});

$( "#PredictButton" ).click(function() {
    var feature_prefix_uri = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\DemoData\\FeaturesFile\\demo\\"; // TODO: ganti dengan folder yang emang disiapin buat demo
    var model_prefix_uri = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\crf_learner\\models\\"; // TODO: ganti dengan folder yang emang disiapin buat demo
    var featurefile_name = $("#featurefile").val();
    var modelfile_name = $("#modelfile").val();
    console.log(feature_prefix_uri.concat(featurefile_name));
    console.log(model_prefix_uri.concat(modelfile_name));
    var feature_full_path = feature_prefix_uri.concat(featurefile_name);
    var model_full_path = model_prefix_uri.concat(modelfile_name);
    var requestbody = {};
    requestbody.featurefile = feature_full_path;
    requestbody.modelfile = model_full_path;
    $.ajax({

        url: "http://localhost:5000/predict",
        data: JSON.stringify(requestbody),
        type: 'POST',
        crossDomain: true,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function(data) { 
            var resultsegment = document.getElementById('predictResult');
            resultsegment.innerHTML = "";
            var resultlist = document.createElement('ol');
            for (var i = 0; i < data.length; i++) {
                var label;
                if (data[i] == "T") {
                    label = "Title row";
                    console.log(label);
                } else if (data[i] = "H") {
                    label = "Header row";
                } else if (data[i] = "D") {
                    label = "Data row";
                } else if (data[i] = "G") {
                    label = "Group Header row";
                } else if (data[i] = "A") {
                    label = "Aggregate row";
                } else if (data[i] = "N") {
                    label = "Non-relational row";
                } else {
                    label = "Blank row";
                }
                var ul = document.createElement('li');
                console.log(label);
                ul.innerHTML = label;
                resultlist.appendChild(ul);
            }
            resultsegment.appendChild(resultlist);
            
            console.log(data);
        },
        error: function() { alert('Failed!'); },
        
    });
});

$( "#extractDataButton" ).click(function() {
    var html_prefix_uri = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\DemoData\\HTMLTable\\demo\\"; // TODO: ganti dengan folder yang emang disiapin buat demo
    var label_prefix_uri = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\DemoData\\LabeledFile\\"; // TODO: ganti dengan folder yang emang disiapin buat demo
    var HTMLtablefile_name = $("#HTMLtablefile").val();
    var labelfile_name = $("#labelfile").val();
    console.log(html_prefix_uri.concat(HTMLtablefile_name));
    console.log(label_prefix_uri.concat(labelfile_name));
    var html_full_path = html_prefix_uri.concat(HTMLtablefile_name);
    var label_full_path = label_prefix_uri.concat(labelfile_name);
    var requestbody = {};
    requestbody.htmlfile = html_full_path;
    requestbody.labelfile = label_full_path;
    $.ajax({

        url: "http://localhost:5000/extract-data",
        data: JSON.stringify(requestbody),
        type: 'POST',
        crossDomain: true,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function(data) { 
            var resultsegment = document.getElementById('extractDataResult');
            resultsegment.innerHTML = "";
            var e = document.createElement('a');
            e.href = html_full_path;
            e.text = html_full_path;
            resultsegment.appendChild(e);
            var resultlist = document.createElement('ol');
            for (var i = 0; i < data.length; i++) {
                var ul = document.createElement('li');
                var bpre = '<pre>';
                var epre = '</pre>';
                var ipre = JSON.stringify(data[i], null, 4);
                ul.innerHTML = bpre.concat(ipre.concat(epre));
                resultlist.appendChild(ul);
            }
            resultsegment.appendChild(resultlist);
            
            console.log(data);
        },
        error: function() { alert('Failed!'); },
        
    });
});

$( "#topoButton" ).click(function() {
    var prefix_uri = "E:\\Dropbox\\[8]\\[cin]TA\\Implementation\\data_table_extractor\\DemoData\\ExtractedData\\"; // TODO: ganti dengan folder yang emang disiapin buat demo
    
    var JSONfile_name = $("#JSONfile").val();
    console.log(prefix_uri.concat(JSONfile_name));
    var full_path = prefix_uri.concat(JSONfile_name);
    var requestbody = {};
    requestbody.jsonfile = full_path;
    $.ajax({

        url: "http://localhost:5000/detect-toponym",
        data: JSON.stringify(requestbody),
        type: 'POST',
        crossDomain: true,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function(data) { 
            var resultsegment = document.getElementById('ToponymResult');
            resultsegment.innerHTML = "";
            
            var bpre = '<pre>';
            var epre = '</pre>';
            var ipre = JSON.stringify(data, null, 4);
            
            resultsegment.innerHTML = bpre.concat(ipre.concat(epre));
            
            console.log(data);
        },
        error: function() { alert('Failed!'); },
        
    });
});
