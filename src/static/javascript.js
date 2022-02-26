
$(function(){

    //init state
    $("#filterItemsByType").hide();

    $("#toggleFilterItemsByType").click(function(){        
        $("#filterItemsByType").toggle();

        var isVisible = $("#filterItemsByType").is(":visible");
        if(isVisible){
            $(this).text("CLOSE")
        }
        else{
            $(this).text("OPEN")
        }        
    });


    $("#exportToCsv").submit(function(){

        if ($('#pcfiles')[0].files.length === 0) {
            alert("Select at least a .bic file");
            return false;
        }


    })
})