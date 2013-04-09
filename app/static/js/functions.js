
function metricz(){
                   window.location.href = "http://127.0.0.1:5000/metrics";
                   $.get("http://127.0.0.1:5000/metrics")
                   .done(function() { metricz })
                   .fail(function() { metricz }); 
                   };




       
