function selectAll(elt){
    $(elt).parent().find("[type=checkbox]").prop("checked", true);
}
function unselectAll(elt){
    $(elt).parent().find("[type=checkbox]").prop("checked", false);
}

function toggleAllBaseItemsCategory(elt){
    if(!$(elt).prop("checked")){
        unselectAll(elt);
    }
    else{
        selectAll(elt)
    }
}

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
            alert("Select at least one .bic file");
            return false;
        }

    })

    $("[type=checkbox]").change(function(){
        console.log("change")
        var id = $(this).attr("id");
        console.log($(this).prop("checked"))
        localStorage.setItem(id, $(this).prop("checked").toString()); 
    })

    $("[type=checkbox]").each(function(){
        var id = $(this).attr("id");
        var state = localStorage.getItem(id);
        if(null != state && undefined != state && "" != state){
            console.log(state)
            $(this).prop("checked", state == 'true')
        }
    })    

})